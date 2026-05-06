FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app/ ./app/
COPY main.py ./

RUN mkdir -p data/blobs

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "main.py"]