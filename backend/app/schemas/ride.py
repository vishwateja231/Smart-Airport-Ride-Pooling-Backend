from pydantic import BaseModel


class RidePassengerInfo(BaseModel):
    passenger_id: int
    pickup_order: int
    drop_order: int


class RideResponse(BaseModel):
    id: int
    cab_id: int
    status: str
    total_price: float
    passengers: list[RidePassengerInfo]


class PoolRunResponse(BaseModel):
    ride_id: int | None
    matched_passengers: int
    message: str
