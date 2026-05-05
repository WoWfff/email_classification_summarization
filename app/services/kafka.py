import json
import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer  # type: ignore
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Producer:
    def __init__(self, bootstrap_servers: str):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    async def __aenter__(self):
        await self.producer.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.producer.stop()

    async def send(self, topic: str, message: BaseModel, key: bytes | None = None) -> None:
        try:
            await self.producer.send_and_wait(topic, message.model_dump(), key=key)
            logger.info(f"Message sent to '{topic}'")
        except Exception:
            logger.error(f"Error sending message to '{topic}'")
            raise


class Consumer:
    def __init__(self, topic: str, bootstrap_servers: str, group_id: str):
        self.consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )

    async def start(self):
        await self.consumer.start()
        logger.info("Consumer started.")

    async def stop(self):
        await self.consumer.stop()
        logger.info("Consumer stopped.")

    async def __aiter__(self):
        async for msg in self.consumer:
            yield msg

    async def commit(self):
        await self.consumer.commit()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
