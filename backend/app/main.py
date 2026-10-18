from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, courses, lectures, enrollments, payments, submissions, progress, challenges, gamification, notifications, admin, ai
from app.core.metrics import (
    PrometheusMiddleware,
    metrics_response,
    DATABASE_HEALTH_STATUS,
    REDIS_HEALTH_STATUS
)
from sqlalchemy import text
from app.database.session import SessionLocal

from app.core.security_headers import SecurityHeadersMiddleware
from app.core.rate_limiter import RateLimitingMiddleware

app = FastAPI(title="CipherPage API", version="1.1.0")

# Security Response Headers & Payload Size Limits (SEC-02, SEC-05)
app.add_middleware(SecurityHeadersMiddleware)

# Token Bucket Rate Limiting (SEC-02, CODE-03, AI-05)
app.add_middleware(RateLimitingMiddleware)

from app.core.config import settings
import redis

# Prometheus Observability Middleware (OPS-09, NFR-06)
app.add_middleware(PrometheusMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # API authentication uses explicit Bearer tokens; no cross-site cookies are issued.
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(lectures.router, prefix="/api/v1")
app.include_router(enrollments.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(submissions.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")
app.include_router(challenges.router, prefix="/api/v1")
app.include_router(gamification.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the CipherPage API"}

@app.get("/health")
def health_check():
    """
    Subsystem health probe checking Database & Redis connectivity (NFR-04, NFR-06).
    Updates Prometheus health gauges in real time.
    """
    db_status = "healthy"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        DATABASE_HEALTH_STATUS.set(1)
    except Exception:
        db_status = "degraded"
        DATABASE_HEALTH_STATUS.set(0)

    redis_status = "healthy"
    try:
        r = redis.from_url(settings.REDIS_URL, socket_timeout=1.0)
        r.ping()
        REDIS_HEALTH_STATUS.set(1)
    except Exception:
        redis_status = "degraded"
        REDIS_HEALTH_STATUS.set(0)

    # Return overall health
    is_healthy = (db_status == "healthy") and (redis_status == "healthy")
    return {
        "status": "ok" if is_healthy else "degraded",
        "subsystems": {
            "database": db_status,
            "redis": redis_status,
            "api": "healthy"
        },
        "version": settings.VERSION
    }

@app.get("/metrics")
def get_metrics():
    """Expose Prometheus metrics for scraping (OPS-09, AC-09)."""
    return metrics_response()
