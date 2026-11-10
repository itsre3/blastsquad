
import uuid
from datetime import datetime

from sqlalchemy import (
    Uuid,
    String,
    ForeignKey,
    DateTime,
    Index,
    func,
    text,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from app.db.session import Base


class Credential(Base):
    __tablename__ = "credentials"

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "wallet_id"],
            ["wallets.user_id", "wallets.id"],
            ondelete="RESTRICT",
            name="fk_credentials_user_wallet",
        ),
        Index(
            "uq_credentials_one_active_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )

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

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
    )

    mint_address: Mapped[str] = mapped_column(
        String(44),
        unique=True,
        nullable=False,
    )

    transaction_signature: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="credentials"
    )

    wallet: Mapped["Wallet"] = relationship(
        back_populates="credentials",
        primaryjoin="and_(Wallet.id == foreign(Credential.wallet_id), Wallet.user_id == Credential.user_id)",
    )
