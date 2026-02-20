"""
Generate Brief Lambda Handler
===============================

POST /generate — Generates interview brief using Bedrock/Claude.

Takes scraped data, parsed documents, and NLP analysis to produce
a comprehensive interviewer brief and interviewee packet.

Request Body:
    {
        "sessionId": "uuid"
    }

Response:
    200: {"brief": {...}, "packet": {...}}
"""

import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from shared.response_helpers import success_response, error_response, parse_body
from shared.bedrock_service import BedrockService
from shared.dynamo_service import DynamoDBService
from shared.s3_service import S3Service


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for AI brief generation.

    Loads all session data, invokes Claude to generate the interviewer
    brief and interviewee packet, and stores results.

    Args:
        event: API Gateway Lambda proxy event.
        context: Lambda context object.

    Returns:
        dict: API Gateway response with generated brief and packet.
    """
    try:
        body = parse_body(event)
    except (ValueError, Exception) as e:
        return error_response(f"Invalid request body: {e}", 400)

    # Support both API Gateway (body.sessionId) and Step Functions (body.sessionResult.sessionId)
    session_id = body.get("sessionId")
    if not session_id:
        session_result = body.get("sessionResult", {})
        session_id = session_result.get("sessionId")
    if not session_id:
        return error_response("sessionId is required", 400)

    try:
        # Load session data
        db = DynamoDBService()
        session = db.get_session(session_id)
        if not session:
            return error_response(f"Session {session_id} not found", 404)

        scraped_data = session.get("scrapedData", {})
        parsed_docs = session.get("parsedDocuments", [])
        analysis = session.get("analysisResults", {})

        # Generate company profile
        bedrock = BedrockService()
        profile = bedrock.generate_company_profile(scraped_data, parsed_docs, analysis)

        # Generate interview questions
        questions = bedrock.generate_questions(profile, analysis)

        # Generate interviewer brief
        brief = bedrock.generate_interviewer_brief(profile, questions, analysis)

        # Generate interviewee packet
        packet = bedrock.generate_interviewee_packet(profile, questions)

        # Store in S3
        s3 = S3Service()
        s3.upload_document(
            file_bytes=json.dumps(brief, indent=2).encode("utf-8"),
            session_id=session_id,
            filename="interviewer_brief.json",
            prefix="briefs",
            content_type="application/json",
        )
        s3.upload_document(
            file_bytes=json.dumps(packet, indent=2).encode("utf-8"),
            session_id=session_id,
            filename="interviewee_packet.json",
            prefix="packets",
            content_type="application/json",
        )

        # Update session
        db.update_session(session_id, session["createdAt"], {
            "interviewerBrief": brief,
            "intervieweePacket": packet,
            "status": "READY",
        })

        result = {
            "sessionId": session_id,
            "status": "READY",
            "brief_sections": list(brief.keys()),
            "questions_count": len(questions),
        }

        logger.info("Brief generated for session %s: %d questions", session_id, len(questions))
        return success_response(result)

    except Exception as e:
        logger.error("Brief generation failed for session %s: %s", session_id, e)
        return error_response("Brief generation failed", 500, str(e))
