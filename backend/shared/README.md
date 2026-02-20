# Shared Service Modules

## Overview

These modules encapsulate all AWS service interactions for the InterviewIQ backend. Lambda handlers are kept thin — they parse the API Gateway event, call the appropriate service, and return a formatted response.

## Modules

| Module | Service | Purpose |
|--------|---------|---------|
| `dynamo_service.py` | DynamoDB | Session CRUD, feedback storage |
| `s3_service.py` | S3 | Document upload/download, presigned URLs |
| `bedrock_service.py` | Bedrock/Claude | AI generation (profiles, questions, briefs) |
| `textract_service.py` | Textract + python-docx | Document text extraction |
| `comprehend_service.py` | Comprehend | Entity/key phrase/sentiment detection |
| `scraper_service.py` | requests + BS4 | Web scraping with mock fallback |

## Architecture Pattern

```
API Gateway Event
       │
       ▼
Lambda Handler (thin)
 ├── Parse event
 ├── Validate input
 ├── Call service module ◄── Business logic here
 ├── Format response
 └── Handle errors
```

## Usage

```python
from shared.dynamo_service import DynamoDBService
from shared.bedrock_service import BedrockService

db = DynamoDBService()
session = db.create_session("GridFlex Energy")

bedrock = BedrockService()
profile = bedrock.generate_company_profile(scraped_data, docs)
```

## Environment Variables

All services read configuration from environment variables set in the SAM template:
- `TABLE_NAME` — DynamoDB table
- `BUCKET_NAME` — S3 bucket
- `MODEL_ID` — Bedrock model
- `BEDROCK_REGION` — Bedrock AWS region
