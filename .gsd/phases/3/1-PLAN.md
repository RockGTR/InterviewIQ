---
phase: 3
plan: 1
wave: 1
---

# Plan 3.1: Implement Bedrock Prompt Engineering

## Objective
Replace the 4 stub methods in `bedrock_service.py` with real Claude prompt engineering using the chained approach (Profile → Questions → Brief → Packet). This is the core AI engine of InterviewIQ.

## Context
- .gsd/phases/3/RESEARCH.md — Chaining decision, JSON schema
- .gsd/DECISIONS.md — ADR-011 through ADR-013
- backend/shared/bedrock_service.py — Has working `invoke_claude()`, 4 stub methods
- backend/data/mock_companies.json — 5 sample companies for testing prompts

## Tasks

<task type="auto">
  <name>Implement generate_company_profile()</name>
  <files>backend/shared/bedrock_service.py</files>
  <action>
    Replace the `generate_company_profile` stub (lines 117-160) with a real implementation that:
    1. Builds a system prompt instructing Claude to act as a company research analyst
    2. Constructs a user prompt containing: scraped_data (JSON), parsed_documents (list of text), analysis_results (entities, key phrases, sentiment from Comprehend)
    3. Instructs Claude to return ONLY valid JSON matching this schema:
       ```json
       {
         "name": "string",
         "industry": "string",
         "region": "string",
         "stage": "string (startup|growth|mature|enterprise)",
         "description": "string (2-3 sentences)",
         "business_model": { "type": "string", "revenue_streams": ["string"] },
         "key_people": [{"name": "string", "role": "string"}],
         "competitors": ["string"],
         "key_initiatives": ["string"],
         "risks": ["string"],
         "hypotheses": ["string (informed guesses about the company)"],
         "confidence_level": "string (High|Medium|Low with explanation)"
       }
       ```
    4. Parse the JSON response with `json.loads()`, with a fallback that attempts to extract JSON from markdown code blocks
    5. Use temperature=0.3 for factual accuracy
    - Do NOT include example company data in the prompt (wastes tokens)
    - Do NOT use f-strings for the system prompt (use .format() or concatenation to avoid {} conflicts with JSON)
  </action>
  <verify>python3 -c "from shared.bedrock_service import BedrockService; print('import OK')"</verify>
  <done>generate_company_profile() sends a real prompt to Claude and parses structured JSON response</done>
</task>

<task type="auto">
  <name>Implement generate_questions()</name>
  <files>backend/shared/bedrock_service.py</files>
  <action>
    Replace the `generate_questions` stub (lines 162-196) with a real implementation that:
    1. Takes the company_profile dict (from step 1) and optional analysis_results
    2. Builds a system prompt instructing Claude to act as an expert interviewer
    3. Instructs Claude to generate `num_questions` (default 10) questions following the two-stage methodology:
       - 3-4 surface-level confirmation questions (warm up, build rapport)
       - 4-5 deep probing questions (business model, market strategy, challenges)
       - 2-3 "what did we get wrong?" questions (inviting corrections)
    4. Each question must follow this JSON schema:
       ```json
       {
         "id": "q1",
         "question": "string",
         "category": "string (rapport|business_model|market|culture|challenges|corrections)",
         "depth": "string (surface|deep)",
         "rationale": "string (why this question matters)",
         "follow_ups": ["string"]
       }
       ```
    5. Use temperature=0.7 for creative but relevant questions
    6. Parse JSON array response with fallback extraction
    - Do NOT generate generic questions that could apply to any company
    - DO reference specific facts from the company profile in the rationale
  </action>
  <verify>python3 -c "from shared.bedrock_service import BedrockService; print('import OK')"</verify>
  <done>generate_questions() produces 10 company-specific questions with categories, depth levels, and follow-ups</done>
</task>

<task type="auto">
  <name>Implement generate_interviewer_brief() and generate_interviewee_packet()</name>
  <files>backend/shared/bedrock_service.py</files>
  <action>
    Replace both stub methods:

    **generate_interviewer_brief()** (lines 198-238):
    1. Takes company_profile, questions list, and analysis_results
    2. Builds a prompt asking Claude to assemble a complete interviewer preparation document
    3. JSON schema:
       ```json
       {
         "executive_summary": "string (3-4 sentences)",
         "company_overview": { ... profile fields ... },
         "industry_context": "string (market trends, competitive landscape)",
         "pre_call_hypotheses": ["string (things to validate in interview)"],
         "questions": [{ ... question objects ... }],
         "conversation_flow": {
           "opening": "string (first 5 minutes guidance)",
           "core": ["string (topic progression)"],
           "closing": "string (wrap up strategy)"
         },
         "key_facts": ["string (quick-reference facts)"]
       }
       ```
    4. Use temperature=0.5 (balanced)

    **generate_interviewee_packet()** (lines 240-271):
    1. Takes company_profile and questions
    2. Builds a prompt asking Claude to create a friendly, professional packet for the interviewee
    3. JSON schema:
       ```json
       {
         "ai_findings": {
           "company_summary": "string",
           "key_facts": ["string"],
           "topics_identified": ["string"]
         },
         "questions_menu": [{ "id": "q1", "question": "string", "topic": "string" }],
         "invitation_text": "string (warm, professional message asking for corrections)"
       }
       ```
    4. Use temperature=0.6
    - The interviewee packet should be SHORTER and more friendly than the interviewer brief
    - Do NOT include rationale or follow-ups in the interviewee questions (those are interviewer-only)
  </action>
  <verify>python3 -c "from shared.bedrock_service import BedrockService; print('import OK')"</verify>
  <done>Both methods produce structured JSON. Interviewer brief has all 7 sections. Interviewee packet has 3 sections.</done>
</task>

## Success Criteria
- [ ] All 4 bedrock_service.py methods call invoke_claude() with engineered prompts
- [ ] All methods return parsed JSON matching the documented schemas
- [ ] JSON parsing includes fallback extraction from markdown code blocks
- [ ] No TODO/stub comments remain in bedrock_service.py
