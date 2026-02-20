# System Architecture

## Design Philosophy

InterviewIQ follows a **serverless-first** architecture built entirely on AWS managed services. This eliminates server management, scales automatically, and keeps costs near-zero during hackathon development.

**Key decisions:**
- **No servers** — Lambda + API Gateway + DynamoDB + S3
- **Python 3.13** backend — Best AWS SDK support (boto3), rich NLP ecosystem
- **React + Vite** frontend — Fast builds, modern DX
- **Step Functions** for orchestration — Visual workflow, built-in retry/error handling

---

## AWS Service Map

| Service | Resource | Purpose |
|---------|----------|---------|
| **API Gateway** | InterviewIQ-API | REST API, CORS, request routing |
| **Lambda** | 9 functions | Request handlers (Python 3.13, x86_64) |
| **Lambda Layer** | shared-deps v2 | Shared modules + pip deps |
| **DynamoDB** | interview-iq-sessions | Session state, metadata |
| **S3** | interview-iq-docs | Document storage, scraped data, briefs |
| **Step Functions** | interview-iq-pipeline | End-to-end orchestration |
| **Bedrock** | Claude 3.5 Sonnet | AI brief generation |
| **Comprehend** | — | Entity extraction, sentiment, key phrases |
| **Textract** | — | PDF/image OCR text extraction |
| **CloudFormation** | interview-iq stack | Infrastructure-as-code (SAM) |

---

## Data Flow

### Pipeline Execution Flow

```
User Input (company name + URL)
       │
       ▼
┌─────────────────┐
│  CreateSession   │  → DynamoDB: new session (status: CREATED)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  ParallelDataGathering      │
│  ┌───────────┐ ┌──────────┐ │
│  │  Scrape   │ │  Parse   │ │  → S3: scraped_data.json, parsed text
│  │  Company  │ │  Docs    │ │  → DynamoDB: update session
│  └───────────┘ └──────────┘ │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────┐
│  Comprehend     │  → DynamoDB: entities, sentiment, key phrases
│  NLP Analysis   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Bedrock/Claude │  → S3: interview_brief.json
│  Generate Brief │  → DynamoDB: status → READY
└────────┬────────┘
         │
         ▼
    Session READY
    (Dashboard viewable)
```

### Session State Machine

```
CREATED → SCRAPING → SCRAPING_COMPLETE → ANALYZING → GENERATING → READY
                                                                    │
                                                          Interviewee reviews
                                                                    │
                                                                    ▼
                                                          FEEDBACK_RECEIVED
                                                                    │
                                                                    ▼
                                                                COMPLETE
```

---

## Lambda Layer Architecture

The Lambda Layer solves a key problem: shared Python modules need to be available to all 9 Lambda functions.

```
layers/shared/
├── requirements.txt          # pip deps: requests, beautifulsoup4, python-docx
├── Makefile                  # Build: pip install + copy shared modules
└── python/
    └── shared/               # Python package (on Lambda's sys.path)
        ├── __init__.py
        ├── bedrock_service.py
        ├── comprehend_service.py
        ├── dynamo_service.py
        ├── s3_service.py
        ├── scraper_service.py
        ├── textract_service.py
        └── response_helpers.py
```

**Build process** (SAM `BuildMethod: makefile`):
1. `pip install` dependencies into `python/`
2. Copy `shared/*.py` into `python/shared/`
3. SAM packages as Lambda Layer

**Import pattern** in handlers:
```python
from shared.response_helpers import success_response, error_response
from shared.dynamo_service import DynamoDBService
```

---

## Frontend Architecture

```
src/
├── App.jsx              # BrowserRouter with 4 routes
├── main.jsx             # Entry point (StrictMode)
├── index.css            # Design system (CSS variables, dark theme)
├── pages/
│   ├── HomePage.jsx         # / — Company input form
│   ├── InterviewerDashboard.jsx  # /dashboard/:sessionId
│   ├── IntervieweePortal.jsx     # /interview/:sessionId
│   └── InterviewGuide.jsx        # /guide/:sessionId
├── components/
│   ├── Header.jsx       # Navigation (glassmorphism)
│   └── Layout.jsx       # Page wrapper
└── services/
    └── api.js           # API client (fetch-based)
```

**Routing:**

| Route | Page | User |
|-------|------|------|
| `/` | HomePage | Interviewer |
| `/dashboard/:id` | InterviewerDashboard | Interviewer |
| `/interview/:id` | IntervieweePortal | Interviewee |
| `/guide/:id` | InterviewGuide | Interviewer |

---

## Security Model

| Layer | Mechanism |
|-------|-----------|
| API Gateway | Open (hackathon); add API keys for production |
| Lambda IAM | Least-privilege per function (DynamoDB, S3, Bedrock, Comprehend, Textract) |
| S3 | Private bucket, pre-signed URLs for access |
| DynamoDB | Function-scoped IAM policies |
| CORS | `AllowOrigin: *` (hackathon; restrict in production) |
| Bedrock | IAM policy with `bedrock:InvokeModel` |
