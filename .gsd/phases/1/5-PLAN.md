---
phase: 1
plan: 5
wave: 2
---

# Plan 1.5: Document Ingestion Pipeline (Textract)

## Objective
Implement the document ingestion pipeline that converts .docx files to PDF, processes them through Amazon Textract, and stores the extracted text. This provides the second data ingestion path alongside web scraping.

## Context
- .gsd/phases/1/RESEARCH.md (section 2 — Textract limitations)
- data/ (5 sample .docx case files)
- backend/functions/parse_document/handler.py (from Plan 1.3)
- backend/shared/textract_service.py (from Plan 1.3)

## Tasks

<task type="auto">
  <name>Implement TextractService with .docx conversion pipeline</name>
  <files>
    backend/shared/textract_service.py
    backend/functions/parse_document/handler.py
  </files>
  <action>
    Implement the TextractService class:

    1. **`convert_docx_to_text(docx_path: str) -> str`**:
       - Use `python-docx` to extract text from .docx file
       - Preserve paragraph structure
       - Return clean text content
       - This serves as the primary extraction method AND as fallback

    2. **`process_document_textract(bucket: str, key: str) -> dict`**:
       - Call Textract `detect_document_text()` for uploaded PDF/image files
       - Parse Textract response blocks
       - Extract text with confidence scores
       - Return structured dict with text, blocks, and metadata
       - Handle Textract errors gracefully

    3. **`upload_and_process(file_bytes: bytes, filename: str, bucket: str) -> dict`**:
       - Upload raw file to S3
       - If .docx: extract text directly via python-docx (fast path)
       - If PDF/image: process via Textract (demo Textract capability)
       - Return extracted text and metadata

    Update `parse_document/handler.py`:
       - Accept file upload (base64 encoded in body, or S3 key reference)
       - Call TextractService.upload_and_process()
       - Store extracted text in DynamoDB session record
       - Return extraction results

    IMPORTANT:
    - Textract does NOT support .docx directly — use python-docx for .docx files
    - For demo: show both paths (python-docx for .docx, Textract for PDF)
    - All functions must have comprehensive docstrings and type hints
    - Handle the 5 case files from `data/` directory as test cases
    - Chunk large documents for Comprehend's 5KB limit (for Phase 2)
  </action>
  <verify>
    python3 -c "
    import sys
    sys.path.insert(0, 'backend/shared')
    from textract_service import TextractService
    svc = TextractService()
    # Test with a sample .docx file
    text = svc.convert_docx_to_text('data/Hackathon Case 001.docx')
    assert len(text) > 100, f'Expected substantial text, got {len(text)} chars'
    assert 'GridFlex' in text, 'Should contain GridFlex company name'
    print(f'Extracted {len(text)} characters from Case 001')
    "
  </verify>
  <done>
    - TextractService can extract text from .docx files via python-docx
    - TextractService can call Textract API for PDF/image files
    - Handler accepts file upload and returns extracted text
    - All 5 sample .docx files process successfully
    - All functions documented with comprehensive docstrings
  </done>
</task>

<task type="auto">
  <name>Upload sample data files to S3</name>
  <files>
    backend/scripts/upload_sample_data.py
    backend/scripts/README.md
  </files>
  <action>
    Create a script to upload the 5 sample .docx files to the S3 bucket:

    1. `backend/scripts/upload_sample_data.py`:
       - Read all .docx files from `data/` directory
       - Upload each to S3 under `sample-data/` prefix
       - Extract text from each using TextractService
       - Store extracted text in DynamoDB as seed data
       - Print summary of uploaded files

    2. `backend/scripts/README.md`:
       - Documents all utility scripts
       - Usage instructions
       - Prerequisites

    IMPORTANT:
    - Script should be idempotent (safe to re-run)
    - Include progress output for each file
    - Handle upload errors gracefully
    - Comprehensive docstrings throughout
  </action>
  <verify>
    python3 backend/scripts/upload_sample_data.py --dry-run
  </verify>
  <done>
    - Script uploads all 5 .docx files to S3
    - Extracted text stored in DynamoDB
    - Script is idempotent and well-documented
    - README.md documents usage
  </done>
</task>

## Success Criteria
- [ ] TextractService extracts text from .docx files
- [ ] TextractService calls Textract API for PDF files
- [ ] All 5 sample case files process correctly
- [ ] Sample data uploaded to S3 and indexed in DynamoDB
- [ ] All code has comprehensive documentation
