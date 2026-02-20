# Interview Workflow Guide

## Overview

InterviewIQ is a two-stage interview intelligence system. It uses AI to analyze company data, then lets both the interviewer and interviewee collaborate before the interview happens.

---

## Stage 1: Interviewer Preparation

### Step 1 — Enter Company Info
The interviewer opens InterviewIQ and enters:
- **Company name** (required) — e.g., "GridFlex Energy"
- **Company URL** (optional) — direct website link

### Step 2 — System Gathers Intelligence
The system automatically:
1. **Scrapes** the company website for public info (about page, team, products, news)
2. **Parses** any uploaded documents (.docx resumes, company profiles)
3. **Analyzes** all text using Amazon Comprehend (entities, sentiment, key phrases)
4. **Generates** a complete interview brief using Amazon Bedrock (Claude AI)

### Step 3 — Review the Brief
The interviewer receives:
- **Company Overview** — AI-generated profile from all gathered data
- **Tailored Questions** — Interview questions customized to the company, with follow-up prompts
- **Conversation Flow** — Suggested structure for the interview (opening, core, closing)
- **Key Talking Points** — Important topics to cover based on analysis

---

## Stage 2: Interviewee Review

### Step 4 — Share the Link
The interviewer shares a unique URL with the interviewee:
```
https://app.interviewiq.com/interview/{sessionId}
```

### Step 5 — Interviewee Reviews AI Findings
The interviewee sees:
- What the AI found about their company
- Proposed discussion topics and questions

### Step 6 — Interviewee Provides Input
The interviewee can:
- **Correct inaccuracies** — Fix anything the AI got wrong
- **Select questions** — Choose 2-3 questions they'd prefer to discuss
- **Add notes** — Share additional context the interviewer should know

### Step 7 — Updated Interview Guide
The interviewer receives an updated guide that incorporates:
- All corrections from the interviewee
- The interviewee's preferred questions (highlighted)
- Any additional context provided

---

## The Result

Both sides come prepared:
- **Interviewer** has researched, relevant questions and knows what matters to the interviewee
- **Interviewee** has reviewed what will be discussed and had input on the topics

This replaces generic "tell me about yourself" interviews with informed, productive conversations.

---

## Supported Company Data Sources

| Source | Method | Reliability |
|--------|--------|-------------|
| Company website | Web scraping (requests + BeautifulSoup) | Variable |
| Mock data | 5 pre-loaded TX companies | 100% (demo) |
| Uploaded .docx | python-docx extraction | High |
| Uploaded PDF | Amazon Textract OCR | High |

### Pre-loaded Mock Companies
For hackathon demos, these companies have complete mock profiles:
1. GridFlex Energy — Renewable energy tech
2. LoneStar Precision — Advanced manufacturing
3. Texas Mechanical — Industrial solutions
4. LaunchStack Tech — SaaS platform
5. PrairieLogic AG — Agricultural technology
