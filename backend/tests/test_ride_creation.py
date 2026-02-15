from app.schemas.passenger import PassengerCreate
from app.services.passenger_service import PassengerService


def test_ride_request_creates_passenger(db_session):
    service = PassengerService(db_session)
    passenger = service.request_ride(
        PassengerCreate(
            pickup_lat=12.97,
            pickup_lng=77.59,
            drop_lat=13.01,
            drop_lng=77.62,
            luggage_count=1,
            detour_tolerance=0.2,
        )
    )
    db_session.commit()

    assert passenger.id is not None
    assert passenger.status.value == "waiting"
