from dataclasses import dataclass

from redis.lock import Lock
from sqlalchemy.orm import Session

from app.algorithms.pooling import PoolingAlgorithm
from app.core.config import settings
from app.core.redis_client import redis_client
from app.models.cab import Cab, CabStatus
from app.models.passenger import Passenger, PassengerStatus
from app.models.ride import Ride, RideStatus
from app.models.ride_passenger import RidePassenger
from app.repositories.cab_repository import CabRepository
from app.repositories.passenger_repository import PassengerRepository
from app.repositories.ride_repository import RideRepository
from app.services.pricing_service import PricingService


@dataclass
class PoolResult:
    ride_id: int | None
    matched_passengers: int
    message: str


class PoolingService:
    def __init__(self, db: Session):
        self.db = db
        self.passenger_repo = PassengerRepository(db)
        self.cab_repo = CabRepository(db)
        self.ride_repo = RideRepository(db)
        self.pricing = PricingService(settings.rate_per_km)

    def run_pooling(self) -> PoolResult:
        lock: Lock = redis_client.lock("pooling_assignment_lock", timeout=5, blocking_timeout=1)
        if not lock.acquire(blocking=True):
            return PoolResult(ride_id=None, matched_passengers=0, message="Pooling already in progress")

        try:
            waiting = self.passenger_repo.waiting()
            if not waiting:
                return PoolResult(ride_id=None, matched_passengers=0, message="No waiting passengers")

            available_cabs = self.cab_repo.find_available_with_lock()
            if not available_cabs:
                return PoolResult(ride_id=None, matched_passengers=0, message="No available cabs")

            selected_ride = self._build_best_pool(waiting, available_cabs)
            if not selected_ride:
                return PoolResult(ride_id=None, matched_passengers=0, message="No feasible pool found")

            self.db.commit()
            return selected_ride
        finally:
            if lock.owned():
                lock.release()

    def _build_best_pool(self, waiting: list[Passenger], cabs: list[Cab]) -> PoolResult | None:
        anchor = waiting[0]
        nearby = [anchor]
        for p in waiting[1:]:
            d = PoolingAlgorithm.haversine_distance_km(anchor.pickup_lat, anchor.pickup_lng, p.pickup_lat, p.pickup_lng)
            if d <= settings.nearby_distance_km:
                nearby.append(p)

        for cab in cabs:
            selected: list[Passenger] = []
            total_luggage = 0
            for p in nearby:
                if len(selected) >= cab.seat_capacity:
                    break
                proposed_luggage = total_luggage + p.luggage_count
                if proposed_luggage > cab.luggage_capacity:
                    continue
                if not self._detour_ok(anchor, selected + [p]):
                    continue
                selected.append(p)
                total_luggage = proposed_luggage

            if selected:
                distance = PoolingAlgorithm.route_distance(
                    [(p.pickup_lat, p.pickup_lng) for p in selected]
                    + [(p.drop_lat, p.drop_lng) for p in selected]
                )
                price = self.pricing.calculate(distance, len(selected), cab.seat_capacity)
                ride = self.ride_repo.create(Ride(cab_id=cab.id, status=RideStatus.active, total_price=price))

                for idx, p in enumerate(selected, start=1):
                    p.status = PassengerStatus.assigned
                    self.db.add(
                        RidePassenger(
                            ride_id=ride.id,
                            passenger_id=p.id,
                            pickup_order=idx,
                            drop_order=idx,
                        )
                    )
                cab.status = CabStatus.full if len(selected) >= cab.seat_capacity else CabStatus.available
                return PoolResult(ride_id=ride.id, matched_passengers=len(selected), message="Ride pooled successfully")
        return None

    def _detour_ok(self, anchor: Passenger, passengers: list[Passenger]) -> bool:
        direct = PoolingAlgorithm.haversine_distance_km(
            anchor.pickup_lat, anchor.pickup_lng, anchor.drop_lat, anchor.drop_lng
        )
        pooled_route = PoolingAlgorithm.route_distance(
            [(p.pickup_lat, p.pickup_lng) for p in passengers]
            + [(p.drop_lat, p.drop_lng) for p in passengers]
        )
        max_allowed = direct * (1 + anchor.detour_tolerance)
        return pooled_route <= max_allowed if direct > 0 else True
