from time import time
import uuid
from datetime import datetime

from sqlalchemy import (
    Uuid, String, ForeignKey, Index, DateTime, func, text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from app.db.session import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    address: Mapped[str] = mapped_column(
        String(44),
        unique=True,
        nullable=False,
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        #server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[list["User"]] = relationship(
        #"User",
        back_populates="wallets"
    )
    credentials: Mapped[list["Credential"]] = relationship(
        back_populates="wallet",
        primaryjoin="and_(Wallet.id == foreign(Credential.wallet_id), Wallet.user_id == Credential.user_id)",
    )

    __table_args__ = (
        Index(
            "uq_wallets_one_active_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("revoked_at is NULL")
        ),
        UniqueConstraint(
            "user_id",
            "id",
            name="uq_wallets_user_id_id"
        )
    )