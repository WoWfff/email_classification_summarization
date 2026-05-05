import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.db_models import Base

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
