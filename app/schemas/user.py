from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WalletPublic(BaseModel):
    address: str
    verified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CredentialPublic(BaseModel):
    mint_address: str
    issued_at: datetime
    revoked_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class UserPublic(BaseModel):
    id: UUID
    username: str
    created_at: datetime

    wallets: list[WalletPublic]
    credentials: list[CredentialPublic]

    average_rating: float
    review_count: int

    model_config = ConfigDict(from_attributes=True)

class WalletChallengeRequest(BaseModel):
    wallet_address: str = Field(min_length=32, max_length=44)

class WalletChallengeResponse(BaseModel):
    wallet_address: str
    message: str