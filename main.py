import asyncio
import logging
from pathlib import Path

from app.config import (
    KAFKA_CLASSIFICATION_CONSUMER_GROUP_ID,
    KAFKA_CLASSIFICATION_TOPIC,
    KAFKA_INPUT_CONSUMER_GROUP_ID,
    KAFKA_INPUT_TOPIC,
    KAFKA_SUMMARIZATION_CONSUMER_GROUP_ID,
    KAFKA_SUMMARIZATION_TOPIC,
)
from app.models.kafka_models import ClassificationResult, InputMessage, SummarizationResult
from app.services.agent import State, graph
from app.services.blob_storage import FileSystemBlobStorage
from app.services.containers import create_kafka, create_postgres
from app.services.db import Database
from app.services.kafka import Consumer, Producer

# Configuration
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


async def process_input_messages(consumer: Consumer, producer: Producer, db: Database):
    try:
        db_msg = None
        async for msg in consumer:
            print("\n")
            try:
                logger.info(f"Got message from topic={msg.topic}, partition={msg.partition}, offset={msg.offset}")
                email_msg = InputMessage.model_validate(msg.value)

                body = await storage.read_text(email_msg.body_blob_path)

                # Writing received message to PostgreSQL database
                db_msg = await db.write_message(
                    recipients=email_msg.recipients,
                    subject=email_msg.subject,
                    body_blob_path=email_msg.body_blob_path,
                )

                # Initializing start graph
                initial_state = State(
                    subject=email_msg.subject,
                    body=body,
                    classification=None,
                    summary=None,
                )

                # Invoking langgraph
                ai_result = await graph.ainvoke(initial_state)  # type: ignore
                classification: str = ai_result["classification"]
                summary: str = ai_result["summary"]

                # Writing results from langgraph to PostgreSQL database
                db_msg = await db.update_message(
                    message_id=db_msg.id,
                    status="processed",
                    classification=classification,
                    summary=summary,
                    error_message=None,
                )

                # Sending classification message to Kafka topic
                cls_msg = ClassificationResult(
                    recipients=email_msg.recipients,
                    subject=email_msg.subject,
                    classification=classification,
                )
                await producer.send(
                    KAFKA_CLASSIFICATION_TOPIC,
                    cls_msg,
                    key=classification.encode() if classification else email_msg.subject.encode(),
                )

                # Sending summarization message to Kafka topic
                sum_msg = SummarizationResult(
                    recipients=email_msg.recipients,
                    subject=email_msg.subject,
                    summary=summary,
                )
                await producer.send(
                    KAFKA_SUMMARIZATION_TOPIC,
                    sum_msg,
                    key=classification.encode() if classification else email_msg.subject.encode(),
                )

                await consumer.commit()

            except Exception as e:
                logger.exception(f"Error processing input message: {e}")
                if db_msg is not None:
                    await db.update_message(
                        message_id=db_msg.id,
                        status="failed",
                        classification=None,
                        summary=None,
                        error_message=str(e),
                    )
    finally:
        await consumer.stop()


async def consume_classification_results(consumer: Consumer):
    try:
        async for msg in consumer:
            try:
                logger.info(f"Got classification result: {msg.value}")
                await consumer.commit()
            except Exception as e:
                logger.exception(f"Error processing classification result: {e}")
    finally:
        await consumer.stop()


async def consume_summarization_results(consumer: Consumer):
    try:
        async for msg in consumer:
            try:
                logger.info(f"Got summarization result: {msg.value}")
                await consumer.commit()
            except Exception as e:
                logger.exception(f"Error processing summarization result: {e}")
    finally:
        await consumer.stop()


async def main():
    postgres_url = create_postgres()
    kafka_bootstrap = create_kafka()

    db = Database(url=postgres_url)
    await db.connect()

    producer = Producer(kafka_bootstrap)
    await producer.start()

    for message in messages:
        await producer.send(topic=KAFKA_INPUT_TOPIC, message=message, key=message.subject.encode())

    input_consumer = Consumer(
        topic=KAFKA_INPUT_TOPIC,
        bootstrap_servers=kafka_bootstrap,
        group_id=KAFKA_INPUT_CONSUMER_GROUP_ID,
    )
    classification_consumer = Consumer(
        topic=KAFKA_CLASSIFICATION_TOPIC,
        bootstrap_servers=kafka_bootstrap,
        group_id=KAFKA_CLASSIFICATION_CONSUMER_GROUP_ID,
    )
    summarization_consumer = Consumer(
        topic=KAFKA_SUMMARIZATION_TOPIC,
        bootstrap_servers=kafka_bootstrap,
        group_id=KAFKA_SUMMARIZATION_CONSUMER_GROUP_ID,
    )

    await input_consumer.start()
    await classification_consumer.start()
    await summarization_consumer.start()

    try:
        # Working demonstration
        await asyncio.gather(
            process_input_messages(input_consumer, producer, db),
            consume_classification_results(classification_consumer),
            consume_summarization_results(summarization_consumer),
        )
    finally:
        await producer.stop()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
