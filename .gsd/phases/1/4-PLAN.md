---
phase: 1
plan: 4
wave: 2
---

# Plan 1.4: Web Scraping Module

## Objective
Implement the web scraping Lambda function that fetches public company information from the web. This provides one of the two data ingestion paths (the other being document parsing in Plan 1.5).

## Context
- .gsd/phases/1/RESEARCH.md (section 3 — web scraping)
- backend/functions/scrape_company/handler.py (from Plan 1.3)
- backend/shared/scraper_service.py (from Plan 1.3)

## Tasks

<task type="auto">
  <name>Implement ScraperService with company data extraction</name>
  <files>
    backend/shared/scraper_service.py
    backend/functions/scrape_company/handler.py
  </files>
  <action>
    Implement the ScraperService class (update the stub from Plan 1.3):

    1. **`scrape_url(url: str) -> dict`**:
       - Send GET request with proper User-Agent header
       - Parse HTML with BeautifulSoup
       - Extract: page title, meta description, main text content
       - Handle HTTP errors gracefully (404, 403, timeout)
       - Return structured dict with extracted data

    2. **`scrape_company(company_name: str, company_url: str = None) -> dict`**:
       - If URL provided: scrape that URL directly
       - If only name: construct Google search-like queries for:
         - Company website (about page)
         - News articles
         - Industry information
       - Scrape multiple pages (max 5) and aggregate results
       - Extract: company name, description, industry, location, key people, recent news
       - Return comprehensive company data dict

    3. **`parse_company_page(soup: BeautifulSoup) -> dict`**:
       - Extract structured data from HTML:
         - Company name from title/h1
         - Description from meta/about sections
         - Contact info
         - Key statistics if available
       - Clean text (remove scripts, styles, navigation)

    Update `scrape_company/handler.py`:
       - Parse `company_name` and `company_url` from request body
       - Call ScraperService.scrape_company()
       - Store raw scraped data in S3
       - Store metadata in DynamoDB
       - Return scraped data in response

    IMPORTANT:
    - Add 2-second delay between requests (polite scraping)
    - Set timeout to 10 seconds per request
    - Include fallback for blocked/unavailable sites
    - All functions must have comprehensive docstrings
    - Log all scraping activities for debugging
  </action>
  <verify>
    python3 -c "
    import sys
    sys.path.insert(0, 'backend/shared')
    from scraper_service import ScraperService
    svc = ScraperService()
    # Test with a known public URL
    result = svc.scrape_url('https://httpbin.org/html')
    assert 'content' in result, 'Missing content field'
    print('ScraperService works:', list(result.keys()))
    "
  </verify>
  <done>
    - ScraperService has 3 implemented methods with docstrings
    - Can successfully scrape a public URL
    - Handler processes request and returns structured response
    - Error handling covers common failure modes
    - All functions documented with type hints
  </done>
</task>

<task type="auto">
  <name>Create mock company data for demo reliability</name>
  <files>
    backend/data/mock_companies.json
    backend/data/README.md
  </files>
  <action>
    Create mock/cached company data for the 5 case study companies:

    1. `backend/data/mock_companies.json`:
       ```json
       {
         "gridflex_energy": {
           "name": "GridFlex Energy",
           "industry": "Virtual Power Plants (VPP)",
           "region": "Texas (ERCOT market)",
           ...
         },
         "lonestar_precision": { ... },
         "texas_mechanical": { ... },
         "launchstack_tech": { ... },
         "prairielogic_ag": { ... }
       }
       ```

       Extract key facts from the 5 case files in `data/` directory.

    2. `backend/data/README.md`:
       - Explains the mock data purpose
       - Documents data structure
       - Lists source files

    This ensures the demo works even if live scraping fails.

    IMPORTANT:
    - Structure should match ScraperService output format exactly
    - Include realistic detail from the actual case files
    - ScraperService should check mock data as fallback
  </action>
  <verify>
    python3 -c "
    import json
    with open('backend/data/mock_companies.json') as f:
        data = json.load(f)
    assert len(data) == 5, f'Expected 5 companies, got {len(data)}'
    for name, info in data.items():
        assert 'name' in info and 'industry' in info
    print('Mock data valid:', list(data.keys()))
    "
  </verify>
  <done>
    - mock_companies.json contains data for all 5 case companies
    - Data structure matches ScraperService output format
    - README.md documents the mock data
    - ScraperService can fall back to mock data
  </done>
</task>

## Success Criteria
- [ ] ScraperService can scrape public company URLs
- [ ] Mock data provides reliable demo fallback
- [ ] Handler integrates with S3 and DynamoDB for storage
- [ ] All code has comprehensive documentation
