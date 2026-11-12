# ==============================================================================
# CLEARLY Backend — Production Dockerfile
# Multi-stage lightweight build for Sovereign FastAPI Core API
# ==============================================================================

FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final production stage
FROM python:3.11-slim as runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

COPY --from=builder /install /usr/local
COPY . /app

# Non-root user for security
RUN useradd -m -u 1000 clearlyuser && \
    mkdir -p /app/storage/documents && \
    chown -R clearlyuser:clearlyuser /app
USER clearlyuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

