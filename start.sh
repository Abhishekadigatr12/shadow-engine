#!/bin/bash

# Shadow Engine Startup Script

set -e

echo "🚀 Shadow Engine Startup"
echo "========================"

# Check Python version
echo "✓ Checking Python version..."
python --version

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt --quiet

# Check Ollama connection
echo "✓ Checking Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "  ✓ Ollama is running"
else
    echo "  ⚠️  Ollama not accessible at http://localhost:11434"
    echo "  Start Ollama: ollama serve"
    echo "  Pull model: ollama pull deepseek:13b"
fi

# Start application
echo ""
echo "✓ Starting Shadow Engine..."
echo "  API: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
