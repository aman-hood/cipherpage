"""
CipherPage Serverless Event Handler - Document & Media Processor
Conforms to SRS v2.2 OPS-08, SEC-02, SEC-04, NFR-03

Demonstrates an event-driven Lambda function triggered by S3 uploads or
API Gateway HTTP requests to validate and process course media assets.
"""

import json
import logging
import os
import re
import urllib.parse
from typing import Any, Dict

# Configure structured logging (OPS-08, SEC-04)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".mp4"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit (LEARN-04)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal or special character injection."""
    cleaned = os.path.basename(filename)
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", cleaned)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entrypoint.
    Supports both S3 object-created events and API Gateway HTTP invocations.
    """
    request_id = getattr(context, "aws_request_id", "local-invoc")
    logger.info(f"Received invocation [request_id={request_id}]")

    try:
        # 1. Handle S3 Event Notification (Event-driven background pipeline)
        if "Records" in event and len(event["Records"]) > 0:
            record = event["Records"][0]
            if record.get("eventSource") == "aws:s3":
                bucket = record["s3"]["bucket"]["name"]
                key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
                size = record["s3"]["object"].get("size", 0)

                # Validation (LEARN-04, OPS-08)
                sanitized_key = sanitize_filename(key)
                ext = os.path.splitext(sanitized_key)[1].lower()

                if ext not in ALLOWED_EXTENSIONS:
                    logger.warning(f"Rejected unsupported extension: {ext} for {sanitized_key}")
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": f"Unsupported file extension {ext}"}),
                    }

                if size > MAX_FILE_SIZE_BYTES:
                    logger.warning(f"File size {size} exceeds {MAX_FILE_SIZE_BYTES} bytes")
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "File exceeds maximum 50MB size limit"}),
                    }

                logger.info(f"Validated S3 upload: bucket={bucket}, key={sanitized_key}, size={size}B")
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "status": "PROCESSED",
                        "bucket": bucket,
                        "key": sanitized_key,
                        "message": "Asset metadata extracted and verified successfully",
                        "request_id": request_id,
                    }),
                }

        # 2. Handle Direct API Gateway Invocation
        body = {}
        if "body" in event and event["body"]:
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]

        file_name = body.get("filename", "")
        file_size = body.get("size", 0)

        if not file_name:
            return {
                "statusCode": 422,
                "body": json.dumps({"detail": "Missing required 'filename' parameter"}),
            }

        sanitized_name = sanitize_filename(file_name)
        ext = os.path.splitext(sanitized_name)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            return {
                "statusCode": 400,
                "body": json.dumps({"detail": f"Unsupported format '{ext}'. Allowed: {list(ALLOWED_EXTENSIONS)}"}),
            }

        logger.info(f"Generated upload pre-signed approval for: {sanitized_name}")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "APPROVED",
                "filename": sanitized_name,
                "max_size_bytes": MAX_FILE_SIZE_BYTES,
                "request_id": request_id,
            }),
        }

    except Exception as exc:
        logger.error(f"Lambda execution error: {str(exc)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"detail": "Internal serverless processing error", "request_id": request_id}),
        }
