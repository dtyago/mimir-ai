#!/bin/bash
# Development startup script for Mimir API

echo "🚀 Starting Mimir API in Development Mode"
echo "=========================================="

# Load environment variables
if [ -f .env ]; then
    echo "✅ Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Make sure to set environment variables."
fi

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p data/{chromadb,uploads,tmp,logs}
mkdir -p tmp/uploads

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the development server
echo "🌟 Starting development server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "🔧 Auto-reload enabled for development"
echo "📊 Admin interface: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.dependencies:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    --access-log
