#!/bin/bash
# Production startup script for Mimir API

echo "🏭 Starting Mimir API in Production Mode"
echo "========================================"

# Load environment variables
if [ -f .env ]; then
    echo "✅ Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ No .env file found. Environment variables must be set."
    exit 1
fi

# Validate required environment variables
required_vars=(
    "AZURE_OPENAI_ENDPOINT"
    "AZURE_OPENAI_API_KEY"
    "AZURE_OPENAI_DEPLOYMENT_NAME"
    "CHROMADB_LOC"
    "EC_ADMIN_PWD"
    "JWT_SECRET_KEY"
)

echo "🔍 Checking required environment variables..."
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    fi
done
echo "✅ All required environment variables are set"

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p data/{chromadb,uploads,tmp,logs}
mkdir -p tmp/uploads

# Set proper permissions
echo "🔒 Setting directory permissions..."
chmod 755 data/
chmod 700 data/chromadb/
chmod 755 data/logs/

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install --no-dev -r requirements.txt
pip install gunicorn

# Start the production server
echo "🌟 Starting production server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "👥 Workers: 4"
echo "📊 Admin interface: http://localhost:8000"
echo ""

# Start with Gunicorn for production
exec gunicorn app.dependencies:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile data/logs/access.log \
    --error-logfile data/logs/error.log \
    --log-level info \
    --preload
