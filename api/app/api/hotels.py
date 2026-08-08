from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.hotel import Hotel
from app.schemas.hotel import HotelCreate, HotelResponse


router = APIRouter(
    prefix="/api/v1/hotels",
    tags=["Hotels"],
)


@router.post("/", response_model=HotelResponse)
async def create_hotel(
    hotel_data: HotelCreate,
    db: AsyncSession = Depends(get_db),
):
    hotel = Hotel(
        name=hotel_data.name,
        description=hotel_data.description,
        address=hotel_data.address,
    )

    db.add(hotel)

    await db.commit()
    await db.refresh(hotel)

    return hotel


@router.get("/", response_model=list[HotelResponse])
async def get_hotels(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Hotel)
    )

    return result.scalars().all()


@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel(
    hotel_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Hotel).where(
            Hotel.id == hotel_id
        )
    )

    hotel = result.scalar_one_or_none()

    if hotel is None:
        raise HTTPException(
            status_code=404,
            detail="Hotel not found",
        )

    return hotel


@router.put("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(
    hotel_id: int,
    hotel_data: HotelCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Hotel).where(
            Hotel.id == hotel_id
        )
    )

    hotel = result.scalar_one_or_none()

    if hotel is None:
        raise HTTPException(
            status_code=404,
            detail="Hotel not found",
        )

    hotel.name = hotel_data.name
    hotel.description = hotel_data.description
    hotel.address = hotel_data.address

    await db.commit()
    await db.refresh(hotel)

    return hotel


@router.delete("/{hotel_id}")
async def delete_hotel(
    hotel_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Hotel).where(
            Hotel.id == hotel_id
        )
    )

    hotel = result.scalar_one_or_none()

    if hotel is None:
        raise HTTPException(
            status_code=404,
            detail="Hotel not found",
        )

    await db.delete(hotel)
    await db.commit()

    return {
        "message": "Hotel deleted successfully"
    }
