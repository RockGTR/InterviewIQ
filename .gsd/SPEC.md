# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision

Build an AI-powered Interview Intelligence System ("InterviewIQ") that enables Texas A&M students, faculty, and staff to conduct high-quality business intelligence interviews with minimal preparation. The system ingests public and proprietary data about a target company, generates comprehensive interviewer briefs and pre-interview packets, and facilitates a two-stage interview workflow where AI-generated insights serve as both preparation tool and conversation catalyst — using the "what did AI get wrong?" approach to transform cold outreach into warm, productive conversations.

## Goals

1. **Rapid Preparation** — Enable effective interviews with ≤5 minutes of prep time by auto-generating comprehensive company briefs
2. **Intelligent Question Generation** — Produce research-backed, well-crafted interview questions that demonstrate depth and follow best practices
3. **Two-Stage Interview Workflow** — Implement the pre-interview packet → interview flow where interviewees review AI findings, correct inaccuracies, and select discussion topics
4. **PDF Packet Generation** — Generate polished, downloadable PDF documents for both interviewer briefs and interviewee packets
5. **Automated Data Collection** — Scrape and synthesize public web data about target companies using automated tools
6. **Proprietary Data Integration** — Ingest and leverage Texas A&M-specific data (case files, reports) alongside public sources

## Non-Goals (Out of Scope)

- LinkedIn scraping (ToS risk, unreliable for hackathon)
- User authentication / multi-tenancy (demo mode, single-user)
- Real-time interview transcription or recording
- CRM integration or interview data persistence beyond session
- Mobile-native app (web-responsive is sufficient)
- Email delivery of packets (PDF download instead)

## Users

- **Primary: Interviewers** — Texas A&M students, faculty, and staff who need to prepare for business intelligence interviews quickly
- **Secondary: Interviewees** — Texas business representatives who receive pre-interview packets, review AI findings, and select discussion questions via a web form

## System Overview

### Data Flow
```
Company Name/URL → Web Scraping + Sample Data Ingestion
     ↓
AI Analysis (Bedrock/Claude) → Company Profile + Intelligence
     ↓
Split into two outputs:
  → Interviewer Brief (PDF): Full context, questions, conversation flow
  → Interviewee Packet (PDF + Web Form): AI findings, question selection
     ↓
Interviewee responds via web form → Corrections + selected questions
     ↓
Updated Interview Guide for interviewer with interviewee preferences
```

### Two-Stage Workflow
1. **Pre-Interview Stage**: Interviewer enters company info → system generates briefs → interviewee receives packet via unique URL → interviewee reviews, corrects, and selects questions via web form
2. **Interview Stage**: Interviewer sees updated guide with interviewee's corrections and selected questions → warm opening using "what did AI misunderstand?" → flows through selected questions → has reserve questions ready

## Constraints

- **Timeline**: 12-hour hackathon — aggressive scoping required
- **Team**: 4 developers, all AWS-experienced
- **Stack**: React frontend (AWS Amplify), AWS Lambda, API Gateway, S3, DynamoDB, Amazon Bedrock (Claude), Amazon Comprehend, Amazon Textract
- **Data**: 5 sample hackathon case files (.docx) in `data/` directory + automated web scraping for public info
- **No authentication**: Demo-quality, single-user experience
- **Budget**: AWS Free Tier / hackathon credits

## Success Criteria

- [ ] Interviewer enters a company name/URL and receives a comprehensive brief within 60 seconds
- [ ] Generated questions demonstrate research depth and follow interview best practices
- [ ] Pre-interview packet is downloadable as a polished PDF
- [ ] Interviewee can access a unique URL, review AI findings, correct inaccuracies, and select 2-3 preferred questions
- [ ] Interviewer sees updated guide reflecting interviewee's input
- [ ] System works end-to-end for demo with sample data
- [ ] Full workflow completable with ≤5 minutes of interviewer preparation
