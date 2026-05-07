import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Kafka input
    recipients: Mapped[list] = mapped_column(JSONB, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    body_blob_path: Mapped[str] = mapped_column(String, nullable=False)

    # AI results
    classification: Mapped[str | None] = mapped_column(String, nullable=True)
    summarization: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="pending")
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
