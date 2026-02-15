from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ride_passenger import RidePassenger
from app.schemas.passenger import PassengerCreate, PassengerResponse
from app.schemas.ride import PoolRunResponse, RidePassengerInfo, RideResponse
from app.services.passenger_service import PassengerService
from app.services.pooling_service import PoolingService
from app.services.ride_service import RideService

router = APIRouter()


@router.post("/passengers/request_ride", response_model=PassengerResponse)
def request_ride(payload: PassengerCreate, db: Session = Depends(get_db)) -> PassengerResponse:
    service = PassengerService(db)
    passenger = service.request_ride(payload)
    db.commit()
    return PassengerResponse(id=passenger.id, status=passenger.status.value)


@router.get("/ride/{ride_id}", response_model=RideResponse)
def get_ride(ride_id: int, db: Session = Depends(get_db)) -> RideResponse:
    service = RideService(db)
    ride = service.get_ride(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    ride_passengers = db.query(RidePassenger).filter(RidePassenger.ride_id == ride_id).all()
    return RideResponse(
        id=ride.id,
        cab_id=ride.cab_id,
        status=ride.status.value,
        total_price=float(ride.total_price),
        passengers=[
            RidePassengerInfo(
                passenger_id=rp.passenger_id,
                pickup_order=rp.pickup_order,
                drop_order=rp.drop_order,
            )
            for rp in ride_passengers
        ],
    )


@router.delete("/ride/{ride_id}", response_model=RideResponse)
def cancel_ride(ride_id: int, db: Session = Depends(get_db)) -> RideResponse:
    service = RideService(db)
    ride = service.cancel_ride(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    ride_passengers = db.query(RidePassenger).filter(RidePassenger.ride_id == ride_id).all()
    return RideResponse(
        id=ride.id,
        cab_id=ride.cab_id,
        status=ride.status.value,
        total_price=float(ride.total_price),
        passengers=[
            RidePassengerInfo(
                passenger_id=rp.passenger_id,
                pickup_order=rp.pickup_order,
                drop_order=rp.drop_order,
            )
            for rp in ride_passengers
        ],
    )


@router.post("/pool/run", response_model=PoolRunResponse)
def run_pool(db: Session = Depends(get_db)) -> PoolRunResponse:
    service = PoolingService(db)
    result = service.run_pooling()
    return PoolRunResponse(**result.__dict__)
