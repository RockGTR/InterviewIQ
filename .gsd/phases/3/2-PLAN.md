---
phase: 3
plan: 2
wave: 2
---

# Plan 3.2: End-to-End Pipeline Integration & Verification

## Objective
Verify the full pipeline works end-to-end: POST /pipeline triggers Step Functions → CreateSession → Scrape → Analyze → GenerateBrief → READY. Deploy and test with a real mock company.

## Context
- .gsd/phases/3/1-PLAN.md — Plan 3.1 must complete first (bedrock methods implemented)
- backend/functions/generate_brief/handler.py — Already calls the 4 bedrock methods in sequence
- backend/statemachine/interview_pipeline.asl.json — Step Functions definition
- backend/template.yaml — SAM template

## Tasks

<task type="auto">
  <name>Update Lambda Layer and Deploy</name>
  <files>backend/layers/shared/python/shared/bedrock_service.py</files>
  <action>
    1. Copy the updated bedrock_service.py to the Lambda Layer:
       cp backend/shared/bedrock_service.py backend/layers/shared/python/shared/bedrock_service.py
    2. Build and deploy:
       cd backend && sam build && sam deploy --no-confirm-changeset
    3. Verify deployment succeeds (stack status UPDATE_COMPLETE)
  </action>
  <verify>aws cloudformation describe-stacks --stack-name interview-iq --query 'Stacks[0].StackStatus' --output text</verify>
  <done>Stack is UPDATE_COMPLETE with updated Lambda Layer</done>
</task>

<task type="auto">
  <name>Test Full Pipeline with Mock Company</name>
  <files>N/A — testing only</files>
  <action>
    1. Trigger the pipeline:
       curl -X POST https://API_URL/dev/pipeline \
         -H "Content-Type: application/json" \
         -d '{"companyName": "GridFlex Energy", "companyUrl": "https://gridflex.com"}'
    2. Note the executionId from response
    3. Poll status every 10 seconds:
       curl https://API_URL/dev/pipeline/{executionId}
    4. When status is SUCCEEDED, retrieve the session:
       curl https://API_URL/dev/sessions/{sessionId}
    5. Verify the response contains:
       - interviewerBrief with all 7 sections
       - intervieweePacket with 3 sections
       - questions array with 10 items
       - status is "READY"
  </action>
  <verify>curl -s https://API_URL/dev/health | python3 -m json.tool</verify>
  <done>Pipeline runs end-to-end, session status is READY, brief contains real AI-generated content</done>
</task>

## Success Criteria
- [ ] SAM deploy succeeds with updated bedrock_service.py
- [ ] POST /pipeline returns executionId
- [ ] Pipeline reaches SUCCEEDED status
- [ ] Session contains real AI-generated brief with questions
