# ROADMAP.md

> **Current Phase**: Phase 2
> **Milestone**: v1.0 — Hackathon Demo
> **Cross-Cutting**: Every phase must include comprehensive documentation — JSDoc/docstrings on all functions, workflow docs, and module-level READMEs.

## Must-Haves (from SPEC)

- [ ] Company data ingestion (web scraping + sample docs)
- [ ] AI-powered brief generation (Bedrock/Claude)
- [ ] Interviewer brief with questions + conversation flow
- [ ] Interviewee pre-interview packet (PDF)
- [ ] Interviewee web form (corrections + question selection)
- [ ] Updated interview guide reflecting interviewee input
- [ ] End-to-end demo flow

## Phases

### Phase 1: Infrastructure & Data Layer
**Status**: ✅ Verified
**Objective**: Set up AWS infrastructure, React app scaffold, and data ingestion pipeline
**Time Budget**: ~12 hours
**Deliverables**:
- React app deployed to AWS Amplify with routing
- S3 bucket for document storage
- DynamoDB table for interview sessions
- Python Lambda functions with API Gateway
- Document ingestion: parse .docx sample data files with Textract
- Web scraping module: fetch public company info (AWS-native, free)
- Store processed data in S3/DynamoDB
- Comprehensive documentation for all modules

**Requirements**: Foundation for all subsequent phases

---

### Phase 2: AWS Deployment & Git Setup
**Status**: ⬜ Not Started
**Objective**: Deploy backend to AWS, push code to remote GitHub repo for team collaboration
**Time Budget**: ~2 hours
**Deliverables**:
- SAM backend deployed to AWS (Lambda, API Gateway, S3, DynamoDB, Step Functions)
- Lambda Layer built and deployed
- Frontend deployed to AWS Amplify (or ready for Amplify console connect)
- GitHub remote repo created and pushed
- `.gitignore` cleaned up (exclude `.tmp.driveupload/`, `node_modules/`, `dist/`)
- Teammate can `git clone` and run locally

**Requirements**: Phase 1 complete (verified ✅)

---

### Phase 3: AI Intelligence Engine
**Status**: ⬜ Not Started
**Objective**: Build the core AI pipeline that analyzes company data and generates interview materials
**Time Budget**: ~20 hours
**Deliverables**:
- Bedrock/Claude integration for company analysis
- Company profile generation from scraped + uploaded data
- Intelligent question generation following interview best practices
- Conversation flow/structure generation
- Comprehend integration for entity/sentiment extraction from source docs
- Interviewer brief assembly (structured JSON → formatted output)
- Interviewee packet assembly (subset of brief + question menu)

**Requirements**: REQ from Phase 1 (data ingestion working)

---

### Phase 4: Frontend & Two-Stage Workflow
**Status**: ⬜ Not Started
**Objective**: Build the complete UI and implement both stages of the interview workflow
**Time Budget**: ~20 hours
**Deliverables**:
- **Interviewer Dashboard**: Input company name/URL → trigger analysis → view brief
- **PDF Generation**: Render interviewer brief and interviewee packet as downloadable PDFs
- **Interviewee Portal**: Unique shareable URL → view AI findings → correct inaccuracies → select 2-3 questions via web form
- **Updated Interview Guide**: Interviewer view that incorporates interviewee's corrections and selected questions
- Responsive, polished UI with professional styling

**Requirements**: REQ from Phase 3 (AI engine producing structured output)

---

### Phase 5: Integration, Polish & Demo Prep
**Status**: ⬜ Not Started
**Objective**: End-to-end integration testing, UI polish, and hackathon demo preparation
**Time Budget**: ~20 hours
**Deliverables**:
- Full workflow smoke test with sample data
- Error handling and loading states
- UI polish: animations, transitions, professional look
- Demo script preparation
- Edge case handling (missing data, API failures)
- Performance optimization (caching, parallel requests)
- Demo recording / presentation prep

**Requirements**: All previous phases complete
