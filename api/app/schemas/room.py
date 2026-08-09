from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RoomCreate(BaseModel):
    hotel_id: int
    room_number: str
    room_type: str
    price_per_night: Decimal
    capacity: int
    status: str = "available"


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_id: int
    room_number: str
    room_type: str
    price_per_night: Decimal
    capacity: int
    status: str
    created_at: datetime
