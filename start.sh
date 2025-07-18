#!/bin/bash
# Universal startup script for Mimir API
# Supports development, production, and Azure App Service environments

set -e  # Exit on error

# Detect environment
if [ -n "$CODESPACES" ]; then
    echo "❌ ERROR: GitHub Codespaces is not supported!"
    echo "   This project requires SQLite 3.35.0+ (Codespaces has 3.34.1)"
    echo "   Please use local DevContainer or Docker Compose instead."
    echo "   See README.md for setup instructions."
    exit 1
elif [ -n "$DEVCONTAINER" ] || [ -f "/.devcontainer-indicator" ]; then
    DETECTED_ENV="devcontainer"
elif [ -n "$WEBSITE_SITE_NAME" ] || [ -n "$APPSETTING_WEBSITE_SITE_NAME" ]; then
    DETECTED_ENV="azure"
elif [ "$APP_ENV" = "production" ]; then
    DETECTED_ENV="production"
else
    DETECTED_ENV="development"
fi

# Override with explicit environment setting
ENVIRONMENT=${ENVIRONMENT:-$DETECTED_ENV}

echo "🚀 Starting Mimir API"
echo "Environment: $ENVIRONMENT"
echo "========================================="

# Load environment variables if .env exists
if [ -f .env ] && [ "$ENVIRONMENT" != "azure" ]; then
    echo "✅ Loading environment variables from .env"
    set -a  # Automatically export all variables
    source .env
    set +a  # Stop auto-exporting
fi

# Environment-specific configuration
case $ENVIRONMENT in
    "azure")
        echo "🔷 Configuring for Azure App Service..."
        export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"
        export PORT=${PORT:-8000}
        export APP_ENV=production
        DATA_DIR="/tmp"
        WORK_DIR="/home/site/wwwroot"
        ;;
    "production")
        echo "🏭 Configuring for production..."
        export APP_ENV=production
        export PYTHONPATH=$(pwd)
        DATA_DIR="$(pwd)/data"
        WORK_DIR=$(pwd)
        
        # Validate required production environment variables
        required_vars=("AZURE_OPENAI_ENDPOINT" "AZURE_OPENAI_API_KEY" "AZURE_OPENAI_DEPLOYMENT_NAME" "EC_ADMIN_PWD" "JWT_SECRET_KEY")
        for var in "${required_vars[@]}"; do
            if [ -z "${!var}" ]; then
                echo "❌ Missing required environment variable: $var"
                exit 1
            fi
        done
        ;;
    "devcontainer")
        echo "🐳 Configuring for DevContainer..."
        export APP_ENV=development
        export PYTHONPATH=$(pwd)
        DATA_DIR="$(pwd)/data"
        WORK_DIR=$(pwd)
        export CHROMADB_ALLOW_RESET=true
        ;;
    *)
        echo "🛠️ Configuring for local development..."
        export APP_ENV=development
        export PYTHONPATH=$(pwd)
        DATA_DIR="$(pwd)/data"
        WORK_DIR=$(pwd)
        
        # Check for virtual environment in local development
        if [ "$ENVIRONMENT" = "development" ] && [ ! -n "$VIRTUAL_ENV" ] && [ ! -n "$CONDA_DEFAULT_ENV" ]; then
            if [ -d "venv" ]; then
                echo "🔧 Activating virtual environment..."
                source venv/bin/activate
            else
                echo "⚠️  No virtual environment detected. Consider creating one with: python -m venv venv"
            fi
        fi
        ;;
esac

# Set common environment variables
export CHROMADB_LOC="${CHROMADB_LOC:-$DATA_DIR/chromadb}"
export USER_DATA_DIR="${USER_DATA_DIR:-$DATA_DIR}"
export UPLOAD_DIR="${UPLOAD_DIR:-$DATA_DIR/uploads}"
export LOG_FILE="${LOG_FILE:-$DATA_DIR/logs/mimir-api.log}"
export PORT=${PORT:-8000}

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p "$DATA_DIR"/{chromadb,uploads,tmp,logs}

# Log environment information
echo "🔍 Environment Information:"
echo "   Environment: $ENVIRONMENT"
echo "   Python version: $(python --version 2>/dev/null || python3 --version)"
echo "   Working directory: $WORK_DIR"
echo "   Python path: $PYTHONPATH"
echo "   Port: $PORT"
echo "   ChromaDB location: $CHROMADB_LOC"
echo "   Azure OpenAI Endpoint: ${AZURE_OPENAI_ENDPOINT:-'Not set'}"

# Test dependencies and SQLite compatibility
echo "🔍 Testing SQLite compatibility..."
cd "$WORK_DIR"
python_cmd=$(which python3 2>/dev/null || which python)

$python_cmd -c "
import sys
sys.path.insert(0, '$WORK_DIR')
try:
    from app.utils.sqlite_compat import setup_sqlite_compatibility
    setup_sqlite_compatibility()
    print('✅ SQLite compatibility check completed')
except Exception as e:
    print('⚠️  SQLite compatibility warning:', str(e))
"

# Verify critical dependencies are installed
echo "📦 Verifying dependencies..."
$python_cmd -c "
import sys
sys.path.insert(0, '$WORK_DIR')
try:
    import fastapi, uvicorn, gunicorn
    print('✅ Core web dependencies verified')
except ImportError as e:
    print('❌ Missing core dependencies:', str(e))
    print('   Run: pip install -r requirements.txt')
    exit(1)
"

# Start the application based on environment
echo ""
echo "🌟 Starting Mimir API..."
echo "📍 Server will be available on port $PORT"
echo ""

case $ENVIRONMENT in
    "production"|"azure")
        echo "🏭 Starting with Gunicorn (production mode)..."
        exec gunicorn app.dependencies:app \
            --worker-class uvicorn.workers.UvicornWorker \
            --workers 4 \
            --bind 0.0.0.0:$PORT \
            --timeout 120 \
            --keepalive 5 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --preload \
            --access-logfile "$DATA_DIR/logs/access.log" \
            --error-logfile "$DATA_DIR/logs/error.log" \
            --log-level info
        ;;
    *)
        echo "🛠️ Starting with Uvicorn (development mode)..."
        echo "📊 Admin interface: http://localhost:$PORT/admin"
        echo "🔧 Auto-reload enabled"
        echo ""
        echo "Press Ctrl+C to stop the server"
        echo ""
        exec uvicorn app.dependencies:app \
            --host 0.0.0.0 \
            --port $PORT \
            --reload \
            --log-level info \
            --access-log
        ;;
esac
