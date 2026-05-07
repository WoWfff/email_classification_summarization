import json
import logging

from aiokafka import AIOKafkaProducer  # type: ignore
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Producer:
    def __init__(self, bootstrap_servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        )

    async def start(self):
        await self.producer.start()
        logger.info("Producer started.")

    async def stop(self):
        await self.producer.stop()
        logger.info("Producer stopped.")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def send(self, topic: str, message: BaseModel, key: bytes | None = None) -> None:
        try:
            await self.producer.send_and_wait(topic, message.model_dump(), key=key)
            logger.info(f"Message sent to '{topic}'")
        except Exception:
            logger.error(f"Error sending message to '{topic}'")
            raise
