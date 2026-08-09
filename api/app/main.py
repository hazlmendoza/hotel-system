from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.hotels import router as hotel_router
from app.api.users import router as user_router
from app.api.rooms import router as room_router
from app.api.guests import router as guest_router
from app.api.bookings import router as booking_router

app = FastAPI(
    title="Hotel System API",
    description="Internal hotel management system API",
    version="1.0.0",
)


# API routes
app.include_router(auth_router)
app.include_router(hotel_router)
app.include_router(user_router)
app.include_router(room_router)
app.include_router(guest_router)
app.include_router(booking_router)


@app.get("/")
async def root():
    return {
        "message": "Hotel System API is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }
