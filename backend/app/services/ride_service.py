from sqlalchemy.orm import Session

from app.models.cab import Cab, CabStatus
from app.models.passenger import Passenger, PassengerStatus
from app.models.ride import Ride, RideStatus
from app.models.ride_passenger import RidePassenger
from app.repositories.ride_repository import RideRepository


class RideService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RideRepository(db)

    def get_ride(self, ride_id: int) -> Ride | None:
        return self.repo.get(ride_id)

    def cancel_ride(self, ride_id: int) -> Ride | None:
        ride = self.repo.get(ride_id)
        if not ride:
            return None

        ride.status = RideStatus.cancelled
        passengers = (
            self.db.query(Passenger)
            .join(RidePassenger, RidePassenger.passenger_id == Passenger.id)
            .filter(RidePassenger.ride_id == ride.id)
            .all()
        )
        for passenger in passengers:
            passenger.status = PassengerStatus.cancelled

        cab = self.db.get(Cab, ride.cab_id)
        if cab:
            cab.status = CabStatus.available

        self.db.commit()
        self.db.refresh(ride)
        return ride
