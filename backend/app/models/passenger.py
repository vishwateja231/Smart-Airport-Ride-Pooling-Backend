import enum

from sqlalchemy import Enum, Float, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PassengerStatus(str, enum.Enum):
    waiting = "waiting"
    assigned = "assigned"
    cancelled = "cancelled"
    completed = "completed"


class Passenger(Base):
    __tablename__ = "passengers"
    __table_args__ = (
        Index("idx_passenger_status", "status"),
        Index("idx_passenger_pickup_lat", "pickup_lat"),
        Index("idx_passenger_pickup_lng", "pickup_lng"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pickup_lat: Mapped[float] = mapped_column(Float, nullable=False)
    pickup_lng: Mapped[float] = mapped_column(Float, nullable=False)
    drop_lat: Mapped[float] = mapped_column(Float, nullable=False)
    drop_lng: Mapped[float] = mapped_column(Float, nullable=False)
    luggage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    detour_tolerance: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)
    status: Mapped[PassengerStatus] = mapped_column(
        Enum(PassengerStatus), nullable=False, default=PassengerStatus.waiting
    )
