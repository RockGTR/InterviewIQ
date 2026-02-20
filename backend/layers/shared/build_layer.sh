#!/bin/bash
# =============================================================================
# build_layer.sh — Build the shared Lambda Layer for InterviewIQ
# =============================================================================
#
# This script packages all shared Python dependencies into a Lambda Layer
# compatible .zip file. The layer is used by all Lambda functions in the
# InterviewIQ backend.
#
# Usage:
#   chmod +x build_layer.sh
#   ./build_layer.sh
#
# Output:
#   layer.zip — Ready to deploy Lambda Layer archive
#
# Requirements:
#   - Python 3.13+ installed locally
#   - pip available
#
# Layer Structure (required by AWS Lambda):
#   python/
#   └── <packages>
#
# =============================================================================

set -euo pipefail

echo "🔧 Building InterviewIQ shared Lambda Layer..."

# Clean up any previous build artifacts
echo "  → Cleaning previous build..."
rm -rf python/ layer.zip

# Create the required python/ directory structure
echo "  → Creating python/ directory..."
mkdir -p python

# Install dependencies from requirements.txt
# --platform: ensures Linux-compatible binaries (Lambda runs on Amazon Linux)
# --only-binary: forces pre-compiled wheels (avoids compilation issues)
# -t python/: installs into the Lambda Layer directory structure
echo "  → Installing dependencies..."
pip install -r requirements.txt \
    -t python/ \
    --platform manylinux2014_x86_64 \
    --only-binary=:all: \
    --quiet \
    2>/dev/null || {
        echo "  ⚠ Platform-specific install failed, falling back to default..."
        pip install -r requirements.txt -t python/ --quiet
    }

# Create the layer zip archive
echo "  → Creating layer.zip..."
zip -r layer.zip python/ -q

# Report results
LAYER_SIZE=$(du -sh layer.zip | cut -f1)
echo ""
echo "✅ Lambda Layer built successfully!"
echo "   Size: ${LAYER_SIZE}"
echo "   File: layer.zip"
echo "   Packages: $(pip list --path python/ --format=columns 2>/dev/null | tail -n +3 | wc -l | tr -d ' ') installed"
echo ""
echo "   Deploy with: sam build && sam deploy"

# Clean up the python/ directory (zip has everything we need)
# Uncomment the next line to auto-clean after build:
# rm -rf python/
