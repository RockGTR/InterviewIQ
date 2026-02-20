---
phase: 1
plan: 6
wave: 3
---

# Plan 1.6: Step Functions Orchestration Pipeline

## Objective
Create the AWS Step Functions state machine that orchestrates the complete interview intelligence pipeline: scrape → parse → analyze → generate. This ties all Lambda functions into a single, visual, reliable workflow.

## Context
- .gsd/phases/1/RESEARCH.md (section 7 — Step Functions)
- backend/template.yaml (all Lambda functions from Plans 1.1, 1.3)
- All Lambda handlers and service modules from Plans 1.3-1.5

## Tasks

<task type="auto">
  <name>Define Step Functions state machine</name>
  <files>
    backend/statemachine/interview_pipeline.asl.json
    backend/statemachine/README.md
  </files>
  <action>
    Create the state machine definition in Amazon States Language (ASL):

    1. `backend/statemachine/interview_pipeline.asl.json`:

    The pipeline should have this flow:
    ```
    Start
      → CreateSession (Lambda)
      → Parallel:
          Branch A: ScrapeCompany (Lambda)
          Branch B: ParseDocuments (Lambda) [if documents uploaded]
      → MergeResults (Pass state — combine scraped + parsed data)
      → AnalyzeWithComprehend (Lambda)
      → GenerateBrief (Lambda — Bedrock/Claude)
      → UpdateSession (Lambda — mark as complete)
    End
    ```

    State machine features:
    - **Parallel execution** of scraping and document parsing
    - **Error handling** with Catch and Retry on each step
    - **Input/output processing** with ResultPath and OutputPath
    - **Wait state** after GenerateBrief for any async processing
    - **Choice state** to skip document parsing if no docs uploaded

    2. `backend/statemachine/README.md`:
       - Visual ASCII diagram of the pipeline
       - State-by-state documentation
       - Input/output format for each state
       - Error handling behavior
       - How to trigger the pipeline

    IMPORTANT:
    - Use `Task` states with Lambda ARN references (use ${} placeholders for SAM substitution)
    - Add comprehensive `Comment` fields on every state
    - Include `Retry` with exponential backoff on all Lambda tasks
    - `Catch` errors and route to a FailState with informative output
    - Keep the state machine under 50 states (readability)
  </action>
  <verify>
    python3 -c "
    import json
    with open('backend/statemachine/interview_pipeline.asl.json') as f:
        sm = json.load(f)
    assert 'StartAt' in sm, 'Missing StartAt'
    assert 'States' in sm, 'Missing States'
    states = sm['States']
    print(f'State machine has {len(states)} states: {list(states.keys())}')
    # Check for error handling
    tasks = [s for s, v in states.items() if v.get(\"Type\") == \"Task\"]
    for task in tasks:
        assert 'Retry' in states[task] or 'Catch' in states[task], f'{task} missing error handling'
    print('All task states have error handling ✓')
    "
  </verify>
  <done>
    - State machine JSON is valid ASL
    - Pipeline includes: parallel scrape/parse, analyze, generate
    - All task states have Retry and Catch
    - README.md documents the full pipeline
  </done>
</task>

<task type="auto">
  <name>Add Step Functions to SAM template and create trigger endpoint</name>
  <files>
    backend/template.yaml
    backend/functions/start_pipeline/handler.py
  </files>
  <action>
    1. Update `backend/template.yaml` to add:
       - **Step Functions State Machine** (`InterviewPipeline`):
         - Reference: `backend/statemachine/interview_pipeline.asl.json`
         - IAM role with permission to invoke all Lambda functions
         - Substitutions for Lambda function ARNs
       - **StartPipeline Lambda** (`StartPipelineFunction`):
         - API Gateway route: POST /pipeline
         - Triggers the Step Functions execution
       - **Outputs**: State machine ARN, API URL

    2. Create `backend/functions/start_pipeline/handler.py`:
       - Accept company_name, company_url, and optional document references
       - Start Step Functions execution with input payload
       - Return execution ARN for status tracking
       - Include comprehensive docstrings

    IMPORTANT:
    - Use SAM `AWS::Serverless::StateMachine` resource type
    - Use `DefinitionSubstitutions` to inject Lambda ARNs
    - Add a `GET /pipeline/{executionId}` route to check execution status
    - All functions documented with docstrings
  </action>
  <verify>
    cd backend && sam validate && sam build
  </verify>
  <done>
    - Step Functions state machine defined in SAM template
    - StartPipeline handler triggers executions
    - Status check endpoint returns execution state
    - SAM build succeeds with all resources
    - All code documented
  </done>
</task>

## Success Criteria
- [ ] State machine definition is valid ASL JSON
- [ ] Pipeline handles parallel scraping and document processing
- [ ] Error handling on all task states
- [ ] SAM template includes state machine and trigger Lambda
- [ ] `sam build` succeeds
- [ ] Comprehensive documentation for the entire pipeline
