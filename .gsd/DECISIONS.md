# DECISIONS.md — Architecture Decision Records

> Log of significant technical decisions.

## ADR-001: Frontend Framework
**Date**: 2026-02-20
**Decision**: React via Vite (local dev) with AWS Amplify deployment
**Rationale**: Team is experienced with React. Vite for fast local dev; Amplify for deployment if time permits.
**Alternatives**: Plain HTML/JS (simpler but less polished), Next.js (overkill for demo)

## ADR-002: AI Model
**Date**: 2026-02-20
**Decision**: Amazon Bedrock with Claude (best available model)
**Rationale**: Claude provides superior reasoning and structured output for question generation. Best-in-class for the "wow factor" on question quality.

## ADR-003: No Authentication
**Date**: 2026-02-20
**Decision**: Skip auth for hackathon demo
**Rationale**: 12-hour timeline. Auth adds no demo value. Single-user mode sufficient.

## ADR-004: PDF Generation
**Date**: 2026-02-20
**Decision**: Client-side PDF generation (e.g., react-pdf or html2pdf)
**Rationale**: Avoids server-side PDF complexity. Faster to implement. Good enough for demo quality.

## ADR-005: Data Collection
**Date**: 2026-02-20
**Decision**: Automated web scraping (AWS-native, free tier) + sample .docx data files via Textract
**Rationale**: Web scraping for public info demonstrates real-world capability. Sample docs simulate proprietary Texas A&M data. No LinkedIn (ToS risk).

---

## Phase 1 Decisions (from `/discuss-phase 1`)

### ADR-006: AWS-First Architecture
**Date**: 2026-02-20
**Decision**: Deploy to AWS from the start — Lambda, API Gateway, S3, DynamoDB, Bedrock
**Rationale**: Team is 4 AWS experts. 72-hour timeline is generous. Real AWS infra demonstrates production-readiness to judges.
**Alternatives**: Local-first development (rejected — not needed with 72h and AWS expertise)

### ADR-007: Python Backend
**Date**: 2026-02-20
**Decision**: Python for all Lambda functions and backend logic
**Rationale**: Better AI/ML library ecosystem, easier Bedrock SDK, team preference.
**Alternatives**: Node.js/TypeScript (rejected)

### ADR-008: Textract for Document Parsing
**Date**: 2026-02-20
**Decision**: Use Amazon Textract for .docx parsing
**Rationale**: Demonstrates AWS service integration. Team wants to showcase Textract usage.

### ADR-009: Timeline Correction
**Date**: 2026-02-20
**Decision**: Hackathon is 72 hours (not 12h). Regions: us-west-2, us-east-1.
**Rationale**: AWS event dashboard confirms 72h duration. More time = higher polish, better docs.

### ADR-010: Sample Data as Exemplars
**Date**: 2026-02-20
**Decision**: The 5 .docx case files serve as BOTH training exemplars AND demo data
**Rationale**: Each file contains a pre-interview AI brief + full interview transcript — exactly the output format our system should produce. Use them to:
  1. Train/prompt the AI on expected output format
  2. Provide demo data for showcasing the system
  3. Serve as the "proprietary Texas A&M data" source

---

## Phase 3 Decisions (from `/discuss-phase 3`)

### ADR-011: Maximize AI Quality via Comprehend
**Date**: 2026-02-20
**Decision**: Use Amazon Comprehend for sentiment and entity extraction to feed as structured context to Bedrock.
**Rationale**: User prioritized the best output quality. Supplying structured NLP data alongside raw text helps Claude generate deeper, more nuanced questions.

### ADR-012: Chained Prompts (Pipeline) Strategy
**Date**: 2026-02-20
**Decision**: Use a chained prompt approach (Option B) for generating the interview brief.
**Rationale**: Breaking generation into steps (e.g., Profile -> Questions -> Flow) produces higher quality output and is easier to debug than one massive prompt.

### ADR-013: Async Polling for Long-Running AI Tasks
**Date**: 2026-02-20
**Decision**: Handle API Gateway 29s timeouts using Step Functions async execution and frontend polling.
**Rationale**: Professional approach for serverless AI workloads. API Gateway triggers Step Functions and immediately returns an execution ID (202 Accepted/200 OK). Frontend polls a status endpoint until complete.

