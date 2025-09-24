#!/bin/bash

# Quick development environment setup script
# Usage: ./setup-dev.sh

set -euo pipefail

echo "🚀 Setting up Kleinanzeigen MCP development environment..."

# Check if Python is available
if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python not found. Please install Python 3.8+ first."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
fi

echo "🐍 Using $PYTHON_CMD"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
else
    echo "📦 Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Unix-like (Linux, macOS)
    source .venv/bin/activate
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
fi

# Install package in development mode
echo "🔗 Installing package in development mode..."
pip install -e .

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🚀 Quick commands:"
echo "  source .venv/bin/activate  # Activate virtual environment"
echo "  ./scripts/lint.sh --fix     # Run linting and formatting"
echo "  python -m src.kleinanzeigen_mcp.server  # Run MCP server"
echo "  pytest                     # Run tests"
echo ""
echo "💡 Don't forget to activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "  .venv\\Scripts\\activate"
else
    echo "  source .venv/bin/activate"
fi