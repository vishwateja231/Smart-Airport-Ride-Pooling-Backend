from pydantic import BaseModel, Field


class PassengerCreate(BaseModel):
    pickup_lat: float = Field(..., ge=-90, le=90)
    pickup_lng: float = Field(..., ge=-180, le=180)
    drop_lat: float = Field(..., ge=-90, le=90)
    drop_lng: float = Field(..., ge=-180, le=180)
    luggage_count: int = Field(default=0, ge=0)
    detour_tolerance: float = Field(default=0.2, ge=0, le=1)


class PassengerResponse(BaseModel):
    id: int
    status: str

    class Config:
        from_attributes = True
