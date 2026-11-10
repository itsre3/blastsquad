from fastapi import APIRouter

from .endpoints import (
    users,
    wallets,
    platforms,
    reviews,
)

api_router = APIRouter()

api_router.include_router(users.router, tags=["Users"])
#api_router.include_router(wallets.router, tags=["Wallets"])
#api_router.include_router(platforms.router, tags=["Platforms"])
#api_router.include_router(reviews.router, tags=["Reviews"])