import enum

from sqlalchemy import Enum, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CabStatus(str, enum.Enum):
    available = "available"
    full = "full"
    offline = "offline"


class Cab(Base):
    __tablename__ = "cabs"
    __table_args__ = (Index("idx_cab_status", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    seat_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    luggage_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[CabStatus] = mapped_column(Enum(CabStatus), nullable=False, default=CabStatus.available)
