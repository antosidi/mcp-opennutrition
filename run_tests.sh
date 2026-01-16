#!/bin/bash
# Run tests for MCP OpenNutrition

set -e

echo "Setting up Python path..."
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

echo "Running pytest tests..."
pytest tests/ -v

echo ""
echo "All tests passed!"
