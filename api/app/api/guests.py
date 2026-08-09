from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_roles
from app.models.guest import Guest
from app.models.user import User
from app.schemas.guest import GuestCreate, GuestResponse


router = APIRouter(
    prefix="/api/v1/guests",
    tags=["Guests"],
)


# =========================================================
# GET ALL GUESTS
#
# Admin, manager and front desk can view guests
# =========================================================

@router.get(
    "/",
    response_model=list[GuestResponse],
)
async def get_guests(
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "front_desk",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Guest)
    )

    return result.scalars().all()


# =========================================================
# GET SINGLE GUEST
# =========================================================

@router.get(
    "/{guest_id}",
    response_model=GuestResponse,
)
async def get_guest(
    guest_id: int,
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "front_desk",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Guest).where(
            Guest.id == guest_id
        )
    )

    guest = result.scalar_one_or_none()

    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    return guest


# =========================================================
# CREATE GUEST
#
# Admin, manager and front desk
# =========================================================

@router.post(
    "/",
    response_model=GuestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_guest(
    guest_data: GuestCreate,
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "front_desk",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Guest).where(
            Guest.email == guest_data.email
        )
    )

    existing_guest = result.scalar_one_or_none()

    if existing_guest:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest with this email already exists",
        )

    guest = Guest(
        first_name=guest_data.first_name,
        last_name=guest_data.last_name,
        email=guest_data.email,
        phone=guest_data.phone,
        address=guest_data.address,
        id_type=guest_data.id_type,
        id_number=guest_data.id_number,
    )

    db.add(guest)

    await db.commit()
    await db.refresh(guest)

    return guest


# =========================================================
# UPDATE GUEST
# =========================================================

@router.put(
    "/{guest_id}",
    response_model=GuestResponse,
)
async def update_guest(
    guest_id: int,
    guest_data: GuestCreate,
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "front_desk",
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Guest).where(
            Guest.id == guest_id
        )
    )

    guest = result.scalar_one_or_none()

    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    guest.first_name = guest_data.first_name
    guest.last_name = guest_data.last_name
    guest.email = guest_data.email
    guest.phone = guest_data.phone
    guest.address = guest_data.address
    guest.id_type = guest_data.id_type
    guest.id_number = guest_data.id_number

    await db.commit()
    await db.refresh(guest)

    return guest


# =========================================================
# DELETE GUEST
#
# Admin only
# =========================================================

@router.delete(
    "/{guest_id}",
)
async def delete_guest(
    guest_id: int,
    current_user: User = Depends(
        require_roles("admin")
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Guest).where(
            Guest.id == guest_id
        )
    )

    guest = result.scalar_one_or_none()

    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guest not found",
        )

    await db.delete(guest)
    await db.commit()

    return {
        "message": "Guest deleted successfully"
    }
