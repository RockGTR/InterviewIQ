---
phase: 6
plan: 2
wave: 1
---

# Plan 6.2: Interview Workflow Guide & Frontend README Update

## Objective
Create an end-user-facing interview workflow guide explaining how the system works from both the interviewer and interviewee perspective. Update the frontend README with useful local dev information.

## Context
- .gsd/SPEC.md (system requirements)
- frontend/src/pages/*.jsx (page components)
- frontend/src/services/api.js (API client)
- README.md (workflow already outlined at high level)

## Tasks

<task type="auto">
  <name>Create Interview Workflow Guide</name>
  <files>docs/INTERVIEW_WORKFLOW.md</files>
  <action>
    Create a user-facing guide documenting the two-stage interview workflow:

    **Stage 1 — Interviewer Preparation:**
    - Enter company name + optional URL
    - System scrapes public info + parses uploaded docs
    - AI analyzes data and generates interview brief
    - Interviewer reviews: company profile, tailored questions, conversation flow

    **Stage 2 — Interviewee Review:**
    - Interviewer shares unique link with interviewee
    - Interviewee reviews AI findings
    - Corrects inaccuracies
    - Selects 2-3 preferred discussion questions
    - Interviewer gets updated guide with corrections

    Include: what data is collected, how AI generates questions, privacy considerations.
  </action>
  <verify>test -f docs/INTERVIEW_WORKFLOW.md && wc -l docs/INTERVIEW_WORKFLOW.md</verify>
  <done>INTERVIEW_WORKFLOW.md exists explaining both stages of the workflow</done>
</task>

<task type="auto">
  <name>Update Frontend README</name>
  <files>frontend/README.md</files>
  <action>
    Update frontend/README.md with:
    - Local development setup (npm install, npm run dev)
    - Page descriptions (HomePage, Dashboard, Portal, Guide)
    - API service configuration (how to set API_BASE)
    - Build and deploy instructions
    - Design system overview (CSS variables, dark theme)
  </action>
  <verify>wc -l frontend/README.md</verify>
  <done>frontend/README.md has comprehensive local dev and page documentation</done>
</task>

## Success Criteria
- [ ] docs/INTERVIEW_WORKFLOW.md exists
- [ ] frontend/README.md updated with comprehensive content
