"""
Bedrock Service — AI Generation via Amazon Bedrock/Claude
==========================================================

Provides methods for invoking Amazon Bedrock's Claude model to generate
interview intelligence: company profiles, interview questions, conversation
flows, and complete interviewer/interviewee briefs.

The service uses few-shot prompting with exemplar case files to produce
output that matches the expected format. Questions follow interview best
practices including the "what did AI get wrong?" warm opening technique.

Usage:
    >>> from shared.bedrock_service import BedrockService
    >>> bedrock = BedrockService()
    >>> profile = bedrock.generate_company_profile(scraped_data, parsed_docs)
    >>> questions = bedrock.generate_questions(profile, analysis_results)
"""

import os
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
            "MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
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

    def generate_company_profile(
        self,
        scraped_data: dict,
        parsed_documents: list,
        analysis_results: Optional[dict] = None,
    ) -> dict:
        """
        Generate a comprehensive company profile from collected data.

        Synthesizes web-scraped data, parsed documents, and NLP analysis
        into a structured company profile including industry context,
        business model hypotheses, and competitive landscape.

        Args:
            scraped_data: Raw data from web scraping (company pages, news).
            parsed_documents: List of extracted text from uploaded documents.
            analysis_results: Optional NLP analysis (entities, key phrases).

        Returns:
            dict: Structured company profile with fields:
                - name, industry, region, stage
                - description, business_model
                - key_people, competitors
                - hypotheses (list of informed guesses)
                - confidence_level

        Note:
            Implementation will be completed in Phase 2. This stub returns
            the expected structure for frontend development.
        """
        # TODO: Phase 2 — Implement with full prompt engineering
        logger.info("generate_company_profile called (stub)")
        return {
            "name": scraped_data.get("company_name", "Unknown"),
            "industry": "To be determined",
            "region": "Texas",
            "stage": "Unknown",
            "description": "Profile generation pending Phase 2 implementation.",
            "business_model": {},
            "key_people": [],
            "competitors": [],
            "hypotheses": [],
            "confidence_level": "Low — stub implementation",
        }

    def generate_questions(
        self,
        company_profile: dict,
        analysis_results: Optional[dict] = None,
        num_questions: int = 10,
    ) -> list:
        """
        Generate interview questions following best practices.

        Produces well-crafted questions that demonstrate research depth,
        following the two-stage interview methodology:
        1. Surface-level confirmation questions
        2. Deeper probing questions for hidden insights
        3. Questions targeting business ecosystems and expertise

        Args:
            company_profile: Structured company profile from generate_company_profile.
            analysis_results: Optional NLP analysis for context.
            num_questions: Number of questions to generate (default: 10).

        Returns:
            list: List of question dicts, each with:
                - id (str): Unique question identifier
                - question (str): The interview question text
                - category (str): Question category (e.g., "business_model", "market")
                - depth (str): "surface" or "deep"
                - rationale (str): Why this question matters
                - follow_ups (list): Suggested follow-up questions

        Note:
            Implementation will be completed in Phase 2.
        """
        # TODO: Phase 2 — Implement with few-shot prompting from case files
        logger.info("generate_questions called (stub)")
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
        an interviewer can read in 5 minutes to prepare for the conversation.

        Args:
            company_profile: Structured company profile.
            questions: Generated interview questions.
            analysis_results: Optional NLP analysis.

        Returns:
            dict: Complete interviewer brief with sections:
                - executive_summary
                - company_overview
                - industry_context
                - pre_call_hypotheses
                - questions (organized by depth/category)
                - conversation_flow (suggested structure)
                - key_facts (quick reference)

        Note:
            Implementation will be completed in Phase 2.
        """
        # TODO: Phase 2 — Full implementation
        logger.info("generate_interviewer_brief called (stub)")
        return {
            "executive_summary": "Brief generation pending Phase 2.",
            "company_overview": company_profile,
            "industry_context": "",
            "pre_call_hypotheses": [],
            "questions": questions,
            "conversation_flow": [],
            "key_facts": [],
        }

    def generate_interviewee_packet(
        self,
        company_profile: dict,
        questions: list,
    ) -> dict:
        """
        Generate the pre-interview packet for the interviewee.

        Creates a document showing what AI "discovered" about the company,
        inviting the interviewee to correct inaccuracies and select
        preferred discussion questions.

        Args:
            company_profile: AI-generated company profile for review.
            questions: Full question list for interviewee selection.

        Returns:
            dict: Interviewee packet with sections:
                - ai_findings (what AI thinks it knows)
                - questions_menu (all questions for selection)
                - invitation_text (asking for corrections)

        Note:
            Implementation will be completed in Phase 2.
        """
        # TODO: Phase 2 — Full implementation
        logger.info("generate_interviewee_packet called (stub)")
        return {
            "ai_findings": company_profile,
            "questions_menu": questions,
            "invitation_text": "Please review the above and let us know what we got wrong.",
        }
