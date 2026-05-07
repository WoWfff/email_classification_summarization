## Running with Docker

Copy `.env.example` to `.env` and fill in the values:
```bash
cp .env.example .env
```

Build the image:
```bash
docker build -t email-processor .
```

Run the container:
```bash
docker run --rm \
  --env-file .env \
  email-processor
```

> **Note:** The service uses TestContainers which requires access to Docker socket.
> When running via `docker run`, mount the socket explicitly:
> ```bash
> docker run --rm \
>   --env-file .env \
>   -v /var/run/docker.sock:/var/run/docker.sock \
>   email-processor
> ```
> For local development without Docker, run directly:
> ```bash
> uv sync
> uv run main.py
> ```

## Overview

A Python service that consumes email messages from Kafka, processes them through
a LangGraph AI agent (summarization + classification), stores results in PostgreSQL,
and publishes processing results to separate Kafka topics.

## Stack

* Python
* Kafka
* LangChain
* LangGraph
* Google Gemini
* PostgreSQL
* SQLAlchemy
* asyncpg
* Pydantic
* TestContainers
* Docker

## How it works

1. A message with email headers and a path to the body blob is consumed from the input Kafka topic
2. The blob body is read from the filesystem (BlobStorage interface)
3. The message is saved to PostgreSQL with status `pending`
4. The LangGraph agent runs two steps sequentially: summarize → classify
5. Results are written back to PostgreSQL with status `processed`
6. Classification and summarization results are published to separate Kafka topics
7. Kafka offset is committed after successful processing

## Multi-instance deployment

Consumer group is configured so that multiple instances can consume from the same
topic in parallel without processing the same partition twice.

Idempotency is ensured via a unique `message_id` constraint in the database and
`ON CONFLICT DO NOTHING` on insert — if the same message is delivered again after
a crash, the duplicate is detected and skipped without re-invoking the LLM.

## Possible Improvements

* Retry policy and DLQ
Failed messages are currently marked as failed and their Kafka offsets are committed, so they are not retried.
A better approach is to add bounded retries with backoff for transient failures and send permanently failed messages to a dedicated DLQ topic.

* Transactional consistency between DB and Kafka
The current flow can write to PostgreSQL and fail before producing result events, or produce one event and fail before the second one.
This can be improved with an outbox pattern or another explicit recovery mechanism to keep DB state and Kafka outputs consistent.

* Production configuration
Currently TestContainers spins up Docker containers directly in main.py. In a production, KAFKA_BOOTSTRAP_SERVERS and DATABASE_URL should be injected via environment variables, and containers.py should use only in the test layer.


## Explanations of code

* Explanation of why a sequential approach is used instead of a parallel one:
Summarization runs first, and the resulting summary is passed to the classifier instead of the full email body. Since the summary is significantly shorter, this reduces the number of tokens sent to the LLM on every classification request, lowering both cost and latency.

* Idempotent processing + message_id
Each input message carries an explicit message_id. A unique constraint on message_id in the database ensures that if the same message is delivered again, the second processing attempt will detect the existing record and skip re-processing, preventing duplicate business entities.
What this solves: if an instance crashes after writing to the database but before committing the offset, the next instance will not create a duplicate record.
What this does not solve (possible improvement): desynchronization between the database and Kafka is still possible — for example, if the instance crashes after the database write but before publishing to the output Kafka topics.