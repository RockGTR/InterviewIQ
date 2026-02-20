---
phase: 2
level: 1
researched_at: 2026-02-20
---

# Phase 2 Research — AWS Deployment & Git Setup

## Questions Investigated

1. What tools need to be installed for AWS deployment?
2. What is the correct order of operations for SAM deployment?
3. How to connect Amplify to the GitHub repo?

## Findings

### Current Machine State

| Tool | Status | Action Needed |
|------|--------|---------------|
| Git | ✅ Installed | — |
| GitHub CLI (`gh`) | ✅ v2.86.0 | — |
| GitHub Remote | ✅ https://github.com/RockGTR/InterviewIQ | — |
| AWS CLI | ❌ Not installed | `brew install awscli` |
| SAM CLI | ❌ Not installed | `brew install aws-sam-cli` |
| Python 3.13 | ✅ Available | — |
| Node.js | ✅ Available | — |

### Installation Steps (macOS)

#### Step 1: Install AWS CLI
```bash
brew install awscli
aws --version
```

#### Step 2: Configure AWS Credentials
```bash
aws configure
# Enter:
#   AWS Access Key ID: (from hackathon credits / AWS console)
#   AWS Secret Access Key: (from AWS console)
#   Default region: us-west-2
#   Default output format: json
```

To get credentials:
1. Log into AWS Console → IAM → Your user → Security credentials
2. Create Access Key → Command Line Interface
3. Download the key pair

#### Step 3: Install SAM CLI
```bash
brew install aws-sam-cli
sam --version
```

#### Step 4: Deploy Backend
```bash
cd backend
sam build
sam deploy --guided
# This will walk through configuration (stack name, region, etc.)
```

#### Step 5: Connect Amplify to GitHub
1. Go to AWS Console → AWS Amplify
2. Click "New app" → "Host web app"
3. Connect to GitHub → Select `RockGTR/InterviewIQ`
4. Set build settings:
   - App directory: `frontend`
   - Build command: `npm run build`
   - Output directory: `dist`
5. Deploy

### For Your Teammate

After you push, your friend can:
```bash
git clone https://github.com/RockGTR/InterviewIQ.git
cd InterviewIQ/frontend
npm install
npm run dev
```

For backend development, they'll also need AWS CLI configured with the same account credentials.

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package manager | Homebrew | Standard for macOS |
| Region | us-west-2 | Matches SAM template config |
| Amplify deploy | GitHub-connected | Auto-deploy on push |

## Ready for Planning
- [x] Questions answered
- [x] Dependencies identified (AWS CLI, SAM CLI)
- [x] Installation steps documented
