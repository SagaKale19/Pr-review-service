from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Which PR was reviewed
    repo_owner: Mapped[str] = mapped_column(String(100))
    repo_name: Mapped[str] = mapped_column(String(100))
    pr_number: Mapped[int] = mapped_column(Integer)
    pr_title: Mapped[str | None] = mapped_column(String(500))

    # Lifecycle: pending -> completed / failed
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # LLM output
    summary: Mapped[str | None] = mapped_column(Text)
    comments: Mapped[list | None] = mapped_column(JSONB)
    model_used: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_reviews_repo_pr", "repo_owner", "repo_name", "pr_number"),
    )