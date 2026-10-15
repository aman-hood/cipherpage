"""
CipherPage Structured Logging & Secret Redaction Module
Conforms to SRS v2.2 SEC-04, NFR-06
"""

import logging
import re
import sys
from typing import Any

# Regex patterns for sensitive data redaction (SEC-04)
SECRET_PATTERNS = [
    # JWT Bearer tokens
    (re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]+", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    # AWS Access Keys
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_AWS_KEY]"),
    # Generic API Keys (e.g. sk-..., ai-...)
    (re.compile(r"(?:sk|sb|ai)-[a-zA-Z0-9_\-]{20,}"), "[REDACTED_API_KEY]"),
    # Passwords in JSON/query parameters
    (re.compile(r'("password"\s*:\s*)"[^"]+"', re.IGNORECASE), r'\1"[REDACTED_PASSWORD]"'),
    (re.compile(r'(password=)[^&\s]+', re.IGNORECASE), r'\1[REDACTED_PASSWORD]'),
    # Database DSN passwords (postgresql://user:pass@host:port/db)
    (re.compile(r"://([^:]+):([^@]+)@", re.IGNORECASE), r"://\1:[REDACTED_PASS]@"),
]

def redact_sensitive_data(message: str) -> str:
    """Scan and replace sensitive secrets, passwords, and tokens with redaction placeholders."""
    if not isinstance(message, str):
        message = str(message)
    for pattern, replacement in SECRET_PATTERNS:
        message = pattern.sub(replacement, message)
    return message


class SecretRedactingFormatter(logging.Formatter):
    """Logging formatter that automatically redacts credentials before writing to console/file."""
    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return redact_sensitive_data(original)


def setup_logger(name: str = "cipherpage") -> logging.Logger:
    """Initialize structured and sanitized logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            SecretRedactingFormatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()
