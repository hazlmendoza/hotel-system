from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_roles
from app.models.booking import Booking
from app.models.guest import Guest
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse


router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["Bookings"],
)


# =========================================================
# GET ALL BOOKINGS
# Authenticated employees
# =========================================================

@router.get(
    "/",
    response_model=list[BookingResponse],
)
async def get_bookings(
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "front_desk",
            "housekeeping",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Booking)
    )

    return result.scalars().all()


# =========================================================
# GET SINGLE BOOKING
# Authenticated employees
# =========================================================

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "front_desk",
            "housekeeping",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Booking).where(
            Booking.id == booking_id
        )
    )

    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking


# =========================================================
# CREATE BOOKING
# Admin, manager and front desk
# =========================================================

@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "front_desk",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    # Check guest
    guest_result = await db.execute(
        select(Guest).where(
            Guest.id == booking_data.guest_id
        )
    )

    guest = guest_result.scalar_one_or_none()

    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    # Check hotel
    hotel_result = await db.execute(
        select(Hotel).where(
            Hotel.id == booking_data.hotel_id
        )
    )

    hotel = hotel_result.scalar_one_or_none()

    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel not found",
        )

    # Check room
    room_result = await db.execute(
        select(Room).where(
            Room.id == booking_data.room_id
        )
    )

    room = room_result.scalar_one_or_none()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    # Make sure room belongs to hotel
    if room.hotel_id != booking_data.hotel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room does not belong to this hotel",
        )

    # Validate dates
    if booking_data.check_out <= booking_data.check_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be after check-in date",
        )

    # Validate guest count
    if booking_data.guests_count < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guests count must be at least 1",
        )

    if booking_data.guests_count > room.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of guests exceeds room capacity",
        )

    # Check room availability for the requested dates
    overlapping_result = await db.execute(
        select(Booking).where(
            Booking.room_id == booking_data.room_id,
            Booking.status.in_(
                ["pending", "confirmed"]
            ),
            Booking.check_in < booking_data.check_out,
            Booking.check_out > booking_data.check_in,
        )
    )

    existing_booking = (
        overlapping_result.scalar_one_or_none()
    )

    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room is already booked for these dates",
        )

    # Calculate total price
    number_of_nights = (
        booking_data.check_out
        - booking_data.check_in
    ).days

    total_price = (
        room.price_per_night
        * number_of_nights
    )

    booking = Booking(
        guest_id=booking_data.guest_id,
        room_id=booking_data.room_id,
        hotel_id=booking_data.hotel_id,
        check_in=booking_data.check_in,
        check_out=booking_data.check_out,
        guests_count=booking_data.guests_count,
        total_price=total_price,
        status="pending",
    )

    db.add(booking)

    await db.commit()
    await db.refresh(booking)

    return booking


# =========================================================
# UPDATE BOOKING STATUS
# Admin, manager and front desk
# =========================================================

@router.patch(
    "/{booking_id}/status",
    response_model=BookingResponse,
)
async def update_booking_status(
    booking_id: int,
    new_status: str,
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "front_desk",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    allowed_statuses = {
        "pending",
        "confirmed",
        "cancelled",
        "completed",
    }

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid status. "
                "Allowed values: pending, confirmed, "
                "cancelled, completed"
            ),
        )

    result = await db.execute(
        select(Booking).where(
            Booking.id == booking_id
        )
    )

    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    booking.status = new_status

    await db.commit()
    await db.refresh(booking)

    return booking


# =========================================================
# DELETE / CANCEL BOOKING
# Admin and manager
# =========================================================

@router.delete(
    "/{booking_id}",
)
async def delete_booking(
    booking_id: int,
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Booking).where(
            Booking.id == booking_id
        )
    )

    booking = result.scalar_one_or_none()

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    await db.delete(booking)

    await db.commit()

    return {
        "message": "Booking deleted successfully"
    }
