"""
InterviewIQ Shared Service Modules
===================================

This package contains reusable service classes for AWS resource interaction.
Each module encapsulates operations for a specific AWS service, keeping
Lambda handlers thin and business logic testable.

Modules:
    - dynamo_service: DynamoDB session CRUD operations
    - s3_service: S3 document storage operations
    - bedrock_service: Amazon Bedrock/Claude AI generation
    - textract_service: Amazon Textract document processing
    - comprehend_service: Amazon Comprehend NLP analysis
    - scraper_service: Web scraping for company data
"""
