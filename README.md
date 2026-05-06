Possible Improvements:

1. Dead Letter Queue (DLQ)
Instead of infinite retries upon an error, after N failed attempts, the message is written to a separate Kafka topic.