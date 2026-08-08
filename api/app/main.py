from fastapi import FastAPI

from app.api.hotels import router as hotel_router


app = FastAPI(
    title="Hotel System API",
    version="1.0.0",
)


app.include_router(hotel_router)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }
