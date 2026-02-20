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
**Decision**: Automated web scraping + sample .docx data files
**Rationale**: Web scraping for public info demonstrates real-world capability. Sample docs simulate proprietary Texas A&M data. No LinkedIn (ToS risk).
