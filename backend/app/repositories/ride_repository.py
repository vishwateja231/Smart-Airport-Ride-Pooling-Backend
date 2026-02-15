from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ride import Ride


class RideRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, ride: Ride) -> Ride:
        self.db.add(ride)
        self.db.flush()
        self.db.refresh(ride)
        return ride

    def get(self, ride_id: int) -> Ride | None:
        return self.db.get(Ride, ride_id)

    def all_for_cab(self, cab_id: int) -> list[Ride]:
        stmt = select(Ride).where(Ride.cab_id == cab_id)
        return list(self.db.scalars(stmt).all())
