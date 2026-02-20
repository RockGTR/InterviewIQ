"""
Scraper Service — Web Scraping for Company Intelligence
=========================================================

Provides methods for scraping public company information from the web.
Uses requests + BeautifulSoup4 for HTML parsing without a headless browser.

Includes a fallback to mock data for demo reliability. When live scraping
fails or a known demo company is requested, pre-built company profiles
from the hackathon case files are returned.

Usage:
    >>> from shared.scraper_service import ScraperService
    >>> scraper = ScraperService()
    >>> data = scraper.scrape_company("GridFlex Energy", "https://gridflex.com")
"""

import os
import json
import time
import logging
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Polite scraping: delay between requests
REQUEST_DELAY_SECONDS = 2
REQUEST_TIMEOUT_SECONDS = 10
MAX_PAGES = 5

# User-Agent header to identify as a research bot
USER_AGENT = (
    "Mozilla/5.0 (compatible; InterviewIQ-Research/1.0; "
    "Texas A&M University Research Project)"
)


class ScraperService:
    """
    Service class for web scraping operations.

    Fetches and parses public company information from web pages.
    Falls back to mock data for known demo companies or when
    live scraping fails.

    Attributes:
        mock_data (dict): Pre-built company profiles for demo.
    """

    def __init__(self):
        """Initialize ScraperService and load mock company data."""
        self.mock_data = self._load_mock_data()
        logger.info("ScraperService initialized with %d mock companies", len(self.mock_data))

    def _load_mock_data(self) -> dict:
        """
        Load mock company data from the data directory.

        Returns:
            dict: Mock company data keyed by normalized company name.
        """
        mock_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "mock_companies.json",
        )
        if os.path.exists(mock_path):
            with open(mock_path) as f:
                return json.load(f)
        return {}

    def scrape_url(self, url: str) -> dict:
        """
        Scrape a single URL and extract structured content.

        Sends a GET request with proper headers and parses the response
        HTML to extract title, description, and main text content.

        Args:
            url: The URL to scrape.

        Returns:
            dict: Scraped content with:
                - url (str): The scraped URL
                - title (str): Page title
                - description (str): Meta description
                - content (str): Main text content (cleaned)
                - success (bool): Whether scraping succeeded
                - error (str): Error message if failed

        Raises:
            No exceptions — errors are captured in the return dict.
        """
        try:
            response = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=REQUEST_TIMEOUT_SECONDS,
                allow_redirects=True,
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            result = self.parse_company_page(soup)
            result["url"] = url
            result["success"] = True
            result["status_code"] = response.status_code

            logger.info("Scraped %s: %d chars extracted", url, len(result.get("content", "")))
            return result

        except requests.exceptions.Timeout:
            logger.warning("Timeout scraping %s", url)
            return {"url": url, "success": False, "error": "Request timed out"}
        except requests.exceptions.HTTPError as e:
            logger.warning("HTTP error scraping %s: %s", url, e)
            return {"url": url, "success": False, "error": f"HTTP {e.response.status_code}"}
        except requests.exceptions.RequestException as e:
            logger.warning("Request error scraping %s: %s", url, e)
            return {"url": url, "success": False, "error": str(e)}

    def parse_company_page(self, soup: BeautifulSoup) -> dict:
        """
        Extract structured data from a parsed HTML page.

        Cleans the HTML (removes scripts, styles, nav) and extracts
        the page title, meta description, and main text content.

        Args:
            soup: BeautifulSoup parsed HTML document.

        Returns:
            dict: Extracted data with:
                - title (str): Page title
                - description (str): Meta description
                - content (str): Cleaned main text content
                - headings (list): H1-H3 headings found
        """
        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Extract title
        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Extract meta description
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")

        # Extract headings
        headings = []
        for level in ["h1", "h2", "h3"]:
            for heading in soup.find_all(level):
                text = heading.get_text(strip=True)
                if text:
                    headings.append({"level": level, "text": text})

        # Extract main text content
        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        content = ""
        if main_content:
            content = main_content.get_text(separator="\n", strip=True)
            # Clean up excessive whitespace
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            content = "\n".join(lines)

        return {
            "title": title,
            "description": description,
            "content": content[:10000],  # Cap at 10K chars
            "headings": headings[:20],   # Cap at 20 headings
        }

    def scrape_company(
        self,
        company_name: str,
        company_url: Optional[str] = None,
    ) -> dict:
        """
        Scrape comprehensive company information from multiple sources.

        If a URL is provided, scrapes that URL directly. Otherwise,
        attempts to find and scrape relevant pages for the company.
        Falls back to mock data for known demo companies.

        Args:
            company_name: Name of the company to research.
            company_url: Optional URL of the company website.

        Returns:
            dict: Comprehensive company data with:
                - company_name (str): Company name
                - company_url (str): URL used
                - pages (list): Data from each scraped page
                - summary (dict): Aggregated company info
                - source (str): "live_scrape" or "mock_data"
        """
        # Check mock data first (for demo reliability)
        normalized_name = company_name.lower().replace(" ", "_")
        for key, mock in self.mock_data.items():
            if key.lower() in normalized_name or normalized_name in key.lower():
                logger.info("Using mock data for: %s", company_name)
                return {
                    "company_name": company_name,
                    "company_url": company_url or "",
                    "pages": [],
                    "summary": mock,
                    "source": "mock_data",
                }

        # Live scraping
        pages = []

        if company_url:
            # Scrape the provided URL
            page_data = self.scrape_url(company_url)
            pages.append(page_data)

            # Try common about page patterns
            parsed = urlparse(company_url)
            about_urls = [
                f"{parsed.scheme}://{parsed.netloc}/about",
                f"{parsed.scheme}://{parsed.netloc}/about-us",
                f"{parsed.scheme}://{parsed.netloc}/company",
            ]

            for about_url in about_urls[:2]:  # Limit to 2 extras
                time.sleep(REQUEST_DELAY_SECONDS)
                about_data = self.scrape_url(about_url)
                if about_data.get("success"):
                    pages.append(about_data)

        # Aggregate results
        summary = self._aggregate_scraped_data(company_name, pages)

        result = {
            "company_name": company_name,
            "company_url": company_url or "",
            "pages": pages,
            "summary": summary,
            "source": "live_scrape",
        }

        logger.info("Scraped %d pages for %s", len(pages), company_name)
        return result

    def _aggregate_scraped_data(self, company_name: str, pages: list) -> dict:
        """
        Aggregate scraped data from multiple pages into a summary.

        Args:
            company_name: Company name.
            pages: List of scraped page data dicts.

        Returns:
            dict: Aggregated company summary.
        """
        all_content = []
        all_headings = []

        for page in pages:
            if page.get("success"):
                all_content.append(page.get("content", ""))
                all_headings.extend(page.get("headings", []))

        return {
            "name": company_name,
            "description": pages[0].get("description", "") if pages else "",
            "combined_content": "\n\n---\n\n".join(all_content),
            "headings": all_headings,
            "pages_scraped": len([p for p in pages if p.get("success")]),
            "total_content_length": sum(len(c) for c in all_content),
        }
