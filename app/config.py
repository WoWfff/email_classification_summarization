from os import getenv

from dotenv import load_dotenv

load_dotenv()

POSTGRESQL_DRIVER = "asyncpg"
POSTGRES_DB = getenv("POSTGRES_DB", "test-db")

KAFKA_INPUT_TOPIC = getenv("KAFKA_INPUT_TOPIC", "input-topic")
KAFKA_CLASSIFICATION_TOPIC = getenv("KAFKA_CLASSIFICATION_TOPIC", "classification-topic")
KAFKA_SUMMARIZATION_TOPIC = getenv("KAFKA_SUMMARIZATION_TOPIC", "summarization-topic")
KAFKA_INPUT_CONSUMER_GROUP_ID = getenv("KAFKA_INPUT_CONSUMER_GROUP_ID", "input_group_id")
KAFKA_CLASSIFICATION_CONSUMER_GROUP_ID = getenv("KAFKA_CLASSIFICATION_CONSUMER_GROUP_ID", "classification_group_id")
KAFKA_SUMMARIZATION_CONSUMER_GROUP_ID = getenv("KAFKA_SUMMARIZATION_CONSUMER_GROUP_ID", "summarization_group_id")
