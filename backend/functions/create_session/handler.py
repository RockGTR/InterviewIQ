"""
Create Session Lambda Handler
==============================

POST /sessions — Creates a new interview preparation session.

Accepts a company name and optional URL, creates a new session record
in DynamoDB, and returns the session details including the generated ID.

Request Body:
    {
        "companyName": "GridFlex Energy",
        "companyUrl": "https://gridflex.com" (optional)
    }

Response:
    201: {"sessionId": "uuid", "status": "CREATED", ...}
    400: {"error": "companyName is required"}
"""

import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from shared.response_helpers import success_response, error_response, parse_body
from shared.dynamo_service import DynamoDBService


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for creating a new interview session.

    Parses the company name and URL from the request body,
    creates a session in DynamoDB, and returns the session record.

    Args:
        event: API Gateway Lambda proxy event.
        context: Lambda context object.

    Returns:
        dict: API Gateway response with created session data.
    """
    try:
        body = parse_body(event)
    except (ValueError, Exception) as e:
        return error_response(f"Invalid request body: {e}", 400)

    company_name = body.get("companyName")
    if not company_name:
        return error_response("companyName is required", 400)

    company_url = body.get("companyUrl", "")

    try:
        db = DynamoDBService()
        session = db.create_session(
            company_name=company_name,
            company_url=company_url,
            metadata=body.get("metadata", {}),
        )

        logger.info("Created session %s for %s", session["sessionId"], company_name)
        response = success_response(session, 201)
        # Add sessionId at top level for Step Functions to extract
        response["sessionId"] = session["sessionId"]
        return response

    except Exception as e:
        logger.error("Failed to create session: %s", e)
        return error_response("Failed to create session", 500, str(e))
