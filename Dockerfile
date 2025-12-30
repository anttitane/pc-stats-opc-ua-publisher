# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md requirements.txt ./
COPY src/ ./src/
RUN pip install --no-cache-dir -e .

ENV OPCUA_ENDPOINT_HOST=0.0.0.0 \
    OPCUA_ENDPOINT_PORT=4840 \
    OPCUA_UPDATE_INTERVAL_SECONDS=2.0

CMD ["python", "-m", "pc_stats_publisher.main"]
