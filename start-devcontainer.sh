#!/bin/bash
# Quick start script for DevContainer environment

echo "🐳 Starting Mimir API in DevContainer"
echo "===================================="

# Check if we're in a devcontainer
if [ -n "$CODESPACES" ] || [ -n "$DEVCONTAINER" ] || [ -f "/.devcontainer-indicator" ]; then
    echo "✅ Running in DevContainer environment"
else
    echo "ℹ️  Not in DevContainer, but continuing..."
fi

# Load environment variables
if [ -f .env ]; then
    echo "✅ Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Using default development settings."
fi

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p data/{chromadb,uploads,tmp,logs}
mkdir -p tmp/uploads

# Quick dependency check
echo "🔍 Checking if dependencies are installed..."
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "🌟 Starting development server..."
echo "📍 Server available at: http://localhost:8000"
echo "🔧 Auto-reload enabled"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Use environment variables for configuration
export APP_ENV=${APP_ENV:-development}
export APP_HOST=${APP_HOST:-0.0.0.0}
export APP_PORT=${APP_PORT:-8000}
export LOG_LEVEL=${LOG_LEVEL:-info}

uvicorn app.dependencies:app \
    --host $APP_HOST \
    --port $APP_PORT \
    --reload \
    --log-level $LOG_LEVEL
