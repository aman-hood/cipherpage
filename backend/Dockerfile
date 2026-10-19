# Multi-Stage Production Dockerfile for CipherPage FastAPI Backend
# Conforms to SRS v2.2 OPS-01, OPS-04, SEC-06

# ---------------------------------------------------------
# Stage 1: Base Environment
# ---------------------------------------------------------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---------------------------------------------------------
# Stage 2: Build Dependencies
# ---------------------------------------------------------
FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---------------------------------------------------------
# Stage 3: Development Target (Used for local live-reload)
# ---------------------------------------------------------
FROM base AS development

COPY --from=builder /install /usr/local
COPY . /app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# The trusted Celery grading worker launches short-lived, isolated runner
# containers through the Docker Engine. The API and frontend do not need this CLI.
FROM development AS runner

RUN apt-get update && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------
# Stage 4: Production Target (Hardened, non-root user)
# ---------------------------------------------------------
FROM base AS production

# Create isolated, unprivileged system user
RUN groupadd -g 10001 ciphergroup && \
    useradd -u 10001 -g ciphergroup -s /bin/false -m cipheruser

# Copy installed python libraries from builder
COPY --from=builder /install /usr/local

# Copy application source code with restricted permissions
COPY --chown=cipheruser:ciphergroup . /app

# Switch to non-root user
USER cipheruser

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
