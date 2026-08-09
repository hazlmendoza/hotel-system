from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_roles
from app.models.room import Room
from app.models.user import User
from app.schemas.room import RoomCreate, RoomResponse


router = APIRouter(
    prefix="/api/v1/rooms",
    tags=["Rooms"],
)


# =========================================================
# GET ALL ROOMS
# Admin, manager, front desk, housekeeping
# =========================================================

@router.get(
    "/",
    response_model=list[RoomResponse],
)
async def get_rooms(
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
        select(Room)
    )

    return result.scalars().all()


# =========================================================
# GET SINGLE ROOM
# =========================================================

@router.get(
    "/{room_id}",
    response_model=RoomResponse,
)
async def get_room(
    room_id: int,
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
        select(Room).where(
            Room.id == room_id
        )
    )

    room = result.scalar_one_or_none()

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    return room


# =========================================================
# CREATE ROOM
# Admin and manager
# =========================================================

@router.post(
    "/",
    response_model=RoomResponse,
)
async def create_room(
    room_data: RoomCreate,
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    room = Room(
        hotel_id=room_data.hotel_id,
        room_number=room_data.room_number,
        room_type=room_data.room_type,
        price_per_night=room_data.price_per_night,
        capacity=room_data.capacity,
        status=room_data.status,
    )

    db.add(room)

    await db.commit()
    await db.refresh(room)

    return room


# =========================================================
# UPDATE ROOM
# Admin and manager
# =========================================================

@router.put(
    "/{room_id}",
    response_model=RoomResponse,
)
async def update_room(
    room_id: int,
    room_data: RoomCreate,
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Room).where(
            Room.id == room_id
        )
    )

    room = result.scalar_one_or_none()

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    room.hotel_id = room_data.hotel_id
    room.room_number = room_data.room_number
    room.room_type = room_data.room_type
    room.price_per_night = room_data.price_per_night
    room.capacity = room_data.capacity
    room.status = room_data.status

    await db.commit()
    await db.refresh(room)

    return room


# =========================================================
# DELETE ROOM
# Admin only
# =========================================================

@router.delete(
    "/{room_id}"
)
async def delete_room(
    room_id: int,
    current_user: User = Depends(
        require_roles("admin")
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Room).where(
            Room.id == room_id
        )
    )

    room = result.scalar_one_or_none()

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    await db.delete(room)

    await db.commit()

    return {
        "message": "Room deleted successfully"
    }
