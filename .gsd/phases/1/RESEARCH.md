---
phase: 1
level: 2
researched_at: 2026-02-20
---

# Phase 1 Research — Infrastructure & Data Layer

## Questions Investigated

1. How to deploy a React app with AWS Amplify Gen 2?
2. Can Amazon Textract parse .docx files directly?
3. What's the best free AWS-native approach for web scraping?
4. How to package Python Lambda functions with dependencies?
5. How to invoke Bedrock/Claude from Python Lambda?
6. Should we use Bedrock Data Automation for document processing?
7. How to orchestrate multi-step workflows with Step Functions?
8. How to use Amazon Comprehend for company text analysis?

---

## Findings

### 1. AWS Amplify Gen 2 (React Deployment)

Amplify Gen 2 uses a **code-first approach** — backend defined in TypeScript under an `amplify/` directory.

**Setup steps:**
- Node.js v18.17+, npm v9+
- `npm create amplify@latest` to scaffold
- `npx ampx sandbox` for per-developer cloud sandboxes
- Git-based CI/CD: connect GitHub repo → auto-deploy on push

**Key concern:** Amplify Gen 2 expects TypeScript backend definitions, but our backend is Python Lambda. We'll use Amplify **only for frontend hosting** and manage Lambda/API Gateway separately.

**Recommendation:** Use Amplify for React frontend deployment. Backend (Python Lambdas) deployed via AWS CLI/SAM/CDK separately.

---

### 2. Amazon Textract & .docx Files

> ⚠️ **Textract does NOT support .docx files directly.**
> Supported formats: PNG, JPEG, TIFF, PDF only.

**To use Textract with .docx files, we need a conversion step:**
1. Convert .docx → PDF (using `python-docx` + `docx2pdf` or LibreOffice)
2. Upload PDF to S3
3. Call Textract on the PDF

**Alternative approach:**
- Use `python-docx` to extract text directly from .docx
- This is simpler, faster, and free — no Textract needed for .docx
- Then use Textract only if the project handles scanned/image documents

**Recommendation:** Two-path approach:
1. **Primary path:** Upload .docx to S3 → Lambda converts to PDF → Textract processes PDF (demonstrates Textract as required by hackathon)
2. **Fallback:** `python-docx` for direct text extraction as backup

---

### 3. Web Scraping (AWS-native, Free)

**Approach:** Lambda function with `requests` + `BeautifulSoup4`

**Free tier coverage:**
- Lambda: 1M free requests + 3.2M seconds compute/month
- More than sufficient for hackathon scraping needs

**Implementation:**
```python
import requests
from bs4 import BeautifulSoup

def scrape_company(url):
    response = requests.get(url, headers={'User-Agent': '...'})
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract company info from page
```

**Packaging:** Bundle `requests` + `beautifulsoup4` as Lambda Layer

**Concerns:**
- 15-minute Lambda timeout — sufficient for our use case
- AWS IP addresses may be blocked — unlikely for simple company websites
- No headless browser needed for text extraction

**Recommendation:** Lambda + requests + BeautifulSoup4. Package as Lambda Layer. Scrape company "about" pages, news, press releases.

---

### 4. Lambda Python Packaging

