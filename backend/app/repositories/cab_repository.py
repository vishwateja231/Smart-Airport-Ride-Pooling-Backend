from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cab import Cab, CabStatus


class CabRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_available_with_lock(self) -> list[Cab]:
        stmt = (
            select(Cab)
            .where(Cab.status == CabStatus.available)
            .order_by(Cab.id)
            .with_for_update(skip_locked=True)
        )
        return list(self.db.scalars(stmt).all())
