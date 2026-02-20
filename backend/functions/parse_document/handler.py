"""
Parse Document Lambda Handler
===============================

POST /parse — Processes uploaded documents for text extraction.

Accepts a file (base64 encoded) or S3 key reference, extracts text
using python-docx (.docx) or Textract (PDF/images), and stores results.

Request Body:
    {
        "sessionId": "uuid",
        "filename": "company_overview.docx",
        "fileContent": "base64-encoded-content" (optional),
        "s3Key": "uploads/uuid/file.docx" (optional, alternative to fileContent)
    }

Response:
    200: {"text_length": 5000, "method": "python-docx", ...}
"""

import os
import base64
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from shared.response_helpers import success_response, error_response, parse_body
from shared.textract_service import TextractService
from shared.s3_service import S3Service
from shared.dynamo_service import DynamoDBService


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for document parsing.

    Routes .docx files to python-docx and PDF/images to Textract.

    Args:
        event: API Gateway Lambda proxy event.
        context: Lambda context object.

    Returns:
        dict: API Gateway response with extracted text and metadata.
    """
    try:
        body = parse_body(event)
    except (ValueError, Exception) as e:
        return error_response(f"Invalid request body: {e}", 400)

    session_id = body.get("sessionId")
    filename = body.get("filename")
    if not session_id or not filename:
        return error_response("sessionId and filename are required", 400)

    try:
        textract = TextractService()

        # Get file bytes from either base64 content or S3
        s3_key = body.get("s3Key")
        file_content = body.get("fileContent")

        if file_content:
            file_bytes = base64.b64decode(file_content)
        elif s3_key:
            s3 = S3Service()
            file_bytes = s3.get_document(s3_key)
        else:
            return error_response("Either fileContent or s3Key is required", 400)

        # Process the document
        result = textract.upload_and_process(file_bytes, filename, session_id)

        # Update session with parsed document info
        db = DynamoDBService()
        session = db.get_session(session_id)
        if session:
            parsed_docs = session.get("parsedDocuments", [])
            parsed_docs.append({
                "filename": filename,
                "method": result.get("method"),
                "text_length": len(result.get("text", "")),
                "s3_key": result.get("s3_key"),
            })
            db.update_session(session_id, session["createdAt"], {
                "parsedDocuments": parsed_docs,
            })

        response = {
            "sessionId": session_id,
            "filename": filename,
            "method": result.get("method"),
            "text_length": len(result.get("text", "")),
            "text_preview": result.get("text", "")[:500],
            "s3_key": result.get("s3_key"),
        }

        logger.info("Parsed %s via %s: %d chars", filename, result.get("method"), len(result.get("text", "")))
        return success_response(response)

    except Exception as e:
        logger.error("Document parsing failed for %s: %s", filename, e)
        return error_response("Document parsing failed", 500, str(e))
