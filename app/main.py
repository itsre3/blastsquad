from fastapi import FastAPI

from app.core.config import settings
from app.db.check import check_database
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "status": "running",
    }


@app.get("/health")
async def health():
    database_connected = await check_database()

    return {
        "status": "healthy" if database_connected else "unhealthy",
        "database": database_connected,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )