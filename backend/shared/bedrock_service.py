"""
Bedrock Service — AI Generation via Amazon Bedrock/Claude
==========================================================

Provides methods for invoking Amazon Bedrock's Claude model to generate
interview intelligence: company profiles, interview questions, conversation
flows, and complete interviewer/interviewee briefs.

Uses a chained prompt approach (Profile → Questions → Brief → Packet)
for maximum output quality. Each method calls invoke_claude() with
engineered system prompts and strict JSON output schemas.

Usage:
    >>> from shared.bedrock_service import BedrockService
    >>> bedrock = BedrockService()
    >>> profile = bedrock.generate_company_profile(scraped_data, parsed_docs)
    >>> questions = bedrock.generate_questions(profile, analysis_results)
"""

import os
import re
import json
import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BedrockService:
    """
    Service class for Amazon Bedrock AI generation operations.

    Wraps the Bedrock Runtime API for invoking Claude models with
    structured prompts optimized for interview intelligence generation.

    Attributes:
        model_id (str): Bedrock model identifier (e.g., Claude 3.5 Sonnet).
        client: boto3 Bedrock Runtime client.
    """

    def __init__(
        self,
        model_id: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize Bedrock service with model configuration.

        Args:
            model_id: Bedrock model ID. Defaults to MODEL_ID env var.
            region: AWS region for Bedrock. Defaults to BEDROCK_REGION env var.
        """
        self.model_id = model_id or os.environ.get(
            "MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        bedrock_region = region or os.environ.get("BEDROCK_REGION", "us-east-1")
        self.client = boto3.client("bedrock-runtime", region_name=bedrock_region)
        logger.info("BedrockService initialized with model: %s in %s", self.model_id, bedrock_region)

    def invoke_claude(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Invoke Claude model with a prompt and return the text response.

        This is the low-level method that handles the Bedrock API call.
        Higher-level methods (generate_company_profile, generate_questions)
        build appropriate prompts and call this method.

        Args:
            prompt: The user message to send to Claude.
            system_prompt: Optional system-level instructions.
            max_tokens: Maximum tokens in the response.
            temperature: Creativity/randomness (0.0-1.0).

        Returns:
            str: The generated text response from Claude.

        Raises:
            ClientError: If Bedrock API call fails.
        """
        messages = [{"role": "user", "content": prompt}]

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_prompt:
            body["system"] = system_prompt

        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        result = json.loads(response["body"].read())
        text = result["content"][0]["text"]
        logger.info(
            "Claude response: %d chars, %d input tokens, %d output tokens",
            len(text),
            result.get("usage", {}).get("input_tokens", 0),
            result.get("usage", {}).get("output_tokens", 0),
        )
        return text

    def _parse_json_response(self, text: str) -> dict | list:
        """
        Parse JSON from Claude's response, handling markdown code blocks.

        Claude sometimes wraps JSON in ```json ... ``` blocks. This method
        extracts and parses the JSON regardless of formatting.

        Args:
            text: Raw text response from Claude.

        Returns:
            dict or list: Parsed JSON object.

        Raises:
            ValueError: If no valid JSON can be extracted.
        """
        # Try direct parse first
        stripped = text.strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code blocks
        pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
        match = re.search(pattern, stripped, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Try finding the first { or [ and matching to last } or ]
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start_idx = stripped.find(start_char)
            end_idx = stripped.rfind(end_char)
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(stripped[start_idx : end_idx + 1])
                except json.JSONDecodeError:
                    pass

        raise ValueError("Could not extract valid JSON from Claude response")

    def generate_company_profile(
        self,
        scraped_data: dict,
        parsed_documents: list,
        analysis_results: Optional[dict] = None,
    ) -> dict:
        """
        Generate a comprehensive company profile from collected data.

        Synthesizes web-scraped data, parsed documents, and NLP analysis
        into a structured company profile.

        Args:
            scraped_data: Raw data from web scraping.
            parsed_documents: List of extracted text from uploaded documents.
            analysis_results: Optional NLP analysis (entities, key phrases).

        Returns:
            dict: Structured company profile.
        """
        system_prompt = (
            "You are a company research analyst preparing intelligence for an interview. "
            "Analyze all provided data and produce a comprehensive company profile. "
            "You MUST respond with ONLY valid JSON — no markdown, no explanation, no preamble. "
            "Use the exact schema provided. If data is missing, make reasonable inferences "
            "and mark confidence_level accordingly."
        )

        # Build context sections
        context_parts = []
        context_parts.append("=== SCRAPED WEB DATA ===")
        context_parts.append(json.dumps(scraped_data, indent=2, default=str))

        if parsed_documents:
            context_parts.append("\n=== PARSED DOCUMENTS ===")
            for i, doc in enumerate(parsed_documents):
                doc_text = doc if isinstance(doc, str) else json.dumps(doc, default=str)
                context_parts.append("--- Document {} ---\n{}".format(i + 1, doc_text[:3000]))

        if analysis_results:
            context_parts.append("\n=== NLP ANALYSIS (Amazon Comprehend) ===")
            context_parts.append(json.dumps(analysis_results, indent=2, default=str))

        user_prompt = (
            "Analyze the following data and generate a company profile.\n\n"
            + "\n".join(context_parts)
            + '\n\nRespond with ONLY this JSON schema:\n'
            '{\n'
            '  "name": "string",\n'
            '  "industry": "string",\n'
            '  "region": "string",\n'
            '  "stage": "startup|growth|mature|enterprise",\n'
            '  "description": "2-3 sentence overview",\n'
            '  "business_model": { "type": "string", "revenue_streams": ["string"] },\n'
            '  "key_people": [{ "name": "string", "role": "string" }],\n'
            '  "competitors": ["string"],\n'
            '  "key_initiatives": ["string"],\n'
            '  "risks": ["string"],\n'
            '  "hypotheses": ["informed guesses about the company to validate in interview"],\n'
            '  "confidence_level": "High|Medium|Low — brief explanation"\n'
            '}'
        )

        logger.info("Generating company profile via Bedrock")
        response_text = self.invoke_claude(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.3,
        )

        try:
            profile = self._parse_json_response(response_text)
            logger.info("Company profile generated: %s", profile.get("name", "unknown"))
            return profile
        except (ValueError, AttributeError) as e:
            logger.error("Failed to parse company profile JSON: %s", e)
            return {
                "name": scraped_data.get("company_name", scraped_data.get("name", "Unknown")),
                "industry": "Unknown",
                "region": "Unknown",
                "stage": "Unknown",
                "description": response_text[:500],
                "business_model": {},
                "key_people": [],
                "competitors": [],
                "key_initiatives": [],
                "risks": [],
                "hypotheses": [],
                "confidence_level": "Low — JSON parse failed, raw text returned",
            }

    def generate_questions(
        self,
        company_profile: dict,
        analysis_results: Optional[dict] = None,
        num_questions: int = 10,
    ) -> list:
        """
        Generate interview questions following best practices.

        Produces questions in three tiers: surface-level rapport builders,
        deep probing questions, and correction-inviting questions.

        Args:
            company_profile: Structured company profile.
            analysis_results: Optional NLP analysis for context.
            num_questions: Number of questions to generate (default: 10).

        Returns:
            list: List of question dicts with id, question, category,
                  depth, rationale, and follow_ups.
        """
        system_prompt = (
            "You are an expert interviewer who prepares insightful, company-specific questions. "
            "You follow a three-tier methodology:\n"
            "1. RAPPORT (3-4 questions): Surface-level questions that show you did research. "
            "These warm up the conversation and build trust.\n"
            "2. DEEP PROBING (4-5 questions): Questions about business model, strategy, "
            "market positioning, and challenges that reveal hidden insights.\n"
            "3. CORRECTIONS (2-3 questions): Questions that acknowledge potential AI inaccuracies "
            "and invite the interviewee to correct your understanding.\n\n"
            "Every question MUST reference specific facts from the company profile. "
            "Never generate generic questions that could apply to any company. "
            "You MUST respond with ONLY a valid JSON array — no markdown, no explanation."
        )

        context_parts = []
        context_parts.append("=== COMPANY PROFILE ===")
        context_parts.append(json.dumps(company_profile, indent=2, default=str))

        if analysis_results:
            context_parts.append("\n=== NLP ANALYSIS ===")
            entities = analysis_results.get("entities", [])[:15]
            phrases = analysis_results.get("key_phrases", [])[:15]
            context_parts.append("Top entities: " + json.dumps(entities, default=str))
            context_parts.append("Top key phrases: " + json.dumps(phrases, default=str))

        user_prompt = (
            "Generate exactly {} interview questions for this company.\n\n".format(num_questions)
            + "\n".join(context_parts)
            + '\n\nRespond with ONLY a JSON array. Each element must match:\n'
            '[\n'
            '  {\n'
            '    "id": "q1",\n'
            '    "question": "string",\n'
            '    "category": "rapport|business_model|market|culture|challenges|corrections",\n'
            '    "depth": "surface|deep",\n'
            '    "rationale": "why this question matters for THIS specific company",\n'
            '    "follow_ups": ["follow-up question 1", "follow-up question 2"]\n'
            '  }\n'
            ']'
        )

        logger.info("Generating %d interview questions via Bedrock", num_questions)
        response_text = self.invoke_claude(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.7,
        )

        try:
            questions = self._parse_json_response(response_text)
            if isinstance(questions, list):
                logger.info("Generated %d questions", len(questions))
                return questions
            logger.warning("Expected list, got %s", type(questions))
            return []
        except (ValueError, AttributeError) as e:
            logger.error("Failed to parse questions JSON: %s", e)
            return []

    def generate_interviewer_brief(
        self,
        company_profile: dict,
        questions: list,
        analysis_results: Optional[dict] = None,
    ) -> dict:
        """
        Generate the complete interviewer brief document.

        Assembles all generated content into a structured brief that
        an interviewer can read in 5 minutes to prepare.

        Args:
            company_profile: Structured company profile.
            questions: Generated interview questions.
            analysis_results: Optional NLP analysis.

        Returns:
            dict: Complete interviewer brief with 7 sections.
        """
        system_prompt = (
            "You are assembling a professional interviewer preparation brief. "
            "The brief should be concise enough to read in 5 minutes but comprehensive "
            "enough to conduct an informed interview. "
            "You MUST respond with ONLY valid JSON — no markdown, no explanation."
        )

        user_prompt = (
            "Create an interviewer brief from the following data.\n\n"
            "=== COMPANY PROFILE ===\n"
            + json.dumps(company_profile, indent=2, default=str)
            + "\n\n=== QUESTIONS ===\n"
            + json.dumps(questions, indent=2, default=str)
            + ("\n\n=== NLP ANALYSIS ===\n" + json.dumps(analysis_results, indent=2, default=str) if analysis_results else "")
            + '\n\nRespond with ONLY this JSON schema:\n'
            '{\n'
            '  "executive_summary": "3-4 sentence overview of who this company is and why this interview matters",\n'
            '  "company_overview": { ... profile fields ... },\n'
            '  "industry_context": "2-3 sentences on market trends and competitive landscape",\n'
            '  "pre_call_hypotheses": ["things to validate during the interview"],\n'
            '  "questions": [{ ... question objects as provided ... }],\n'
            '  "conversation_flow": {\n'
            '    "opening": "guidance for the first 5 minutes",\n'
            '    "core": ["topic 1 to cover", "topic 2", "topic 3"],\n'
            '    "closing": "wrap up strategy and next steps"\n'
            '  },\n'
            '  "key_facts": ["quick-reference facts for the interviewer"]\n'
            '}'
        )

        logger.info("Generating interviewer brief via Bedrock")
        response_text = self.invoke_claude(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.5,
        )

        try:
            brief = self._parse_json_response(response_text)
            logger.info("Interviewer brief generated with %d sections", len(brief))
            return brief
        except (ValueError, AttributeError) as e:
            logger.error("Failed to parse brief JSON: %s", e)
            return {
                "executive_summary": "Brief generation encountered a parsing error.",
                "company_overview": company_profile,
                "industry_context": "",
                "pre_call_hypotheses": [],
                "questions": questions,
                "conversation_flow": {"opening": "", "core": [], "closing": ""},
                "key_facts": [],
            }

    def generate_interviewee_packet(
        self,
        company_profile: dict,
        questions: list,
    ) -> dict:
        """
        Generate the pre-interview packet for the interviewee.

        Creates a friendly, professional document showing what AI discovered
        and inviting corrections and question selection.

        Args:
            company_profile: AI-generated company profile for review.
            questions: Full question list for interviewee selection.

        Returns:
            dict: Interviewee packet with ai_findings, questions_menu,
                  and invitation_text.
        """
        system_prompt = (
            "You are creating a friendly, professional pre-interview packet for an interviewee. "
            "The tone should be warm and respectful — you are inviting them to review what AI "
            "found about their company and correct any mistakes. Keep it concise and professional. "
            "The questions_menu should be simplified versions without rationale or follow-ups. "
            "You MUST respond with ONLY valid JSON — no markdown, no explanation."
        )

        # Simplify questions for the interviewee (no rationale/follow-ups)
        simplified_questions = []
        for q in questions:
            simplified_questions.append({
                "id": q.get("id", ""),
                "question": q.get("question", ""),
                "topic": q.get("category", ""),
            })

        user_prompt = (
            "Create a pre-interview packet for the interviewee.\n\n"
            "=== COMPANY PROFILE (AI-generated) ===\n"
            + json.dumps(company_profile, indent=2, default=str)
            + "\n\n=== QUESTIONS MENU ===\n"
            + json.dumps(simplified_questions, indent=2, default=str)
            + '\n\nRespond with ONLY this JSON schema:\n'
            '{\n'
            '  "ai_findings": {\n'
            '    "company_summary": "2-3 sentence friendly summary of what we found",\n'
            '    "key_facts": ["fact 1", "fact 2", ...],\n'
            '    "topics_identified": ["topic we plan to discuss"]\n'
            '  },\n'
            '  "questions_menu": [{ "id": "q1", "question": "string", "topic": "string" }],\n'
            '  "invitation_text": "warm, professional 2-3 sentence message inviting corrections"\n'
            '}'
        )

        logger.info("Generating interviewee packet via Bedrock")
        response_text = self.invoke_claude(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.6,
        )

        try:
            packet = self._parse_json_response(response_text)
            logger.info("Interviewee packet generated")
            return packet
        except (ValueError, AttributeError) as e:
            logger.error("Failed to parse packet JSON: %s", e)
            return {
                "ai_findings": {
                    "company_summary": company_profile.get("description", ""),
                    "key_facts": company_profile.get("key_initiatives", []),
                    "topics_identified": [q.get("category", "") for q in questions[:5]],
                },
                "questions_menu": simplified_questions,
                "invitation_text": (
                    "We used AI to research your company before the interview. "
                    "Please take a moment to review what we found and let us know "
                    "if anything needs to be corrected. You can also select 2-3 "
                    "questions you would most like to discuss."
                ),
            }
