import uuid
from datetime import datetime

from sqlalchemy import (
    Uuid,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_reviews_rating_range",
        ),
        UniqueConstraint(
            "platform_id",
            "external_reference",
            name="uq_reviews_platform_external_ref",
        ),
        Index("ix_reviews_subject_user_id", "subject_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    subject_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    platform_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("platforms.id", ondelete="RESTRICT"),
        nullable=False,
    )

    external_reference: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    subject: Mapped["User"] = relationship(
        back_populates="reviews_received"
    )

    platform: Mapped["Platform"] = relationship(
        back_populates="reviews"
    )