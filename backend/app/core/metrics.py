"""
CipherPage Prometheus Observability & Metrics Module
Conforms to SRS v2.2 OPS-09, NFR-06, AC-09
"""

import time
import re
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY
)

# ------------------------------------------------------------------------------
# 1. Prometheus Metric Definitions (OPS-09, NFR-06)
# ------------------------------------------------------------------------------

# HTTP Traffic & Latency Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "cipherpage_http_requests_total",
    "Total count of HTTP requests processed by CipherPage API",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "cipherpage_http_request_duration_seconds",
    "HTTP request latency in seconds across percentiles",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ACTIVE_REQUESTS = Gauge(
    "cipherpage_active_requests",
    "Number of currently executing HTTP requests in flight"
)

# Coding Arena & Runner Metrics (NFR-06, CODE-05)
CODE_SUBMISSIONS_TOTAL = Counter(
    "cipherpage_code_submissions_total",
    "Total submissions graded by isolated runner",
    ["language", "verdict"]
)

RUNNER_EXECUTION_DURATION_SECONDS = Histogram(
    "cipherpage_runner_execution_duration_seconds",
    "Execution duration of student code inside isolated runner",
    ["language"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0]
)

# GenAI Coding Mentor & RAG Metrics (NFR-06, AI-07, RAG-04)
AI_MENTOR_REQUESTS_TOTAL = Counter(
    "cipherpage_ai_mentor_requests_total",
    "Total requests to GenAI Coding Mentor",
    ["mode", "status"]
)

RAG_QUERIES_TOTAL = Counter(
    "cipherpage_rag_queries_total",
    "Total queries to RAG Learning Assistant",
    ["course_id", "sources_found"]
)

# System & Subsystem Health Status (NFR-04, NFR-06)
DATABASE_HEALTH_STATUS = Gauge(
    "cipherpage_database_health_status",
    "PostgreSQL connection health status (1 = healthy, 0 = degraded)"
)

REDIS_HEALTH_STATUS = Gauge(
    "cipherpage_redis_health_status",
    "Redis cache and Celery broker connection health status (1 = healthy, 0 = degraded)"
)

# Initialize health gauges to healthy
DATABASE_HEALTH_STATUS.set(1)
REDIS_HEALTH_STATUS.set(1)


# ------------------------------------------------------------------------------
# 2. Path Normalization (Prevents Label Cardinality Explosion)
# ------------------------------------------------------------------------------
def normalize_endpoint(path: str) -> str:
    """
    Replace dynamic IDs in URL paths with placeholders to avoid
    generating infinite unique Prometheus labels.
    Example: /api/v1/challenges/486/submit -> /api/v1/challenges/{id}/submit
    """
    # Replace numeric IDs
    path = re.sub(r"/\d+(?=/|$)", "/{id}", path)
    # Replace UUIDs
    path = re.sub(r"/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}(?=/|$)", "/{uuid}", path)
    return path


# ------------------------------------------------------------------------------
# 3. FastAPI Prometheus Middleware
# ------------------------------------------------------------------------------
class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Ignore metrics endpoint itself to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        method = request.method
        normalized_path = normalize_endpoint(request.url.path)

        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            return response
        except Exception:
            status_code = "500"
            raise
        finally:
            duration = time.time() - start_time
            ACTIVE_REQUESTS.dec()

            # Record metrics
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=normalized_path,
                status_code=status_code
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=normalized_path
            ).observe(duration)


# ------------------------------------------------------------------------------
# 4. Metrics Export Endpoint Handler
# ------------------------------------------------------------------------------
def metrics_response() -> Response:
    """Generate latest Prometheus exposition text format (AC-09: No secrets exposed)."""
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
