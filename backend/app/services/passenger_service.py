from sqlalchemy.orm import Session

from app.models.passenger import Passenger
from app.repositories.passenger_repository import PassengerRepository
from app.schemas.passenger import PassengerCreate


class PassengerService:
    def __init__(self, db: Session):
        self.repo = PassengerRepository(db)

    def request_ride(self, payload: PassengerCreate) -> Passenger:
        passenger = Passenger(**payload.model_dump())
        return self.repo.create(passenger)
