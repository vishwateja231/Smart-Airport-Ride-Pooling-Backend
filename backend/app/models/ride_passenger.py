from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RidePassenger(Base):
    __tablename__ = "ride_passengers"

    ride_id: Mapped[int] = mapped_column(ForeignKey("rides.id", ondelete="CASCADE"), primary_key=True)
    passenger_id: Mapped[int] = mapped_column(ForeignKey("passengers.id", ondelete="CASCADE"), primary_key=True)
    pickup_order: Mapped[int] = mapped_column(Integer, nullable=False)
    drop_order: Mapped[int] = mapped_column(Integer, nullable=False)
