import asyncio
import logging
from pathlib import Path

from app.config import KAFKA_CONSUMER_GROUP_ID, KAFKA_INPUT_TOPIC
from app.models.kafka_models import InputMessage
from app.services.blob_storage import FileSystemBlobStorage
from app.services.containers import create_kafka, create_postgres
from app.services.db import Database
from app.services.kafka import Consumer, Producer
from dotenv import load_dotenv

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
storage = FileSystemBlobStorage(Path("data/blobs"))

# Test data
messages = [
    InputMessage(
        recipients=["anna@example.com", "bob@example.com"],
        subject="Monday schedule",
        body_blob_path="monday_schedule.txt",
    ),
    InputMessage(
        recipients=["sam@example.com", "j@example.com"],
        subject="Google security alert",
        body_blob_path="google.txt",
    ),
    InputMessage(
        recipients=["dj@example.com", "ollama@example.com"],
        subject="LinkedIn offer",
        body_blob_path="linkedin.txt",
    ),
    InputMessage(
        recipients=["open@example.com", "groov@example.com"],
        subject="Daily offer",
        body_blob_path="daily_offer.txt",
    ),
]


async def main():
    postgres_url = create_postgres()
    kafka_bootstrap = create_kafka()
    db = Database(url=postgres_url)

    await db.connect()

    async with Producer(kafka_bootstrap) as producer:
        for message in messages:
            await producer.send(topic=KAFKA_INPUT_TOPIC, message=message, key=message.subject.encode())

    consumer = Consumer(topic=KAFKA_INPUT_TOPIC, bootstrap_servers=kafka_bootstrap, group_id=KAFKA_CONSUMER_GROUP_ID)
    await consumer.start()

    try:
        async for msg in consumer:
            try:
                logger.info(f"Got message from topic={msg.topic}, partition={msg.partition}, offset={msg.offset}")
                email_msg = InputMessage(**msg.value)
                body = await storage.read_text(email_msg.body_blob_path)

                await consumer.commit()

            except Exception as e:
                logger.exception(f"Error while processing message: {e}")
    finally:
        await consumer.stop()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
