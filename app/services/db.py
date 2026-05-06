import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.db_models import Base, Message

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, url: str):
        self.engine = create_async_engine(url, echo=False)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def connect(self) -> None:
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("A database connection has been established.")
        except Exception as err:
            logger.error(f"Unable to connect to the database: {err}")
            raise RuntimeError("DB connection failed") from err

    async def close(self):
        await self.engine.dispose()
        logger.info("A database connection has been closed.")

    async def write_message(self, recipients: list[str], subject: str, body_blob_path: str) -> Message:
        async with self.async_session() as session:
            stmt = (
                insert(Message)
                .values(recipients=recipients, subject=subject, body_blob_path=body_blob_path)
                .returning(Message)
            )
            result = await session.execute(stmt)
            message = result.scalar_one()
            await session.commit()
            logger.info("Message saved to database.")
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
            logger.info("Message updated in database.")
            return message

    async def get_message(self, message_id: UUID) -> Message:
        async with self.async_session() as session:
            stmt = select(Message).where(Message.id == message_id)
            result = await session.execute(stmt)
            return result.scalar_one()
