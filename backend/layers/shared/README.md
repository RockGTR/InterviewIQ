# Shared Lambda Layer

## Purpose

This Lambda Layer contains all shared Python dependencies used across InterviewIQ Lambda functions. Packaging dependencies in a layer keeps individual function deployment packages small and ensures consistent versions.

## Contents

| Package | Version | Purpose |
|---------|---------|---------|
| `boto3` | ≥1.35.0 | AWS SDK (Bedrock, Textract, Comprehend, S3, DynamoDB) |
| `requests` | ≥2.31.0 | HTTP requests for web scraping |
| `beautifulsoup4` | ≥4.12.0 | HTML parsing for web scraping |
| `python-docx` | ≥1.1.0 | .docx file text extraction |

## Building

```bash
chmod +x build_layer.sh
./build_layer.sh
```

This creates `layer.zip` (~30MB) containing all dependencies in the `python/` directory structure required by Lambda.

## Updating Dependencies

1. Edit `requirements.txt`
2. Run `./build_layer.sh`
3. Deploy: `cd ../.. && sam build && sam deploy`

## Constraints

- **Max unzipped size**: 250 MB (Lambda Layer limit)
- **Python version**: Must match Lambda runtime (3.13)
- **Platform**: Packages must be Linux-compatible (`manylinux2014_x86_64`)
