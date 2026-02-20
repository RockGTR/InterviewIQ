---
phase: 6
plan: 1
wave: 1
---

# Plan 6.1: API Reference & Architecture Docs

## Objective
Create detailed API reference documentation (all 10 endpoints with request/response examples) and a system architecture doc explaining data flow, service interactions, and design decisions.

## Context
- backend/template.yaml (all endpoints defined)
- backend/functions/*/handler.py (handler logic)
- backend/shared/*.py (service modules)
- backend/statemachine/interview_pipeline.asl.json (pipeline flow)
- README.md (high-level architecture already present)

## Tasks

<task type="auto">
  <name>Create API Reference</name>
  <files>docs/API_REFERENCE.md</files>
  <action>
    Create a full API reference covering all 10 endpoints:
    - Method, path, description
    - Request body schema (JSON)
    - Response body schema (JSON)
    - Error responses
    - Example curl commands
    - Status codes

    Reference each handler.py to get exact request/response shapes.
  </action>
  <verify>test -f docs/API_REFERENCE.md && wc -l docs/API_REFERENCE.md</verify>
  <done>API_REFERENCE.md exists with all 10 endpoints documented including request/response schemas</done>
</task>

<task type="auto">
  <name>Create Architecture Doc</name>
  <files>docs/ARCHITECTURE.md</files>
  <action>
    Create architecture documentation covering:
    - System overview and design philosophy
    - AWS service map (which services, why each was chosen)
    - Data flow: session lifecycle (CREATED → SCRAPING → ANALYZING → GENERATING → READY → FEEDBACK → COMPLETE)
    - Lambda Layer architecture (why shared modules, how the build works)
    - Step Functions pipeline (each state, what it does, error handling)
    - Frontend routing and page responsibilities
    - Security model (IAM roles, CORS, API Gateway auth)
  </action>
  <verify>test -f docs/ARCHITECTURE.md && wc -l docs/ARCHITECTURE.md</verify>
  <done>ARCHITECTURE.md exists with system design, data flow, and service interaction docs</done>
</task>

## Success Criteria
- [ ] docs/API_REFERENCE.md exists with all 10 endpoints
- [ ] docs/ARCHITECTURE.md exists with system design docs
