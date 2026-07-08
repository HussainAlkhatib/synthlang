#!/bin/bash
# Clean up temporary files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.bak" -delete
find . -name "*.tmp" -delete
rm -rf dist/ build/ *.egg-info 2>/dev/null || true
echo "Cleanup complete"