# InterviewIQ Backend

> AI-Powered Interview Intelligence System — AWS Serverless Backend

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────────────────┐
│  React App  │────▶│ API Gateway  │────▶│  Step Functions State Machine   │
│  (Amplify)  │     │  REST API    │     │                                 │
└─────────────┘     └──────────────┘     │  ┌─────────┐  ┌─────────────┐  │
                                         │  │ Scrape   │  │ Parse Docs  │  │
                                         │  │ Company  │  │ (Textract)  │  │
                                         │  └────┬─────┘  └──────┬──────┘  │
                                         │       └───────┬───────┘         │
                                         │               ▼                 │
                                         │       ┌───────────────┐         │
                                         │       │   Analyze     │         │
                                         │       │ (Comprehend)  │         │
                                         │       └───────┬───────┘         │
                                         │               ▼                 │
                                         │       ┌───────────────┐         │
                                         │       │   Generate    │         │
                                         │       │ Brief (Claude)│         │
                                         │       └───────────────┘         │
                                         └─────────────────────────────────┘
                                                        │
                                         ┌──────────────┼──────────────┐
                                         ▼              ▼              ▼
                                    ┌─────────┐  ┌──────────┐  ┌──────────┐
                                    │   S3    │  │ DynamoDB │  │ Bedrock  │
                                    │  Docs   │  │ Sessions │  │  Claude  │
                                    └─────────┘  └──────────┘  └──────────┘
```

## Prerequisites

- **Python 3.13** — Lambda runtime
- **AWS SAM CLI** — `pip install aws-sam-cli`
- **AWS CLI** — configured with credentials (`aws configure`)
- **Docker** — required for `sam build` with native dependencies

## Quick Start

```bash
# 1. Build the Lambda Layer
cd layers/shared
chmod +x build_layer.sh
./build_layer.sh

# 2. Build all Lambda functions
cd ../..
sam build

# 3. Deploy to AWS
sam deploy --guided

# 4. Note the outputs (API URL, bucket name, etc.)
```

## Project Structure

```
backend/
├── template.yaml              # SAM template (all AWS resources)
├── samconfig.toml              # Deployment configuration
├── functions/                  # Lambda function handlers
│   ├── health/                 # GET /health
│   ├── create_session/         # POST /sessions
│   ├── get_session/            # GET /sessions/{id}
│   ├── scrape_company/         # POST /scrape
│   ├── parse_document/         # POST /parse
│   ├── analyze_company/        # POST /analyze
│   ├── generate_brief/         # POST /generate
│   ├── submit_feedback/        # POST /sessions/{id}/feedback
│   └── start_pipeline/         # POST /pipeline
├── shared/                     # Shared service modules
│   ├── dynamo_service.py       # DynamoDB operations
│   ├── s3_service.py           # S3 operations
│   ├── bedrock_service.py      # Bedrock/Claude integration
│   ├── textract_service.py     # Textract document processing
│   ├── comprehend_service.py   # NLP analysis
│   └── scraper_service.py      # Web scraping
├── layers/shared/              # Lambda Layer (dependencies)
├── statemachine/               # Step Functions ASL definition
├── scripts/                    # Utility scripts
└── data/                       # Mock/seed data
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | System health check |
| POST | `/sessions` | Create interview session |
| GET | `/sessions/{id}` | Get session data |
| POST | `/scrape` | Scrape company info |
| POST | `/parse` | Parse uploaded document |
| POST | `/analyze` | Analyze with Comprehend |
| POST | `/generate` | Generate brief with Claude |
| POST | `/sessions/{id}/feedback` | Submit interviewee feedback |
| POST | `/pipeline` | Start full pipeline |
| GET | `/pipeline/{id}` | Check pipeline status |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TABLE_NAME` | DynamoDB table name (auto-set) |
| `BUCKET_NAME` | S3 bucket name (auto-set) |
| `MODEL_ID` | Bedrock model identifier |
| `BEDROCK_REGION` | AWS region for Bedrock |
| `STATE_MACHINE_ARN` | Step Functions ARN (pipeline only) |

## Deployment

```bash
# Validate template
sam validate

# Build
sam build

# Deploy (first time — interactive)
sam deploy --guided

# Deploy (subsequent — uses saved config)
sam deploy
```
