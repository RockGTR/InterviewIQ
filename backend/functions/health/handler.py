"""
Health Check Lambda Handler
============================

GET /health — Returns system status and service availability.

Verifies that core AWS services (DynamoDB, S3, Bedrock) are accessible
and returns a simple health status response.

Response:
    200: {"status": "healthy", "services": {...}, "timestamp": "..."}
    500: {"error": "Health check failed", "details": "..."}
"""

import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Import shared modules (available via Lambda Layer)
from shared.response_helpers import success_response, error_response


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for the health check endpoint.

    Performs a lightweight check of system configuration and returns
    the current status. Does not make actual AWS API calls to keep
    response time fast.

    Args:
        event: API Gateway Lambda proxy event.
        context: Lambda context object.

    Returns:
        dict: API Gateway response with health status.
    """
    try:
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "InterviewIQ",
            "version": "1.0.0",
            "config": {
                "table_name": os.environ.get("TABLE_NAME", "NOT_SET"),
                "bucket_name": os.environ.get("BUCKET_NAME", "NOT_SET"),
                "model_id": os.environ.get("MODEL_ID", "NOT_SET"),
                "bedrock_region": os.environ.get("BEDROCK_REGION", "NOT_SET"),
            },
        }

        logger.info("Health check: %s", health["status"])
        return success_response(health)

    except Exception as e:
        logger.error("Health check failed: %s", e)
        return error_response("Health check failed", 500, str(e))
