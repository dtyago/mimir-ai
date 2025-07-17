#!/bin/bash
# Azure App Service startup script for Mimir API

echo "🔷 Starting Mimir API on Azure App Service"
echo "========================================="

# Set Azure App Service specific environment variables
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"
export PORT=${PORT:-8000}

# Create necessary directories (Azure App Service compatible)
echo "📁 Creating required directories..."
mkdir -p /tmp/{chromadb,uploads,tmp,logs}

# Set ChromaDB location for Azure App Service
export CHROMADB_LOC="/tmp/chromadb"

# Log environment info
echo "🔍 Environment Information:"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Port: $PORT"
echo "Azure OpenAI Endpoint: ${AZURE_OPENAI_ENDPOINT}"
echo "ChromaDB Location: ${CHROMADB_LOC}"

# Install production dependencies if needed
echo "📦 Checking dependencies..."
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip install --no-cache-dir -r requirements.txt
fi

# Start the application with Gunicorn
echo "🌟 Starting Mimir API with Gunicorn..."
echo "📍 Application will be available on port $PORT"

exec gunicorn app.dependencies:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile /tmp/logs/access.log \
    --error-logfile /tmp/logs/error.log \
    --log-level info
