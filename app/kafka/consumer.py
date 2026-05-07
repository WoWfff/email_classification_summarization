import json
import logging

from aiokafka import AIOKafkaConsumer  # type: ignore

logger = logging.getLogger(__name__)


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
