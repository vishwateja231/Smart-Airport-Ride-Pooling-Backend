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


def test_pooling_marks_cab_unavailable_after_assignment(db_session, monkeypatch):
    monkeypatch.setattr(pooling_service, "redis_client", DummyRedis())

    cab = Cab(seat_capacity=4, luggage_capacity=4)
    db_session.add(cab)
    db_session.add_all(
        [
            Passenger(pickup_lat=12.9700, pickup_lng=77.5900, drop_lat=12.9800, drop_lng=77.6000, luggage_count=1, detour_tolerance=10),
            Passenger(pickup_lat=12.9703, pickup_lng=77.5902, drop_lat=12.9805, drop_lng=77.6005, luggage_count=1, detour_tolerance=10),
            Passenger(pickup_lat=12.9704, pickup_lng=77.5903, drop_lat=12.9806, drop_lng=77.6006, luggage_count=1, detour_tolerance=10),
        ]
    )
    db_session.commit()

    first_run = PoolingService(db_session).run_pooling()
    second_run = PoolingService(db_session).run_pooling()

    db_session.refresh(cab)
    assert first_run.ride_id is not None
    assert cab.status.value == "full"
    assert second_run.ride_id is None


def test_pooling_uses_dynamic_anchor_when_first_anchor_not_feasible(db_session, monkeypatch):
    monkeypatch.setattr(pooling_service, "redis_client", DummyRedis())

    db_session.add(Cab(seat_capacity=4, luggage_capacity=2))

    # First passenger cannot fit luggage constraints for this cab, so this anchor
    # should be skipped and the next passenger should be used as anchor.
    db_session.add_all(
        [
            Passenger(pickup_lat=12.9700, pickup_lng=77.5900, drop_lat=12.9800, drop_lng=77.6000, luggage_count=5, detour_tolerance=0.1),
            Passenger(pickup_lat=12.9701, pickup_lng=77.5901, drop_lat=12.9801, drop_lng=77.6001, luggage_count=1, detour_tolerance=10),
            Passenger(pickup_lat=12.9702, pickup_lng=77.5902, drop_lat=12.9802, drop_lng=77.6002, luggage_count=1, detour_tolerance=10),
        ]
    )
    db_session.commit()

    result = PoolingService(db_session).run_pooling()

    assert result.ride_id is not None
    assert result.matched_passengers >= 1
