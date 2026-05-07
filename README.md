Possible Improvements:

1. Dead Letter Queue (DLQ)
Instead of infinite retries upon an error, after N failed attempts, the message is written to a separate Kafka topic.
2. Production configuration
Currently TestContainers spins up Docker containers directly in main.py. In a production, KAFKA_BOOTSTRAP_SERVERS and DATABASE_URL should be injected via environment variables, and containers.py should use only in the test layer.


Explanation of why a sequential approach is used instead of a parallel one:
Sequential LLM usage for token reduction
Summarization runs first, and the resulting summary is passed to the classifier instead of the full email body. Since the summary is significantly shorter, this reduces the number of tokens sent to the LLM on every classification request, lowering both cost and latency.