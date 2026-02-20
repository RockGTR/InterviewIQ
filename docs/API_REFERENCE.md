# API Reference

**Base URL:** `https://l8xc3yrptf.execute-api.us-west-2.amazonaws.com/dev`

All responses follow the format:
```json
{ "field": "value" }        // 2xx success
{ "error": "msg" }          // 4xx/5xx error
```

---

## Endpoints

### GET /health

Health check — returns system status.

**Response 200:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-20T16:45:00+00:00",
  "service": "InterviewIQ",
  "version": "1.0.0",
  "config": {
    "table_name": "interview-iq-sessions-interview-iq",
    "bucket_name": "interview-iq-docs-143643339510-us-west-2",
    "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "bedrock_region": "us-east-1"
  }
}
```

---

### POST /sessions

Create a new interview preparation session.

**Request:**
```json
{
  "companyName": "GridFlex Energy",
  "companyUrl": "https://gridflex.com",
  "metadata": {}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `companyName` | string | ✅ | Company to research |
| `companyUrl` | string | ❌ | Company website URL |
| `metadata` | object | ❌ | Additional metadata |

**Response 201:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "companyName": "GridFlex Energy",
  "companyUrl": "https://gridflex.com",
  "status": "CREATED",
  "createdAt": "2026-02-20T10:00:00Z"
}
```

**Error 400:** `{ "error": "companyName is required" }`

---

### GET /sessions/{sessionId}

Retrieve session data including briefs and feedback.

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `sessionId` | string | UUID of the session |

**Response 200:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "companyName": "GridFlex Energy",
  "status": "READY",
  "brief": { ... },
  "feedback": { ... },
  "createdAt": "2026-02-20T10:00:00Z"
}
```

**Error 400:** `{ "error": "sessionId is required" }`
**Error 404:** `{ "error": "Session not found" }`

---

### POST /scrape

Scrape public company information from web sources.

**Request:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "companyName": "GridFlex Energy",
  "companyUrl": "https://gridflex.com"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sessionId` | string | ✅ | Session to associate data with |
| `companyName` | string | ✅ | Company name to scrape |
| `companyUrl` | string | ❌ | Direct URL to scrape |

**Response 200:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "source": "mock",
  "pages_count": 3,
  "summary": {
    "name": "GridFlex Energy",
    "industry": "Energy Technology",
    "description": "..."
  }
}
```

**Notes:** Falls back to mock data (`backend/data/mock_companies.json`) if live scraping fails. 5 companies pre-loaded: GridFlex Energy, LoneStar Precision, Texas Mechanical, LaunchStack Tech, PrairieLogic AG.

---

### POST /parse

Parse uploaded documents via Textract for text extraction.

**Request:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "s3Key": "uploads/resume.docx",
  "fileType": "docx"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sessionId` | string | ✅ | Session to associate data with |
| `s3Key` | string | ✅ | S3 key of uploaded document |
| `fileType` | string | ❌ | File type (`docx`, `pdf`). Auto-detected if omitted |

**Response 200:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "text": "Extracted document text...",
  "pages": 3,
  "method": "python-docx"
}
```

**Notes:** `.docx` files use python-docx (direct extraction). PDF/image files use Amazon Textract OCR.

---

### POST /analyze

Run NLP analysis using Amazon Comprehend.

**Request:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "text": "Company description text to analyze..."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sessionId` | string | ✅ | Session to associate with |
| `text` | string | ✅ | Text to analyze |

**Response 200:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "entities": [
    { "text": "GridFlex", "type": "ORGANIZATION", "score": 0.99 }
  ],
  "keyPhrases": ["renewable energy", "smart grid"],
  "sentiment": { "overall": "POSITIVE", "scores": { ... } }
}
```

---

### POST /generate

Generate interview brief and questions using Amazon Bedrock (Claude).

**Request:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "companyProfile": { ... },
  "analysisResults": { ... }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sessionId` | string | ✅ | Session to associate with |
| `companyProfile` | object | ✅ | Scraped + parsed company data |
| `analysisResults` | object | ❌ | NLP analysis results |

**Response 200:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "brief": {
    "companyOverview": "...",
    "questions": [
      { "question": "...", "purpose": "...", "followUp": "..." }
    ],
    "conversationFlow": { ... },
    "intervieweePacket": { ... }
  }
}
```

**Timeout:** 300s (5 min) — Bedrock generation can take time.

---

### POST /sessions/{sessionId}/feedback

Store interviewee corrections and selected questions.

**Request:**
```json
{
  "corrections": [
    { "field": "industry", "original": "Oil & Gas", "corrected": "Energy Tech" }
  ],
  "selectedQuestions": ["q1", "q3"],
  "additionalNotes": "I'd like to discuss our sustainability initiatives"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `corrections` | array | ❌ | List of factual corrections |
| `selectedQuestions` | array | ❌ | IDs of questions interviewee selected |
| `additionalNotes` | string | ❌ | Free-form notes from interviewee |

**Response 200:**
```json
{
  "sessionId": "a1b2c3d4-...",
  "feedbackStored": true,
  "status": "FEEDBACK_RECEIVED"
}
```

---

### POST /pipeline

Start the full end-to-end interview intelligence pipeline (Step Functions).

**Request:**
```json
{
  "companyName": "GridFlex Energy",
  "companyUrl": "https://gridflex.com"
}
```

**Response 200:**
```json
{
  "executionArn": "arn:aws:states:us-west-2:...:execution:...",
  "sessionId": "a1b2c3d4-...",
  "status": "RUNNING"
}
```

---

### GET /pipeline/{executionId}

Check pipeline execution status.

**Response 200:**
```json
{
  "executionArn": "arn:aws:states:...",
  "status": "SUCCEEDED",
  "sessionId": "a1b2c3d4-...",
  "output": { ... }
}
```

**Status values:** `RUNNING`, `SUCCEEDED`, `FAILED`, `TIMED_OUT`, `ABORTED`

---

## Session Status Lifecycle

```
CREATED → SCRAPING → SCRAPING_COMPLETE → ANALYZING → GENERATING → READY → FEEDBACK_RECEIVED → COMPLETE
```

## Error Format

All errors return:
```json
{
  "error": "Human-readable error message",
  "details": "Technical details (optional)"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request (missing/invalid parameters) |
| 404 | Resource not found |
| 500 | Internal server error |
