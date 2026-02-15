from app.models.cab import Cab
from app.models.passenger import Passenger
from app.services import pooling_service
from app.services.pooling_service import PoolingService


class DummyLock:
    def acquire(self, blocking=True):
        return True

    def owned(self):
        return True

    def release(self):
        return None


class DummyRedis:
    def lock(self, *args, **kwargs):
        return DummyLock()


def test_pooling_assigns_ride(db_session, monkeypatch):
    monkeypatch.setattr(pooling_service, "redis_client", DummyRedis())

    db_session.add(Cab(seat_capacity=4, luggage_capacity=4))
    db_session.add_all(
        [
            Passenger(pickup_lat=12.9700, pickup_lng=77.5900, drop_lat=12.9800, drop_lng=77.6000, luggage_count=1, detour_tolerance=10),
            Passenger(pickup_lat=12.9705, pickup_lng=77.5904, drop_lat=12.9810, drop_lng=77.6010, luggage_count=1, detour_tolerance=10),
        ]
    )
    db_session.commit()

    result = PoolingService(db_session).run_pooling()

    assert result.ride_id is not None
    assert result.matched_passengers >= 1
