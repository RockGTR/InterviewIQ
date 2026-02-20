# Contributing to InterviewIQ

## Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/RockGTR/InterviewIQ.git
cd InterviewIQ
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev        # → http://localhost:5173
```

### 3. Backend Setup
```bash
# Install AWS CLI + SAM CLI
brew install awscli aws-sam-cli

# Configure credentials (get from team lead)
aws configure

# Build and deploy
cd backend
sam build
sam deploy --stack-name interview-iq --region us-west-2 \
  --resolve-s3 --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
  --no-confirm-changeset
```

## Development Workflow

### Branch Strategy
```
master          ← production branch (deployed)
 └── feature/*  ← feature branches
```

### Making Changes

**Frontend changes:**
```bash
cd frontend
npm run dev          # Live reload at localhost:5173
# Make changes → test in browser → commit
```

**Backend handler changes:**
```bash
cd backend
# Edit functions/{name}/handler.py
sam build && sam deploy --no-confirm-changeset
# Test: curl https://API_URL/endpoint
```

**Shared module changes** (critical — extra step required):
```bash
# 1. Edit backend/shared/{module}.py
# 2. Copy to layer
cp backend/shared/*.py backend/layers/shared/python/shared/
# 3. Build and deploy
cd backend && sam build && sam deploy --no-confirm-changeset
```

### Commit Conventions
```
feat(phase-N): description       # New feature
fix(phase-N): description        # Bug fix
docs(phase-N): description       # Documentation
refactor: description            # Code restructure
```

## Project Structure at a Glance

| Directory | What It Does | When to Edit |
|-----------|-------------|--------------|
| `frontend/src/pages/` | React page components | UI changes |
| `frontend/src/services/api.js` | API client | New endpoints |
| `backend/functions/*/handler.py` | Lambda handlers | Backend logic |
| `backend/shared/*.py` | Shared services | Cross-cutting logic |
| `backend/template.yaml` | AWS resources | New resources/permissions |
| `backend/data/` | Mock data | Test data |

## Testing

### Health Check
```bash
curl -s https://l8xc3yrptf.execute-api.us-west-2.amazonaws.com/dev/health | python3 -m json.tool
```

### SAM Local Invoke
```bash
cd backend
sam build
sam local invoke HealthFunction
```

## Key Things to Know

1. **Lambda Layer** — All shared Python modules (`bedrock_service.py`, `dynamo_service.py`, etc.) are packaged in a Lambda Layer. If you change them, you must copy to `layers/shared/python/shared/` before deploying.

2. **Mock Data** — `backend/data/mock_companies.json` has 5 pre-loaded companies. The scraper falls back to this data if live scraping fails.

3. **Temporary Credentials** — If using AWS Academy / hackathon creds, they expire. Re-export `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` when they expire.

4. **Frontend API URL** — Set in `frontend/src/services/api.js`. Update after deployment to match your API Gateway URL.
