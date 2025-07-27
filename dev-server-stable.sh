#!/bin/bash
# Stable development server for testing (no auto-reload)
# Use this when running tests to avoid restart issues

set -e  # Exit on error

echo "🔒 Starting Mimir API in Stable Development Mode"
echo "   (Auto-reload disabled for testing stability)"
echo "========================================="

# Set environment
export ENVIRONMENT=devcontainer
export APP_ENV=development
export PYTHONPATH=$(pwd)
export PORT=${PORT:-8000}

# Set default data paths
DATA_DIR="$(pwd)/data"
export CHROMADB_LOC="$DATA_DIR/chromadb"
export USER_DATA_DIR="$DATA_DIR"
export TEMP_UPLOAD_DIR="$DATA_DIR/tmp"
export UPLOAD_DIR="$DATA_DIR/uploads"
export FACE_TEMP_DIR="$DATA_DIR/tmp"
export LOG_FILE="$DATA_DIR/logs/app.log"
export CHROMADB_ALLOW_RESET=true

# Load .env if it exists
if [ -f .env ]; then
    echo "✅ Loading environment variables from .env"
    set -a  # Automatically export all variables
    source .env
    set +a  # Turn off automatic export
fi

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p "$DATA_DIR"/{chromadb,uploads,tmp,logs}

# Test SQLite compatibility
echo "🔍 Testing SQLite compatibility..."
python3 -c "
import sys
sys.path.insert(0, '$(pwd)')
try:
    from app.utils.sqlite_compat import setup_sqlite_compatibility
    setup_sqlite_compatibility()
    print('✅ SQLite compatibility check completed')
except Exception as e:
    print('⚠️  SQLite compatibility warning:', str(e))
"

echo ""
echo "🌟 Starting Mimir API (Stable Mode)..."
echo "📍 Server will be available at: http://localhost:$PORT"
echo "📊 Admin interface: http://localhost:$PORT/admin"
echo "🔒 Auto-reload: DISABLED (for testing stability)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start without auto-reload for stability
exec uvicorn app.dependencies:app \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level info \
    --access-log
