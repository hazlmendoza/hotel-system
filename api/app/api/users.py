from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_roles
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
)


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)


# =========================================================
# GET ALL USERS
# Admin and manager
# =========================================================

@router.get(
    "/",
    response_model=list[UserResponse],
)
async def get_users(
    current_user: User = Depends(
        require_roles("admin", "manager")
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).order_by(User.id)
    )

    return result.scalars().all()


# =========================================================
# GET USER
# Admin and manager
# =========================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    current_user: User = Depends(
        require_roles("admin", "manager")
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            User.id == user_id
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# =========================================================
# CREATE USER
# Admin only
# =========================================================

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(
        require_roles("admin")
    ),
    db: AsyncSession = Depends(get_db),
):
    # Check if email already exists
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        role=user_data.role,
        is_active=True,
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


# =========================================================
# UPDATE USER
# Admin only
# =========================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(
        require_roles("admin")
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            User.id == user_id
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.email is not None:
        # Check email belongs to another user
        email_result = await db.execute(
            select(User).where(
                User.email == user_data.email,
                User.id != user_id,
            )
        )

        existing_email = email_result.scalar_one_or_none()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )

        user.email = user_data.email

    if user_data.password is not None:
        user.password_hash = hash_password(
            user_data.password
        )

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    return user


# =========================================================
# DELETE / DEACTIVATE USER
# Admin only
# =========================================================

@router.delete(
    "/{user_id}",
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(
        require_roles("admin")
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            User.id == user_id
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Don't allow admin to delete themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    # Soft delete instead of permanently deleting
    user.is_active = False

    await db.commit()

    return {
        "message": "User deactivated successfully"
    }
