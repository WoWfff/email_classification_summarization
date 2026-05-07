import logging

from testcontainers.kafka import KafkaContainer  # type: ignore
from testcontainers.postgres import PostgresContainer  # type: ignore

from app.config import POSTGRES_DB, POSTGRESQL_DRIVER

logger = logging.getLogger(__name__)


def create_kafka() -> tuple[str, KafkaContainer]:
    """Create Kafka container

    Returns:
        tuple[str, KafkaContainer]: bootstrap_server, KafkaContainer
    """
    try:
        kafka = KafkaContainer()
        kafka.start()
        logger.info("Kafka container created.")

        return kafka.get_bootstrap_server(), kafka

    except Exception:
        logger.error("Error while creating Kafka container.")
        raise


def create_postgres() -> tuple[str, PostgresContainer]:
    """Create PostgreSQL container

    Returns:
        tuple[str, PostgresContainer]: PostgreSQL connection url, PostgresContainer
    """
    try:
        postgres = PostgresContainer(
            driver=POSTGRESQL_DRIVER,
            dbname=POSTGRES_DB,
        )

        postgres.start()
        logger.info("Postgres container created.")

        return postgres.get_connection_url(), postgres

    except Exception:
        logger.error("Error while creating Postgres container.")
        raise
