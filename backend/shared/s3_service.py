"""
S3 Service — Document Storage Operations
==========================================

Provides operations for storing and retrieving documents in Amazon S3.
Used for uploading company documents (.docx, PDFs), storing generated
briefs, and generating presigned URLs for frontend access.

Bucket Structure:
    uploads/{sessionId}/          — Raw uploaded documents
    parsed/{sessionId}/           — Textract-processed text
    briefs/{sessionId}/           — Generated interview briefs
    packets/{sessionId}/          — Interviewee pre-interview packets
    scraped/{sessionId}/          — Raw scraped web content

Usage:
    >>> from shared.s3_service import S3Service
    >>> s3 = S3Service()
    >>> s3.upload_document(file_bytes, "session-123", "company_profile.docx")
    >>> url = s3.generate_presigned_url("session-123", "brief.pdf")
"""

import os
import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Service:
    """
    Service class for S3 document storage operations.

    Manages all file uploads, downloads, and presigned URL generation
    for the InterviewIQ document pipeline.

    Attributes:
        bucket_name (str): S3 bucket name from environment.
        client: boto3 S3 client.
    """

    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize S3 service with bucket reference.

        Args:
            bucket_name: Override bucket name. Defaults to BUCKET_NAME env var.
        """
        self.bucket_name = bucket_name or os.environ.get("BUCKET_NAME", "interview-iq-docs")
        self.client = boto3.client("s3")
        logger.info("S3Service initialized with bucket: %s", self.bucket_name)

    def upload_document(
        self,
        file_bytes: bytes,
        session_id: str,
        filename: str,
        prefix: str = "uploads",
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload a document to S3 under the session's directory.

        Args:
            file_bytes: Raw file content as bytes.
            session_id: Session ID for organizing files.
            filename: Original filename.
            prefix: S3 key prefix (uploads, parsed, briefs, etc.).
            content_type: MIME type of the file.

        Returns:
            str: The S3 key where the file was stored.

        Raises:
            ClientError: If S3 upload fails.
        """
        s3_key = f"{prefix}/{session_id}/{filename}"

        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        self.client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=file_bytes,
            **extra_args,
        )
        logger.info("Uploaded %s to s3://%s/%s", filename, self.bucket_name, s3_key)
        return s3_key

    def get_document(self, s3_key: str) -> bytes:
        """
        Download a document from S3.

        Args:
            s3_key: Full S3 key path to the document.

        Returns:
            bytes: The file content.

        Raises:
            ClientError: If the file doesn't exist or access is denied.
        """
        response = self.client.get_object(Bucket=self.bucket_name, Key=s3_key)
        content = response["Body"].read()
        logger.info("Downloaded %s (%d bytes)", s3_key, len(content))
        return content

    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        method: str = "get_object",
    ) -> str:
        """
        Generate a presigned URL for temporary access to an S3 object.

        Used to provide the frontend with time-limited download links
        for briefs, packets, and other generated documents.

        Args:
            s3_key: Full S3 key path to the document.
            expiration: URL expiry in seconds (default: 1 hour).
            method: S3 operation (get_object for download, put_object for upload).

        Returns:
            str: The presigned URL.

        Raises:
            ClientError: If URL generation fails.
        """
        url = self.client.generate_presigned_url(
            ClientMethod=method,
            Params={"Bucket": self.bucket_name, "Key": s3_key},
            ExpiresIn=expiration,
        )
        logger.info("Generated presigned URL for %s (expires in %ds)", s3_key, expiration)
        return url

    def list_session_files(self, session_id: str, prefix: str = "") -> list:
        """
        List all files associated with a session.

        Args:
            session_id: Session ID to list files for.
            prefix: Optional prefix filter (uploads, parsed, etc.).

        Returns:
            list: List of S3 key strings.
        """
        search_prefix = f"{prefix}/{session_id}/" if prefix else f"uploads/{session_id}/"
        response = self.client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=search_prefix,
        )
        keys = [obj["Key"] for obj in response.get("Contents", [])]
        logger.info("Found %d files for session %s", len(keys), session_id)
        return keys
