from pydantic import BaseModel


class HotelCreate(BaseModel):
    name: str
    description: str | None = None
    address: str


class HotelResponse(BaseModel):
    id: int
    name: str
    description: str | None
    address: str

    model_config = {
        "from_attributes": True
    }