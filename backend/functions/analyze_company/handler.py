"""
Analyze Company Lambda Handler
================================

POST /analyze — Runs NLP analysis on company text using Comprehend.

Detects entities, key phrases, and sentiment from the combined
scraped and parsed text for a session.

Request Body:
    {
        "sessionId": "uuid",
        "text": "raw text to analyze" (optional; auto-loads from session if omitted)
    }

Response:
    200: {"entities": [...], "key_phrases": [...], "sentiment": {...}}
"""

import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from shared.response_helpers import success_response, error_response, parse_body
from shared.comprehend_service import ComprehendService
from shared.dynamo_service import DynamoDBService
from shared.s3_service import S3Service


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for NLP analysis.

    Runs Comprehend entity/key-phrase/sentiment analysis on session text.

    Args:
        event: API Gateway Lambda proxy event.
        context: Lambda context object.

    Returns:
        dict: API Gateway response with NLP analysis results.
    """
    try:
        body = parse_body(event)
    except (ValueError, Exception) as e:
        return error_response(f"Invalid request body: {e}", 400)

    session_id = body.get("sessionId")
    if not session_id:
        return error_response("sessionId is required", 400)

    try:
        # Get text to analyze
        text = body.get("text", "")

        if not text:
            # Auto-load from session's scraped data
            s3 = S3Service()
            try:
                scraped_bytes = s3.get_document(f"scraped/{session_id}/scraped_data.json")
                scraped_data = json.loads(scraped_bytes)
                text = scraped_data.get("summary", {}).get("combined_content", "")
            except Exception:
                logger.warning("No scraped data found for session %s", session_id)

        if not text:
            return error_response("No text available for analysis. Scrape or provide text first.", 400)

        # Run NLP analysis
        nlp = ComprehendService()
        analysis = nlp.analyze_text(text)

        # Update session with analysis results
        db = DynamoDBService()
        session = db.get_session(session_id)
        if session:
            db.update_session(session_id, session["createdAt"], {
                "analysisResults": analysis,
                "status": "ANALYSIS_COMPLETE",
            })

        result = {
            "sessionId": session_id,
            "entities_count": len(analysis.get("entities", [])),
            "key_phrases_count": len(analysis.get("key_phrases", [])),
            "sentiment": analysis.get("sentiment", {}),
            "top_entities": analysis.get("entities", [])[:10],
            "top_key_phrases": analysis.get("key_phrases", [])[:10],
        }

        logger.info("Analysis complete: %d entities, %d phrases",
                     result["entities_count"], result["key_phrases_count"])
        return success_response(result)

    except Exception as e:
        logger.error("Analysis failed for session %s: %s", session_id, e)
        return error_response("Analysis failed", 500, str(e))
