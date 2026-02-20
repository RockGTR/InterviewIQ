---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: AWS Core Infrastructure (SAM Template + Lambda Layer)

## Objective
Provision all foundational AWS resources and create the shared Lambda Layer with Python dependencies. This is the bedrock everything else builds on — no other plan can execute without these resources existing first.

## Context
- .gsd/SPEC.md
- .gsd/ROADMAP.md
- .gsd/phases/1/RESEARCH.md (sections 4, 7)
- .gsd/DECISIONS.md (ADR-006 through ADR-010)

## Tasks

<task type="auto">
  <name>Create SAM template with core AWS resources</name>
  <files>
    backend/template.yaml
    backend/samconfig.toml
    backend/README.md
  </files>
  <action>
    Create an AWS SAM template (`backend/template.yaml`) that defines:

    1. **S3 Bucket** (`InterviewIQDocsBucket`):
       - For storing uploaded .docx files, converted PDFs, and generated briefs
       - Enable CORS for frontend access
       - Add lifecycle policy for demo cleanup (30-day expiry)

    2. **DynamoDB Table** (`InterviewSessionsTable`):
       - Partition key: `sessionId` (String)
       - Sort key: `createdAt` (String)
       - On-demand billing (no capacity planning needed for hackathon)
       - GSI on `status` for querying active sessions

    3. **IAM Role** (`InterviewIQLambdaRole`):
       - Lambda basic execution (CloudWatch Logs)
       - S3 read/write on the docs bucket
       - DynamoDB CRUD on sessions table
       - Bedrock invoke model
       - Textract detect/analyze document
       - Comprehend detect entities/key phrases/sentiment
       - Step Functions start execution

    4. **Lambda Layer** (`SharedDepsLayer`):
       - Reference to local layer build artifact
       - Python 3.13 compatible

    Create `backend/samconfig.toml` with:
       - Stack name: interview-iq
       - Region: us-east-1
       - S3 bucket for SAM deployments (auto-create)
       - Capabilities: CAPABILITY_IAM

    Create `backend/README.md` with:
       - Project overview
       - Prerequisites (Python 3.13, SAM CLI, AWS CLI)
       - Setup instructions
       - Deployment commands
       - Architecture diagram (ASCII)

    IMPORTANT:
    - Use `AWS::Serverless-2016-10-31` transform
    - All resource names should use `InterviewIQ` prefix
    - Add comprehensive YAML comments explaining each resource
    - Every function and configuration must have inline documentation
    - Do NOT hardcode any model IDs — use Parameters or environment variables
  </action>
  <verify>
    cd backend && sam validate
  </verify>
  <done>
    - template.yaml passes SAM validation
    - All 4 resource types defined (S3, DynamoDB, IAM, Layer reference)
    - README.md contains setup and deployment instructions
    - All resources have documentation comments
  </done>
</task>

<task type="auto">
  <name>Build shared Lambda Layer with Python dependencies</name>
  <files>
    backend/layers/shared/requirements.txt
    backend/layers/shared/build_layer.sh
    backend/layers/shared/README.md
  </files>
  <action>
    Create the shared Lambda Layer build system:

    1. `backend/layers/shared/requirements.txt`:
       ```
       boto3>=1.35.0
       requests>=2.31.0
       beautifulsoup4>=4.12.0
       python-docx>=1.1.0
       ```

    2. `backend/layers/shared/build_layer.sh`:
       - Create `python/` directory
       - pip install from requirements.txt targeting manylinux2014_x86_64
       - Zip into `layer.zip`
       - Clean up temporary directory
       - Add docstring header explaining usage

    3. `backend/layers/shared/README.md`:
       - What the layer contains and why
       - How to build
       - How to update dependencies
       - Layer size constraints (250MB max unzipped)

    IMPORTANT:
    - Script must be idempotent (clean before build)
    - Use `--only-binary=:all:` flag for compiled packages
    - Target `python/` directory structure (Lambda Layer requirement)
  </action>
  <verify>
    cd backend/layers/shared && chmod +x build_layer.sh && bash build_layer.sh && ls -la layer.zip
  </verify>
  <done>
    - requirements.txt lists all 4 dependencies
    - build_layer.sh creates layer.zip successfully
    - layer.zip contains `python/` directory with installed packages
    - README.md documents build process
  </done>
</task>

<task type="checkpoint:human-verify">
  <name>Deploy core infrastructure to AWS</name>
  <files>
    backend/template.yaml
  </files>
  <action>
    Deploy the SAM template to AWS:
    ```bash
    cd backend
    sam build
    sam deploy --guided
    ```

    Record infrastructure outputs:
    - S3 bucket name
    - DynamoDB table name
    - Lambda role ARN
    - Lambda layer ARN

    Update `.gsd/STATE.md` with deployed resource ARNs.
  </action>
  <verify>
    aws cloudformation describe-stacks --stack-name interview-iq --query "Stacks[0].StackStatus"
  </verify>
  <done>
    - Stack status is CREATE_COMPLETE
    - S3 bucket accessible
    - DynamoDB table accessible
    - Lambda role has correct permissions
    - STATE.md updated with resource ARNs
  </done>
</task>

## Success Criteria
- [ ] SAM template validates successfully
- [ ] Lambda Layer builds with all dependencies
- [ ] CloudFormation stack deploys to us-east-1
- [ ] All resource ARNs recorded in STATE.md
