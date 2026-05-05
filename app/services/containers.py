import logging

from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer

from app.config import POSTGRES_DB, POSTGRESQL_DRIVER

logger = logging.getLogger(__name__)


def create_kafka() -> str:
    try:
        kafka = KafkaContainer()

        kafka.start()
        logger.info("Kafka container created.")

        return kafka.get_bootstrap_server()

    except Exception:
        logger.error("Error while creating Kafka container.")
        raise


def create_postgres() -> str:
    try:
        postgres = PostgresContainer(
            driver=POSTGRESQL_DRIVER,
            dbname=POSTGRES_DB,
        )

        postgres.start()
        logger.info("Postgres container created.")

        return postgres.get_connection_url()

    except Exception:
        logger.error("Error while creating Postgres container.")
        raise
