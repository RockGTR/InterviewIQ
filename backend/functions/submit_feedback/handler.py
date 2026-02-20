"""
Submit Feedback Lambda Handler
================================

POST /sessions/{sessionId}/feedback — Stores interviewee feedback.

Accepts corrections to AI findings and selected interview questions
from the interviewee's pre-interview review.

Request Body:
    {
        "corrections": [{"field": "industry", "original": "SaaS", "corrected": "VPP"}],
        "selectedQuestions": ["q1", "q3", "q7"],
        "notes": "Optional free-form notes"
    }

Response:
    200: {"status": "FEEDBACK_RECEIVED", ...}
"""

import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from response_helpers import success_response, error_response, parse_body
from dynamo_service import DynamoDBService


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for storing interviewee feedback.

    Args:
        event: API Gateway Lambda proxy event with sessionId path param.
        context: Lambda context object.

    Returns:
        dict: API Gateway response confirming feedback stored.
    """
    session_id = event.get("pathParameters", {}).get("sessionId")
    if not session_id:
        return error_response("sessionId path parameter is required", 400)

    try:
        body = parse_body(event)
    except (ValueError, Exception) as e:
        return error_response(f"Invalid request body: {e}", 400)

    corrections = body.get("corrections", [])
    selected_questions = body.get("selectedQuestions", [])
    notes = body.get("notes", "")

    try:
        db = DynamoDBService()
        session = db.get_session(session_id)
        if not session:
            return error_response(f"Session {session_id} not found", 404)

        updated = db.store_feedback(
            session_id=session_id,
            created_at=session["createdAt"],
            corrections=corrections,
            selected_questions=selected_questions,
            notes=notes,
        )

        result = {
            "sessionId": session_id,
            "status": "FEEDBACK_RECEIVED",
            "corrections_count": len(corrections),
            "selected_questions_count": len(selected_questions),
        }

        logger.info("Feedback stored for session %s: %d corrections, %d questions",
                     session_id, len(corrections), len(selected_questions))
        return success_response(result)

    except Exception as e:
        logger.error("Failed to store feedback for %s: %s", session_id, e)
        return error_response("Failed to store feedback", 500, str(e))
