from os import getenv

POSTGRESQL_DRIVER = "asyncpg"
POSTGRES_DB = getenv("POSTGRES_DB", "test_db")

KAFKA_INPUT_TOPIC = getenv("KAFKA_INPUT_TOPIC", "input-topic")
KAFKA_CONSUMER_GROUP_ID = "1234"