**Best practices:**
- Use **Lambda Layers** for shared dependencies (boto3, requests, beautifulsoup4)
- Python 3.13 runtime (latest stable in Feb 2026)
- Bundle **own boto3** version (don't rely on pre-installed — may be outdated)
- Structure: `python/` directory at root of layer .zip

**Layer build command:**
```bash
pip install -r requirements.txt -t python/ --platform manylinux2014_x86_64 --only-binary=:all:
zip -r layer.zip python/
```

**SnapStart for Python** — reduces cold starts (available since 2025)

**Recommendation:** Create one shared Lambda Layer with all common dependencies. Use SAM or raw CloudFormation for deployment.

---

### 5. Amazon Bedrock / Claude Integration

**API pattern:**
```python
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

response = bedrock.invoke_model(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    contentType='application/json',
    accept='application/json',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096
    })
)

result = json.loads(response['body'].read())
```

**Recommendation:** Use `anthropic.claude-3-5-sonnet` for best quality. Wrap in a reusable service module. Use streaming for long-running generations if needed.

---

### 6. Bedrock Data Automation (BDA)

**Status:** GA as of July 2025. Available in our hackathon timeframe.

**What it does:**
- Unified API for processing documents, images, audio, video
- Zero-shot document classification
- Intelligent summarization
- Confidence scores and hallucination mitigation
- Blueprints for custom extraction schemas

**Trade-off:**
- Pro: Single API replaces Textract + manual parsing + Comprehend
- Con: Additional learning curve, may be overkill for 5 .docx files
- Con: Less control over output format

**Recommendation:** Consider as a stretch goal. Start with Textract + Comprehend (more granular control, better for demo narrative). Integrate BDA only if time permits.

---

### 7. AWS Step Functions

**Use case:** Orchestrate the multi-step interview intelligence pipeline:
```
Scrape → Textract → Comprehend → Bedrock → Assemble Brief
```

**Implementation:**
- Define state machine in JSON/YAML (Amazon States Language)
- Each step invokes a Lambda function
- Built-in error handling, retries, parallel execution
- Visual workflow in AWS console — great for demo!

**Recommendation:** Use Step Functions to orchestrate the pipeline. Creates a clean architecture and impressive visual for demo.

---

### 8. Amazon Comprehend

**Relevant APIs:**
- `detect_entities()` — extracts PERSON, ORGANIZATION, LOCATION, DATE, QUANTITY
- `detect_key_phrases()` — extracts meaningful phrases
- `detect_sentiment()` — positive/negative/neutral/mixed

**Integration:**
```python
comprehend = boto3.client('comprehend')
entities = comprehend.detect_entities(Text=text, LanguageCode='en')
key_phrases = comprehend.detect_key_phrases(Text=text, LanguageCode='en')
```

**Text limit:** 5,000 bytes per synchronous request. Use batch for larger docs.

**Recommendation:** Use Comprehend to extract entities and key phrases from scraped data and documents. Feed results to Bedrock/Claude as structured context for question generation.

---

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend hosting | Amplify (frontend only) | Git CI/CD, React-optimized |
| Backend deployment | SAM/CLI (Python Lambda) | Amplify Gen 2 expects TS backend |
| .docx processing | Convert to PDF → Textract | Demonstrates Textract (hackathon req) |
| Web scraping | Lambda + requests + BS4 | Free, simple, sufficient |
| Python runtime | 3.13 | Latest stable |
| Dependency packaging | Lambda Layers | Shared deps, smaller packages |
| Workflow orchestration | Step Functions | Visual, reliable, demo-friendly |
| NLP enrichment | Comprehend | Entities, key phrases, sentiment |
| AI generation | Bedrock Claude 3.5 Sonnet | Best quality for question gen |
| Doc automation (BDA) | Stretch goal | Nice-to-have if time permits |

## Patterns to Follow

- **Lambda handler → service module** — Keep handlers thin, business logic in separate modules
- **Shared Layer** — One Layer with all common deps (boto3, requests, bs4, python-docx)
- **S3 event-driven** — Document upload to S3 triggers processing pipe
- **Step Functions state machine** — Orchestrate multi-step pipeline
- **Structured JSON output from Bedrock** — Request JSON output for easier parsing

## Anti-Patterns to Avoid

- ❌ **Textract on .docx directly** — Will fail; must convert to PDF first
- ❌ **Monolithic Lambda** — Split into focused functions (scrape, parse, analyze, generate)
- ❌ **Hardcoded model IDs** — Use environment variables for model selection
- ❌ **Synchronous Comprehend on large docs** — Use batch or chunk text to 5KB segments
- ❌ **Amplify Gen 2 for Python backend** — It expects TypeScript; use for frontend only

## Dependencies Identified

| Package | Purpose | Deployment |
|---------|---------|------------|
| boto3 | AWS SDK (Bedrock, Textract, Comprehend, S3, DynamoDB) | Lambda Layer |
| requests | HTTP requests for web scraping | Lambda Layer |
| beautifulsoup4 | HTML parsing for web scraping | Lambda Layer |
| python-docx | .docx text extraction (backup to Textract) | Lambda Layer |
| react | Frontend framework | npm |
| react-router-dom | Client-side routing | npm |
| @aws-amplify/ui-react | Amplify UI components | npm |
| aws-amplify | Amplify client SDK | npm |

## Risks

| Risk | Mitigation |
|------|------------|
| Textract .docx conversion adds complexity | Use python-docx as fallback |
| Web scraping blocked by sites | Have mock data ready for demo |
| Bedrock model access not enabled | Confirm in console before starting |
| Lambda cold starts slow demo | Enable SnapStart, warm functions |
| Step Functions learning curve | Start with simple linear workflow |

## Ready for Planning

- [x] Questions answered
- [x] Approach selected
- [x] Dependencies identified
- [x] Risks documented
