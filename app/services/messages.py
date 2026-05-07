import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.db import Base, Message

logger = logging.getLogger(__name__)


class MessagesService:
    def __init__(self, url: str):
        self.engine = create_async_engine(url, echo=False)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def connect(self) -> None:
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("PostgreSQL connection has been established.")
        except Exception as err:
            logger.error(f"Unable to connect to PostgreSQL: {err}")
            raise RuntimeError("PostgreSQL connection failed") from err

    async def close(self):
        await self.engine.dispose()
        logger.info("PostgreSQL connection has been closed.")

    async def write_message(self, message_id: UUID, recipients, subject, body_blob_path) -> Message | None:
        async with self.async_session() as session:
            stmt = (
                pg_insert(Message)
                .values(
                    message_id=message_id,
                    recipients=recipients,
                    subject=subject,
                    body_blob_path=body_blob_path,
                )
                .on_conflict_do_nothing(index_elements=["message_id"])
                .returning(Message)
            )
            result = await session.execute(stmt)
            message = result.scalar_one_or_none()
            await session.commit()
            logger.info("Message saved to PostgreSQL.")
            return message

    async def update_message(
        self,
        message_id: UUID,
        status: str,
        classification: str | None = None,
        summary: str | None = None,
        error_message: str | None = None,
    ) -> Message:
        async with self.async_session() as session:
            stmt = (
                update(Message)
                .where(Message.id == message_id)
                .values(
                    classification=classification,
                    summarization=summary,
                    status=status,
                    error_message=error_message,
                    processed_at=datetime.now(UTC),
                )
                .returning(Message)
            )
            result = await session.execute(stmt)
            message = result.scalar_one()
            await session.commit()
            if message:
                logger.info("Message saved to PostgreSQL.")
            else:
                logger.info("Duplicate message_id, skipped.")
            return message

    async def get_message(self, message_id: UUID) -> Message:
        async with self.async_session() as session:
            stmt = select(Message).where(Message.id == message_id)
            result = await session.execute(stmt)
            return result.scalar_one()
