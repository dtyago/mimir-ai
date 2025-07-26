#!/bin/bash
# Azure App Service startup script with debugging

echo "=== Debug Info ==="
echo "User: $(whoami)"
echo "PWD: $(pwd)"
echo "PORT: $PORT"
echo "ENVIRONMENT: $ENVIRONMENT"
echo "Files in /app:"
ls -la /app/

echo "=== Ensuring Data Directories ==="
mkdir -p /home/data/chromadb /home/data/uploads /home/data/tmp /home/data/logs /home/data/face_images
chmod -R 777 /home/data 2>/dev/null || true
echo "Directory permissions set"

echo "=== Environment Variables ==="
echo "CHROMADB_LOC: $CHROMADB_LOC"
echo "UPLOAD_DIR: $UPLOAD_DIR"
echo "TEMP_UPLOAD_DIR: $TEMP_UPLOAD_DIR"
echo "USER_DATA_DIR: $USER_DATA_DIR"
echo "FACE_TEMP_DIR: $FACE_TEMP_DIR"

echo "=== Starting Gunicorn ==="
exec gunicorn -k uvicorn.workers.UvicornWorker -c /app/gunicorn_conf.py startup:app
