---
phase: 3
level: 2
researched_at: 2026-02-20T11:10:00-06:00
---

# Phase 3 Research: AI Intelligence Engine

## Questions Investigated
1. **JSON Structure**: What is the optimal JSON schema for the Interview Brief to support both the Interviewer Dashboard and Interviewee Portal?
2. **Prompt Chaining Architecture**: Should prompt chaining (Profile -> Questions -> Flow) happen inside a single Lambda function or as separate tasks within Step Functions?
3. **API Gateway Timeout Handling**: What are the most professional patterns for handling Bedrock generations that exceed API Gateway's 29-second timeout limit?

## Findings

### 1. JSON Data Structure for Interview Brief
To support the two-stage workflow where the interviewee can select questions and correct facts, the JSON must separate raw data from AI-generated questions and store them by ID.

**Proposed Schema:**
```json
{
  "companyProfile": {
    "name": "string",
    "industry": "string",
    "overview": "string",
    "keyInitiatives": ["string"],
    "risks": ["string"]
  },
  "questions": [
    {
      "id": "q1",
      "text": "string",
      "purpose": "string",
      "followUps": ["string"]
    }
  ],
  "conversationFlow": {
    "opening": "string",
    "coreTopics": ["string"],
    "closing": "string"
  }
}
```
**Recommendation:** Ensure `generate_brief` Lambda produces exactly this structure.

### 2. Prompt Chaining Architecture
Since the user selected "Chained Prompts", we need to break the AI generation into steps.
**Option A: Step Functions Orchestration**
Add `GenerateProfile`, `GenerateQuestions`, and `GenerateFlow` as separate Lambda tasks in `interview_pipeline.asl.json`.
*Pros*: Maximum visibility, individual retries. *Cons*: Requires heavy modification of the SAM template and existing ASL; passing large text payloads between states can hit Step Functions size limits (256KB).

**Option B: Single Lambda Orchestration**
Keep the existing `GenerateBrief` Step Functions task, but inside `generate_brief/handler.py`, make 3 sequential `boto3` calls to Bedrock.
*Pros*: No infrastructure changes required (keeps SAM template clean), easily shares large context variables in memory, avoids Step Functions payload limits. *Cons*: Lambda runs longer (costs slightly more, but well within 15-minute Lambda timeout).

**Recommendation:** **Option B (Single Lambda)**. It is much safer for a hackathon, avoids payload size limits, and fits the already-deployed `interview_pipeline.asl.json`.

### 3. API Gateway Timeout Mitigation
API Gateway has a hard limit of 29 seconds. Bedrock chaining will take 30-60 seconds.
Professional implementation options:
1. **WebSockets**: Complex setup via API Gateway v2, overkill for this timeline.
2. **AppSync (GraphQL Subscriptions)**: Requires entirely new infrastructure.
3. **Async Step Functions + Polling (The "Decoupled Invocation" Pattern)**
   - Client calls `POST /pipeline`.
   - API Gateway triggers Step Functions asynchronously.
   - Immediate response: `200 OK` with `{ "executionArn": "...", "status": "RUNNING" }`.
   - Client implements Exponential Backoff Polling on `GET /pipeline/{executionId}`.

**Recommendation:** The ASL and Lambda stubs for `start_pipeline` and checking execution status already exist. We must implement the polling logic cleanly in the frontend React app (using a custom hook like `usePipelinePolling`).

## Decisions Made
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Chaining Location | In-Lambda (Option B) | Avoids Step Functions payload limits (256KB) and minimizes SAM template surgery. |
| Timeout Handling | Async Polling | We already have the boilerplate `POST /pipeline` and `GET /pipeline/{id}`. Most professional pattern without adding WebSockets. |
| Output Format | Strict JSON | Bedrock must be prompted to return strict JSON arrays/objects matching our exact schema. |

## Patterns to Follow
- **System Prompts**: Use `<system>` tags or the Bedrock `system` parameter to enforce output schema.
- **Claude 3.5 Sonnet Tool Use**: Alternatively, force Claude to call a "save_interview_brief" tool to guarantee the JSON schema perfectly.
- **Exponential Backoff**: Frontend polling must use backoff (2s, 4s, 8s, etc.) to avoid hammering the API.

## Anti-Patterns to Avoid
- **Passing raw HTML to Claude**: Claude has a 200k context, but raw HTML wastes tokens and confuses the model. Extract text first (which `ScraperService` already does).
- **Synchronous API Wait**: Never have the frontend `await fetch('/generate')` without a timeout handler. Always use the `/pipeline` async route for the full generation.

## Dependencies Identified
| Package | Version | Purpose |
|---------|---------|---------|
| `boto3` | Latest | Provided by Lambda environment. Need to verify Bedrock Converse API support. |

## Ready for Planning
- [x] Questions answered
- [x] Approach selected
- [x] Dependencies identified
