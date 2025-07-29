#!/bin/bash
# Azure App Service startup script with debugging and path detection

echo "=== Azure App Service Startup Debug ==="
echo "User: $(whoami)"
echo "PWD: $(pwd)"
echo "PORT: $PORT"
echo "ENVIRONMENT: $ENVIRONMENT"

# Detect if we're in Azure App Service and find the correct path
if [ -d "/home/site/wwwroot/app" ]; then
    echo "🔍 Found app in Azure App Service location"
    cd /home/site/wwwroot
    export PYTHONPATH=/home/site/wwwroot
    echo "📁 Working from: /home/site/wwwroot"
elif [ -d "/app/app" ]; then
    echo "🔍 Found app in container location"
    cd /app
    export PYTHONPATH=/app
    echo "📁 Working from: /app"
else
    echo "⚠️  Warning: Could not find app directory, using current location"
fi

echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Files in current directory:"
ls -la

echo "=== Ensuring Data Directories ==="
# Create data directories in both locations for maximum compatibility
mkdir -p /home/data/chromadb /home/data/uploads /home/data/tmp /home/data/logs /home/data/face_images
mkdir -p data/chromadb data/uploads data/tmp data/logs data/face_images 2>/dev/null || true
chmod -R 777 /home/data data 2>/dev/null || true
echo "✅ Directory permissions set"

echo "=== Environment Variables ==="
echo "CHROMADB_LOC: $CHROMADB_LOC"
echo "UPLOAD_DIR: $UPLOAD_DIR"
echo "TEMP_UPLOAD_DIR: $TEMP_UPLOAD_DIR"
echo "USER_DATA_DIR: $USER_DATA_DIR"
echo "FACE_TEMP_DIR: $FACE_TEMP_DIR"

echo "=== Starting Gunicorn ==="
exec gunicorn -k uvicorn.workers.UvicornWorker -c /app/gunicorn_conf.py startup:app
