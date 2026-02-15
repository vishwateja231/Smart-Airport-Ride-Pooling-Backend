from app.db.session import SessionLocal
from app.models.cab import Cab
from app.models.passenger import Passenger


def run_seed() -> None:
    db = SessionLocal()
    try:
        if db.query(Cab).count() == 0:
            db.add_all(
                [
                    Cab(seat_capacity=4, luggage_capacity=6),
                    Cab(seat_capacity=3, luggage_capacity=4),
                    Cab(seat_capacity=6, luggage_capacity=8),
                ]
            )

        if db.query(Passenger).count() == 0:
            db.add_all(
                [
                    Passenger(pickup_lat=12.97, pickup_lng=77.59, drop_lat=12.99, drop_lng=77.62, luggage_count=1, detour_tolerance=0.3),
                    Passenger(pickup_lat=12.971, pickup_lng=77.591, drop_lat=13.01, drop_lng=77.63, luggage_count=1, detour_tolerance=0.25),
                    Passenger(pickup_lat=12.972, pickup_lng=77.592, drop_lat=13.03, drop_lng=77.65, luggage_count=2, detour_tolerance=0.4),
                    Passenger(pickup_lat=12.973, pickup_lng=77.593, drop_lat=13.04, drop_lng=77.66, luggage_count=1, detour_tolerance=0.35),
                    Passenger(pickup_lat=12.974, pickup_lng=77.594, drop_lat=13.05, drop_lng=77.67, luggage_count=1, detour_tolerance=0.2),
                ]
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
