from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.passenger import Passenger, PassengerStatus


class PassengerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, passenger: Passenger) -> Passenger:
        self.db.add(passenger)
        self.db.flush()
        self.db.refresh(passenger)
        return passenger

    def waiting(self) -> list[Passenger]:
        stmt = select(Passenger).where(Passenger.status == PassengerStatus.waiting).order_by(Passenger.id)
        return list(self.db.scalars(stmt).all())

    def by_ids(self, ids: list[int]) -> list[Passenger]:
        stmt = select(Passenger).where(Passenger.id.in_(ids))
        return list(self.db.scalars(stmt).all())
