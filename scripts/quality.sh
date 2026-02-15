#!/usr/bin/env bash
set -eu

cd "$(dirname "$0")/.."

FIX=false
if [[ "${1:-}" == "--fix" ]]; then
    FIX=true
fi

echo "=== Code Quality Check ==="
echo ""

if $FIX; then
    echo "Running black (formatting)..."
    uv run black main.py backend/
    echo ""
    echo "All files formatted."
else
    echo "Running black --check..."
    if uv run black --check main.py backend/; then
        echo ""
        echo "PASSED: All files are properly formatted."
    else
        echo ""
        echo "FAILED: Some files need formatting. Run 'bash scripts/quality.sh --fix' to auto-format."
        exit 1
    fi
fi
