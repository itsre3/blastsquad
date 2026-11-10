import uuid
from datetime import datetime

from sqlalchemy import Uuid, String, Index, text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        String(256),
        unique=True,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    wallets: Mapped[list["Wallet"]] = relationship(
        back_populates="user"
    )
    credentials: Mapped[list["Credential"]] = relationship(
        back_populates="user"
    )
    reviews_received: Mapped[list["Review"]] = relationship(
        back_populates="subject"
    )

    __table_args__ = (
        Index(
            "ix_users_username_lower",
            #expressions=text("lower(username)"),
            text("lower(username)"),
            unique=True,
        ),
    )