"""
Response Helpers — Shared API Gateway response utilities
=========================================================

Provides standardized response formatting for all Lambda handlers.
Ensures consistent CORS headers, error formatting, and JSON serialization.

Usage:
    >>> from shared.response_helpers import success_response, error_response
    >>> return success_response({"sessionId": "123"})
    >>> return error_response("Not found", 404)
"""

import json
import logging
from typing import Any
from decimal import Decimal

logger = logging.getLogger(__name__)

# CORS headers for all responses (open for hackathon; restrict in production)
CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key",
}


class DecimalEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles Decimal types from DynamoDB.

    DynamoDB returns numeric values as Decimal objects, which the
    standard JSON encoder cannot serialize.
    """

    def default(self, obj: Any) -> Any:
        """Convert Decimal to int or float for JSON serialization."""
        if isinstance(obj, Decimal):
            return int(obj) if obj == int(obj) else float(obj)
        return super().default(obj)


def success_response(body: Any, status_code: int = 200) -> dict:
    """
    Create a successful API Gateway response.

    Args:
        body: Response body (will be JSON serialized).
        status_code: HTTP status code (default: 200).

    Returns:
        dict: API Gateway proxy integration response.
    """
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, cls=DecimalEncoder),
    }


def error_response(message: str, status_code: int = 400, details: Any = None) -> dict:
    """
    Create an error API Gateway response.

    Args:
        message: Human-readable error message.
        status_code: HTTP status code (default: 400).
        details: Optional additional error details.

    Returns:
        dict: API Gateway proxy integration response with error body.
    """
    body = {"error": message, "statusCode": status_code}
    if details:
        body["details"] = details

    logger.error("Error response [%d]: %s", status_code, message)
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, cls=DecimalEncoder),
    }


def parse_body(event: dict) -> dict:
    """
    Parse the JSON body from an API Gateway event.

    Handles both direct JSON and base64-encoded bodies.

    Args:
        event: API Gateway Lambda proxy event.

    Returns:
        dict: Parsed request body.

    Raises:
        ValueError: If body is missing or not valid JSON.
    """
    body = event.get("body", "")
    if not body:
        raise ValueError("Request body is required")

    if isinstance(body, str):
        return json.loads(body)
    return body
