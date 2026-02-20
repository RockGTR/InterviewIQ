"""
Scrape Company Lambda Handler
===============================

POST /scrape — Triggers web scraping for company intelligence.

Scrapes public company information from web sources and stores
the results in S3 and DynamoDB.

Request Body:
    {
        "sessionId": "uuid",
        "companyName": "GridFlex Energy",
        "companyUrl": "https://gridflex.com" (optional)
    }

Response:
    200: {"scraped_data": {...}, "pages_count": 3}
    400: {"error": "sessionId and companyName are required"}
"""

import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from shared.response_helpers import success_response, error_response, parse_body
from shared.scraper_service import ScraperService
from shared.s3_service import S3Service
from shared.dynamo_service import DynamoDBService


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for web scraping.

    Scrapes company info, stores raw data in S3, and updates the session.

    Args:
        event: API Gateway Lambda proxy event.
        context: Lambda context object.

    Returns:
        dict: API Gateway response with scraped data summary.
    """
    try:
        body = parse_body(event)
    except (ValueError, Exception) as e:
        return error_response(f"Invalid request body: {e}", 400)

    session_id = body.get("sessionId")
    company_name = body.get("companyName")
    if not session_id or not company_name:
        return error_response("sessionId and companyName are required", 400)

    company_url = body.get("companyUrl", "")

    try:
        # Scrape company data
        scraper = ScraperService()
        scraped_data = scraper.scrape_company(company_name, company_url)

        # Store raw scraped data in S3
        s3 = S3Service()
        s3.upload_document(
            file_bytes=json.dumps(scraped_data, indent=2).encode("utf-8"),
            session_id=session_id,
            filename="scraped_data.json",
            prefix="scraped",
            content_type="application/json",
        )

        # Update session with scraped data summary
        db = DynamoDBService()
        session = db.get_session(session_id)
        if session:
            db.update_session(session_id, session["createdAt"], {
                "scrapedData": scraped_data.get("summary", {}),
                "status": "SCRAPING_COMPLETE",
            })

        result = {
            "sessionId": session_id,
            "source": scraped_data.get("source", "unknown"),
            "pages_count": len(scraped_data.get("pages", [])),
            "summary": scraped_data.get("summary", {}),
        }

        logger.info("Scraping complete for %s (%s)", company_name, scraped_data.get("source"))
        return success_response(result)

    except Exception as e:
        logger.error("Scraping failed for %s: %s", company_name, e)
        return error_response("Scraping failed", 500, str(e))
