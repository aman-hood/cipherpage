"""
CipherPage Security Headers & Request Protection Middleware
Conforms to SRS v2.2 SEC-02, SEC-05, NFR-05
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# 10 Megabytes maximum payload limit (SEC-02, LEARN-04)
MAX_REQUEST_SIZE_BYTES = 10 * 1024 * 1024

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check request payload size limit (SEC-02)
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_REQUEST_SIZE_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request payload exceeds maximum allowed size limit (10MB)"}
                    )
            except ValueError:
                pass

        # Execute request handler
        response = await call_next(request)

        # Inject OWASP Recommended Security Response Headers (SEC-02)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

        return response
