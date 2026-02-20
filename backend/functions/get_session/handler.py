"""
Get Session Lambda Handler
===========================

GET /sessions/{sessionId} — Retrieves interview session data.

Returns the full session record including company data, generated
briefs, interviewee packet, and any submitted feedback.

Response:
    200: {session data}
    404: {"error": "Session not found"}
"""

import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from response_helpers import success_response, error_response
from dynamo_service import DynamoDBService


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for retrieving a session by ID.

    Args:
        event: API Gateway Lambda proxy event with sessionId path param.
        context: Lambda context object.

    Returns:
        dict: API Gateway response with session data or 404.
    """
    session_id = event.get("pathParameters", {}).get("sessionId")
    if not session_id:
        return error_response("sessionId path parameter is required", 400)

    try:
        db = DynamoDBService()
        session = db.get_session(session_id)

        if not session:
            return error_response(f"Session {session_id} not found", 404)

        logger.info("Retrieved session %s (status: %s)", session_id, session.get("status"))
        return success_response(session)

    except Exception as e:
        logger.error("Failed to get session %s: %s", session_id, e)
        return error_response("Failed to retrieve session", 500, str(e))
