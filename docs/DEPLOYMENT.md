# Deployment Guide

## Prerequisites

| Tool | Install | Verify |
|------|---------|--------|
| AWS CLI v2 | `brew install awscli` | `aws --version` |
| SAM CLI | `brew install aws-sam-cli` | `sam --version` |
| Node.js 18+ | `brew install node` | `node --version` |
| Python 3.13+ | `brew install python@3.13` | `python3 --version` |

## AWS Credentials

```bash
# Option A: aws configure (permanent)
aws configure
# Access Key ID, Secret Access Key, Region: us-west-2, Output: json

# Option B: Environment variables (temporary/session)
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."        # Only for temporary credentials
export AWS_DEFAULT_REGION="us-west-2"

# Verify
aws sts get-caller-identity
```

## Backend Deployment (SAM)

### First Deploy
```bash
cd backend
sam build
sam deploy --stack-name interview-iq \
  --region us-west-2 \
  --resolve-s3 \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
  --no-confirm-changeset
```

### Subsequent Deploys
```bash
cd backend
sam build && sam deploy --no-confirm-changeset
```

### Updating Shared Modules
When you modify files in `backend/shared/`:
```bash
# 1. Copy to layer source
cp backend/shared/*.py backend/layers/shared/python/shared/

# 2. Rebuild and deploy
cd backend && sam build && sam deploy --no-confirm-changeset
```

### Stack Outputs
After deployment, note these outputs:
```
ApiUrl:          https://XXXXXXX.execute-api.us-west-2.amazonaws.com/dev
BucketName:      interview-iq-docs-ACCOUNT-us-west-2
TableName:       interview-iq-sessions-interview-iq
StateMachineArn: arn:aws:states:us-west-2:ACCOUNT:stateMachine:interview-iq-pipeline
SharedLayerArn:  arn:aws:lambda:us-west-2:ACCOUNT:layer:interview-iq-shared-deps:N
```

## Frontend Deployment (Amplify)

### Option A: Amplify Console (Recommended)
1. Go to [AWS Amplify Console](https://us-west-2.console.aws.amazon.com/amplify/)
2. Click **New app** → **Host web app**
3. Connect to **GitHub** → Select `RockGTR/InterviewIQ`
4. Configure build settings:
   - App directory: `frontend`
   - Build command: `npm run build`
   - Output directory: `dist`
5. Deploy

### Option B: Manual (S3 + CloudFront)
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket-name/ --delete
```

## Environment Configuration

### Frontend API URL
Update `frontend/src/services/api.js`:
```javascript
const API_BASE = 'https://YOUR-API-ID.execute-api.us-west-2.amazonaws.com/dev';
```

### Backend Variables (auto-set by SAM)
These are automatically injected into Lambda via `template.yaml` Globals:
- `TABLE_NAME` — DynamoDB table name
- `BUCKET_NAME` — S3 bucket name
- `MODEL_ID` — Bedrock model ID
- `BEDROCK_REGION` — Region for Bedrock API

## Teardown
```bash
# Delete CloudFormation stack (removes all resources)
aws cloudformation delete-stack --stack-name interview-iq --region us-west-2
```
