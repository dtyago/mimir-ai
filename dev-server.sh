#!/bin/bash
# Local development server with hot reload
# Use this for rapid development, then deploy when ready

echo "🔥 Starting local development server with hot reload..."

# Check if we're in the right directory
if [ ! -f "startup.py" ]; then
    echo "❌ Please run this from the mimir-ai root directory"
    exit 1
fi

# Create data directories if they don't exist
mkdir -p data/chromadb data/uploads data/tmp data/logs

# Set environment variables for development
export ENVIRONMENT=development
export PYTHONPATH=/workspaces/mimir-ai
export CHROMADB_ALLOW_RESET=true

# Install development dependencies if needed
if ! python -c "import watchdog" 2>/dev/null; then
    echo "📦 Installing development dependencies..."
    pip install watchdog[watchmedo]
fi

echo "🚀 Server starting at http://localhost:8000"
echo "🔄 Hot reload enabled - changes will auto-restart the server"
echo "📋 Available endpoints:"
echo "   • http://localhost:8000/health - Health check"
echo "   • http://localhost:8000/docs - API documentation"
echo "   • http://localhost:8000/admin - Admin interface"
echo ""
echo "💡 Press Ctrl+C to stop"
echo ""

# Start with auto-reload using watchdog
watchmedo auto-restart \
    --directory=./app \
    --pattern="*.py" \
    --recursive \
    -- uvicorn startup:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
