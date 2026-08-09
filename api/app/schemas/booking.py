from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BookingCreate(BaseModel):
    guest_id: int
    room_id: int
    hotel_id: int

    check_in: date
    check_out: date

    guests_count: int = 1


class BookingResponse(BaseModel):
    id: int

    guest_id: int
    room_id: int
    hotel_id: int

    check_in: date
    check_out: date

    guests_count: int
    total_price: Decimal
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
