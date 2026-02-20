---
phase: 1
plan: 3
wave: 2
---

# Plan 1.3: API Gateway & Lambda Function Scaffolds

## Objective
Create all Python Lambda function handlers with API Gateway routes. This plan depends on Plan 1.1 (infrastructure must exist). Each Lambda is a thin handler that delegates to service modules — business logic comes in Phase 2.

## Context
- .gsd/SPEC.md (API endpoints needed)
- .gsd/phases/1/RESEARCH.md (sections 4, 5, 8)
- backend/template.yaml (from Plan 1.1)

## Tasks

<task type="auto">
  <name>Create Lambda function handlers and service module stubs</name>
  <files>
    backend/functions/health/handler.py
    backend/functions/create_session/handler.py
    backend/functions/get_session/handler.py
    backend/functions/scrape_company/handler.py
    backend/functions/parse_document/handler.py
    backend/functions/analyze_company/handler.py
    backend/functions/generate_brief/handler.py
    backend/functions/submit_feedback/handler.py
    backend/shared/dynamo_service.py
    backend/shared/s3_service.py
    backend/shared/bedrock_service.py
    backend/shared/textract_service.py
    backend/shared/comprehend_service.py
    backend/shared/scraper_service.py
    backend/shared/__init__.py
    backend/shared/README.md
  </files>
  <action>
    Create Lambda handlers following the thin-handler pattern:

    1. **Handler files** (in `backend/functions/{name}/handler.py`):
       Each handler should:
       - Parse the API Gateway event (query params, body, path params)
       - Validate input
       - Call the appropriate service module
       - Return properly formatted API Gateway response with CORS headers
       - Handle errors gracefully with structured error responses
       - Include comprehensive docstrings

       Handlers to create:
       - `health/handler.py` — GET /health → returns system status
       - `create_session/handler.py` — POST /sessions → creates new interview session
       - `get_session/handler.py` — GET /sessions/{sessionId} → returns session data
       - `scrape_company/handler.py` — POST /scrape → triggers web scraping
       - `parse_document/handler.py` — POST /parse → triggers Textract processing
       - `analyze_company/handler.py` — POST /analyze → triggers Comprehend analysis
       - `generate_brief/handler.py` — POST /generate → triggers Bedrock brief generation
       - `submit_feedback/handler.py` — POST /sessions/{sessionId}/feedback → stores interviewee feedback

    2. **Shared service modules** (in `backend/shared/`):
       Each service should be a class with comprehensive docstrings:
       - `dynamo_service.py` — DynamoDBService: create_session, get_session, update_session, store_feedback
       - `s3_service.py` — S3Service: upload_document, get_document, generate_presigned_url
       - `bedrock_service.py` — BedrockService: invoke_claude, generate_company_profile, generate_questions (stubs)
       - `textract_service.py` — TextractService: process_document, extract_text (stubs)
       - `comprehend_service.py` — ComprehendService: detect_entities, detect_key_phrases, detect_sentiment (stubs)
       - `scraper_service.py` — ScraperService: scrape_url, parse_company_page (stubs)
       - `__init__.py` — Package init
       - `README.md` — Module documentation

    IMPORTANT:
    - ALL functions and classes must have comprehensive docstrings
    - Use Python type hints throughout
    - Service stubs should have the correct method signatures and return types
    - Business logic will be implemented in Phase 2 — these are just stubs
    - Use environment variables for resource names (table name, bucket name, model ID)
    - Include a standard CORS response helper function
    - Each handler should catch and log exceptions properly
  </action>
  <verify>
    python3 -c "
    import sys
    sys.path.insert(0, 'backend/shared')
    from dynamo_service import DynamoDBService
    from s3_service import S3Service
    from bedrock_service import BedrockService
    from textract_service import TextractService
    from comprehend_service import ComprehendService
    from scraper_service import ScraperService
    print('All service modules import successfully')
    "
  </verify>
  <done>
    - All 8 Lambda handlers created with proper structure
    - All 6 service modules importable with correct class/method signatures
    - Every function has docstrings and type hints
    - CORS helper function works
    - README.md documents the module architecture
  </done>
</task>

<task type="auto">
  <name>Update SAM template with Lambda functions and API Gateway</name>
  <files>
    backend/template.yaml
  </files>
  <action>
    Update the SAM template from Plan 1.1 to add:

    1. **API Gateway** (`InterviewIQApi`):
       - REST API type
       - CORS enabled for all origins (hackathon)
       - Stage: `dev`

    2. **Lambda Functions** (one per handler):
       - Runtime: python3.13
       - Handler: handler.lambda_handler
       - Memory: 256MB (512MB for Bedrock/Textract functions)
       - Timeout: 30s (300s for scrape/generate functions)
       - Layer reference: SharedDepsLayer
       - Role: InterviewIQLambdaRole
       - Environment variables: TABLE_NAME, BUCKET_NAME, MODEL_ID

    3. **API Gateway Routes**:
       - GET /health → HealthFunction
       - POST /sessions → CreateSessionFunction
       - GET /sessions/{sessionId} → GetSessionFunction
       - POST /scrape → ScrapeFunction
       - POST /parse → ParseDocumentFunction
       - POST /analyze → AnalyzeFunction
       - POST /generate → GenerateBriefFunction
       - POST /sessions/{sessionId}/feedback → SubmitFeedbackFunction

    IMPORTANT:
    - Each function definition should have YAML comments
    - Use `!Sub` for dynamic resource references
    - Keep Lambda code path relative: `functions/{name}/`
    - Add Outputs section with API URL
  </action>
  <verify>
    cd backend && sam validate && sam build
  </verify>
  <done>
    - SAM template validates with all functions defined
    - SAM build succeeds
    - API Gateway has all 8 routes
    - All functions reference shared layer and role
    - Environment variables configured
  </done>
</task>

## Success Criteria
- [ ] 8 Lambda handlers created with proper API Gateway event handling
- [ ] 6 shared service modules with documented class stubs
- [ ] SAM template updated with all functions and API routes
- [ ] `sam build` succeeds
- [ ] All imports work correctly
