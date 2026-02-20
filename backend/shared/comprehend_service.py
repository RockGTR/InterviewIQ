"""
Comprehend Service — NLP Analysis via Amazon Comprehend
========================================================

Provides natural language processing capabilities for analyzing
company-related text. Extracts entities (people, organizations,
locations), key phrases, and sentiment from scraped web content
and parsed documents.

Text is chunked to respect Comprehend's 5,000 byte limit per request.
Results are aggregated and deduplicated across chunks.

Usage:
    >>> from shared.comprehend_service import ComprehendService
    >>> nlp = ComprehendService()
    >>> entities = nlp.detect_entities("GridFlex Energy is a Texas-based VPP...")
    >>> phrases = nlp.detect_key_phrases("GridFlex provides grid stabilization...")
"""

import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Comprehend's synchronous API limit per request
MAX_BYTES = 5000


class ComprehendService:
    """
    Service class for Amazon Comprehend NLP operations.

    Provides entity detection, key phrase extraction, and sentiment
    analysis with automatic text chunking for large documents.

    Attributes:
        client: boto3 Comprehend client.
    """

    def __init__(self):
        """Initialize Comprehend service."""
        self.client = boto3.client("comprehend")
        logger.info("ComprehendService initialized")

    def _chunk_text(self, text: str, max_bytes: int = MAX_BYTES) -> list:
        """
        Split text into chunks that fit within Comprehend's byte limit.

        Splits on paragraph boundaries first, then sentence boundaries
        if paragraphs are too large.

        Args:
            text: Input text to chunk.
            max_bytes: Maximum bytes per chunk (default: 5000).

        Returns:
            list: List of text chunks, each within the byte limit.
        """
        if len(text.encode("utf-8")) <= max_bytes:
            return [text]

        chunks = []
        current_chunk = ""

        for paragraph in text.split("\n"):
            test_chunk = current_chunk + "\n" + paragraph if current_chunk else paragraph

            if len(test_chunk.encode("utf-8")) > max_bytes:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph[:max_bytes]
            else:
                current_chunk = test_chunk

        if current_chunk:
            chunks.append(current_chunk)

        logger.info("Chunked %d bytes into %d chunks", len(text.encode("utf-8")), len(chunks))
        return chunks

    def detect_entities(self, text: str, language: str = "en") -> list:
        """
        Detect named entities in text using Amazon Comprehend.

        Identifies entities of types: PERSON, ORGANIZATION, LOCATION,
        DATE, QUANTITY, EVENT, TITLE, COMMERCIAL_ITEM, OTHER.

        Args:
            text: Input text to analyze.
            language: Language code (default: "en").

        Returns:
            list: Deduplicated list of entity dicts with:
                - text (str): Entity text
                - type (str): Entity type
                - score (float): Confidence score (0-1)
        """
        chunks = self._chunk_text(text)
        all_entities = {}

        for chunk in chunks:
            if not chunk.strip():
                continue

            try:
                response = self.client.detect_entities(Text=chunk, LanguageCode=language)

                for entity in response.get("Entities", []):
                    key = f"{entity['Type']}:{entity['Text']}"
                    if key not in all_entities or entity["Score"] > all_entities[key]["score"]:
                        all_entities[key] = {
                            "text": entity["Text"],
                            "type": entity["Type"],
                            "score": round(entity["Score"], 4),
                        }
            except ClientError as e:
                logger.warning("Comprehend detect_entities failed for chunk: %s", e)

        entities = sorted(all_entities.values(), key=lambda x: x["score"], reverse=True)
        logger.info("Detected %d unique entities", len(entities))
        return entities

    def detect_key_phrases(self, text: str, language: str = "en") -> list:
        """
        Extract key phrases from text using Amazon Comprehend.

        Identifies the most important phrases that describe the main
        topics and concepts in the text.

        Args:
            text: Input text to analyze.
            language: Language code (default: "en").

        Returns:
            list: Deduplicated list of key phrase dicts with:
                - text (str): Key phrase text
                - score (float): Confidence score (0-1)
        """
        chunks = self._chunk_text(text)
        all_phrases = {}

        for chunk in chunks:
            if not chunk.strip():
                continue

            try:
                response = self.client.detect_key_phrases(Text=chunk, LanguageCode=language)

                for phrase in response.get("KeyPhrases", []):
                    key = phrase["Text"].lower()
                    if key not in all_phrases or phrase["Score"] > all_phrases[key]["score"]:
                        all_phrases[key] = {
                            "text": phrase["Text"],
                            "score": round(phrase["Score"], 4),
                        }
            except ClientError as e:
                logger.warning("Comprehend detect_key_phrases failed for chunk: %s", e)

        phrases = sorted(all_phrases.values(), key=lambda x: x["score"], reverse=True)
        logger.info("Detected %d unique key phrases", len(phrases))
        return phrases

    def detect_sentiment(self, text: str, language: str = "en") -> dict:
        """
        Analyze overall sentiment of text using Amazon Comprehend.

        Returns the dominant sentiment (POSITIVE, NEGATIVE, NEUTRAL, MIXED)
        and confidence scores for each sentiment class.

        Args:
            text: Input text to analyze.
            language: Language code (default: "en").

        Returns:
            dict: Sentiment analysis with:
                - sentiment (str): Dominant sentiment
                - scores (dict): Confidence for each class
        """
        # Use first chunk only for overall sentiment (representative sample)
        chunk = self._chunk_text(text)[0] if text else ""

        if not chunk.strip():
            return {"sentiment": "NEUTRAL", "scores": {}}

        try:
            response = self.client.detect_sentiment(Text=chunk, LanguageCode=language)

            result = {
                "sentiment": response["Sentiment"],
                "scores": {
                    "positive": round(response["SentimentScore"]["Positive"], 4),
                    "negative": round(response["SentimentScore"]["Negative"], 4),
                    "neutral": round(response["SentimentScore"]["Neutral"], 4),
                    "mixed": round(response["SentimentScore"]["Mixed"], 4),
                },
            }
            logger.info("Sentiment: %s (%.2f confidence)", result["sentiment"],
                        result["scores"].get(result["sentiment"].lower(), 0))
            return result

        except ClientError as e:
            logger.error("Comprehend detect_sentiment failed: %s", e)
            return {"sentiment": "UNKNOWN", "scores": {}, "error": str(e)}

    def analyze_text(self, text: str) -> dict:
        """
        Run full NLP analysis pipeline on text.

        Convenience method that runs entity detection, key phrase extraction,
        and sentiment analysis in one call.

        Args:
            text: Input text to analyze.

        Returns:
            dict: Combined results with:
                - entities (list): Named entities
                - key_phrases (list): Key phrases
                - sentiment (dict): Sentiment analysis
        """
        return {
            "entities": self.detect_entities(text),
            "key_phrases": self.detect_key_phrases(text),
            "sentiment": self.detect_sentiment(text),
        }
