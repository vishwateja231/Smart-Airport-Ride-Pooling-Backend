import enum

from sqlalchemy import Enum, ForeignKey, Index, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RideStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"
    completed = "completed"


class Ride(Base):
    __tablename__ = "rides"
    __table_args__ = (Index("idx_ride_status", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cab_id: Mapped[int] = mapped_column(ForeignKey("cabs.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[RideStatus] = mapped_column(Enum(RideStatus), nullable=False, default=RideStatus.active)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
