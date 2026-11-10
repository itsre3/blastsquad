
import hashlib
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from solders.pubkey import Pubkey
from solders.signature import Signature

from app.db.session import get_db
from app.models import User, Wallet
from app.schemas.user import (
    WalletChallengeRequest,
    WalletChallengeResponse,
    UserPublic,
)
from app.services.wallet import generate_wallet_challenge


router = APIRouter(prefix="/users", tags=["Users"])

# Temporary in-memory challenge storage.
# Replace with Redis or database storage for production.
challenges = {}


class WalletConnectRequest(BaseModel):
    wallet_address: str
    message: str
    signature: str = Field(min_length=80, max_length=100)


@router.post(
    "/challenge",
    response_model=WalletChallengeResponse,
)
async def create_wallet_challenge(
    data: WalletChallengeRequest,
):
    try:
        Pubkey.from_string(data.wallet_address)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Solana wallet address",
        )

    message = generate_wallet_challenge(data.wallet_address)

    challenges[data.wallet_address] = {
        "message": message,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
    }

    return WalletChallengeResponse(
        wallet_address=data.wallet_address,
        message=message,
    )


@router.post("/connect-wallet")
async def connect_wallet(
    data: WalletConnectRequest,
    db: AsyncSession = Depends(get_db),
):
    challenge = challenges.pop(data.wallet_address, None)

    if challenge is None:
        raise HTTPException(
            status_code=401,
            detail="Challenge not found or already used",
        )

    if datetime.now(timezone.utc) > challenge["expires_at"]:
        raise HTTPException(
            status_code=401,
            detail="Challenge expired",
        )

    if data.message != challenge["message"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid challenge message",
        )

    try:
        public_key = Pubkey.from_string(data.wallet_address)
        signature = Signature.from_string(data.signature)

        verified = signature.verify(
            public_key,
            data.message.encode("utf-8"),
        )
    except ValueError:
        verified = False

    if not verified:
        raise HTTPException(
            status_code=401,
            detail="Wallet signature verification failed",
        )

    result = await db.execute(
        select(Wallet)
        .options(selectinload(Wallet.user))
        .where(Wallet.address == data.wallet_address)
    )

    existing_wallet = result.scalar_one_or_none()

    if existing_wallet:
        if existing_wallet.revoked_at is not None:
            raise HTTPException(
                status_code=403,
                detail="This wallet has been revoked",
            )

        return {
            "message": "Wallet already connected",
            "user_id": str(existing_wallet.user.id),
            "username": existing_wallet.user.username,
            "wallet_address": existing_wallet.address,
            "created": False,
        }

    username_hash = hashlib.sha256(
        data.wallet_address.encode()
    ).hexdigest()[:16]

    user = User(
        username=f"wallet_{username_hash}"
    )

    db.add(user)
    await db.flush()

    wallet = Wallet(
        user_id=user.id,
        address=data.wallet_address,
        verified_at=datetime.now(timezone.utc),
    )

    db.add(wallet)
    await db.commit()

    return {
        "message": "Identity created successfully",
        "user_id": str(user.id),
        "username": user.username,
        "wallet_address": wallet.address,
        "created": True,
    }


@router.get("/{username}", response_model=UserPublic)
async def get_user_profile(
    username: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.wallets),
            selectinload(User.credentials),
            selectinload(User.reviews_received),
        )
        .where(User.username == username)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    reviews = user.reviews_received

    average_rating = (
        sum(review.rating for review in reviews) / len(reviews)
        if reviews else 0.0
    )

    return {
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at,
        "wallets": [
            wallet for wallet in user.wallets
            if wallet.revoked_at is None
        ],
        "credentials": [
            credential for credential in user.credentials
            if credential.revoked_at is None
        ],
        "average_rating": round(average_rating, 2),
        "review_count": len(reviews),
    }
