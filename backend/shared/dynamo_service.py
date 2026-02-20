"""
DynamoDB Service — Interview Session Data Operations
=====================================================

Provides CRUD operations for managing interview preparation sessions
in Amazon DynamoDB. Each session represents a single interview preparation
workflow from company input through brief generation and feedback.

Table Schema:
    - Partition Key: sessionId (String) — UUID for each session
    - Sort Key: createdAt (String) — ISO 8601 timestamp
    - GSI: StatusIndex (status + createdAt) — query by session state

Session Lifecycle:
    CREATED → SCRAPING → ANALYZING → GENERATING → READY → FEEDBACK_RECEIVED → COMPLETE

Usage:
    >>> from shared.dynamo_service import DynamoDBService
    >>> db = DynamoDBService()
    >>> session = db.create_session("GridFlex Energy", "https://gridflex.com")
    >>> db.get_session(session["sessionId"])
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DynamoDBService:
    """
    Service class for DynamoDB interview session operations.

    Encapsulates all DynamoDB interactions for the InterviewIQ system,
    providing a clean interface for session lifecycle management.

    Attributes:
        table_name (str): DynamoDB table name from environment.
        table: boto3 DynamoDB Table resource.
    """

    def __init__(self, table_name: Optional[str] = None):
        """
        Initialize DynamoDB service with table reference.

        Args:
            table_name: Override table name. Defaults to TABLE_NAME env var.
        """
        self.table_name = table_name or os.environ.get("TABLE_NAME", "interview-iq-sessions")
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(self.table_name)
        logger.info("DynamoDBService initialized with table: %s", self.table_name)

    def create_session(
        self,
        company_name: str,
        company_url: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a new interview preparation session.

        Generates a unique session ID and initializes the session record
        with the provided company details and a CREATED status.

        Args:
            company_name: Name of the target company for the interview.
            company_url: Optional URL of the company website.
            metadata: Optional additional metadata to store.

        Returns:
            dict: The created session record including sessionId and createdAt.

        Raises:
            ClientError: If DynamoDB put operation fails.
        """
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        item = {
            "sessionId": session_id,
            "createdAt": now,
            "updatedAt": now,
            "status": "CREATED",
            "companyName": company_name,
            "companyUrl": company_url or "",
            "scrapedData": {},
            "parsedDocuments": [],
            "analysisResults": {},
            "interviewerBrief": {},
            "intervieweePacket": {},
            "feedback": {},
            "metadata": metadata or {},
        }

        self.table.put_item(Item=item)
        logger.info("Created session %s for company: %s", session_id, company_name)
        return item

    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Retrieve a session by its ID.

        Fetches the most recent record for the given session ID.

        Args:
            session_id: The unique session identifier.

        Returns:
            dict or None: The session record, or None if not found.

        Raises:
            ClientError: If DynamoDB query operation fails.
        """
        try:
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("sessionId").eq(session_id),
                ScanIndexForward=False,
                Limit=1,
            )
            items = response.get("Items", [])
            return items[0] if items else None
        except ClientError as e:
            logger.error("Failed to get session %s: %s", session_id, e)
            raise

    def update_session(self, session_id: str, created_at: str, updates: dict) -> dict:
        """
        Update specific fields of an existing session.

        Dynamically builds the update expression from the provided updates
        dictionary, setting each key-value pair on the session record.

        Args:
            session_id: The unique session identifier.
            created_at: The sort key (createdAt) for the session record.
            updates: Dictionary of field names and their new values.

        Returns:
            dict: The updated session attributes.

        Raises:
            ClientError: If DynamoDB update operation fails.
        """
        now = datetime.now(timezone.utc).isoformat()
        updates["updatedAt"] = now

        update_expr_parts = []
        expr_attr_values = {}
        expr_attr_names = {}

        for i, (key, value) in enumerate(updates.items()):
            attr_name = f"#attr{i}"
            attr_value = f":val{i}"
            update_expr_parts.append(f"{attr_name} = {attr_value}")
            expr_attr_names[attr_name] = key
            expr_attr_values[attr_value] = value

        response = self.table.update_item(
            Key={"sessionId": session_id, "createdAt": created_at},
            UpdateExpression="SET " + ", ".join(update_expr_parts),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="ALL_NEW",
        )
        logger.info("Updated session %s with fields: %s", session_id, list(updates.keys()))
        return response.get("Attributes", {})

    def store_feedback(
        self,
        session_id: str,
        created_at: str,
        corrections: list,
        selected_questions: list,
        notes: Optional[str] = None,
    ) -> dict:
        """
        Store interviewee feedback (corrections and selected questions).

        This is called when an interviewee submits their pre-interview form,
        identifying AI inaccuracies and choosing their preferred discussion topics.

        Args:
            session_id: The unique session identifier.
            created_at: The sort key for the session record.
            corrections: List of corrections to AI-generated findings.
            selected_questions: List of question IDs selected by interviewee.
            notes: Optional free-form notes from the interviewee.

        Returns:
            dict: The updated session attributes.
        """
        feedback = {
            "corrections": corrections,
            "selectedQuestions": selected_questions,
            "notes": notes or "",
            "submittedAt": datetime.now(timezone.utc).isoformat(),
        }

        return self.update_session(session_id, created_at, {
            "feedback": feedback,
            "status": "FEEDBACK_RECEIVED",
        })
