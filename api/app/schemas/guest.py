from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class GuestCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str | None = None
    id_type: str | None = None
    id_number: str | None = None


class GuestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str | None
    id_type: str | None
    id_number: str | None
    created_at: datetime
