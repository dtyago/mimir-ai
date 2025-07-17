# Mimir API Deployment Guide

## 🚀 Starting the Application

### Development Environment

#### Option 1: DevContainer (Recommended for VS Code)
```bash
# Quick start for devcontainer
./start-devcontainer.sh
```

#### Option 2: Local Development
```bash
# Full development setup
./start-dev.sh
```

#### Option 3: Manual Development Start
```bash
# Load environment variables
source .env

# Start with auto-reload
uvicorn app.dependencies:app --host 0.0.0.0 --port 8000 --reload --log-level info
```

### Production Environment

#### Option 1: Production Script (Recommended)
```bash
# Start production server
./start-prod.sh
```

#### Option 2: Docker Compose (Container Deployment)
```bash
# Build and start with Docker
docker-compose up --build -d

# View logs
docker-compose logs -f mimir-api

# Stop
docker-compose down
```

#### Option 3: Manual Production Start
```bash
# Load environment variables
source .env

# Start with Gunicorn
gunicorn app.dependencies:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile data/logs/access.log \
    --error-logfile data/logs/error.log \
    --log-level info \
    --preload
```

## 📊 Application Endpoints

### Main Application
- **Admin Interface**: `http://localhost:8000/`
- **Health Check**: `http://localhost:8000/health`

### API Endpoints
- **User Login**: `POST /user/login`
- **User Logout**: `POST /user/logout`
- **Chat**: `POST /user/chat`
- **File Upload**: `POST /user/upload`
- **Admin Login**: `POST /admin/login`
- **User Registration**: `POST /admin/register_user`
- **Data Management**: `GET /admin/data_management`

## 🔧 Configuration

### Environment Variables
All configuration is managed through the `.env` file:
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Your API key
- `AZURE_OPENAI_API_VERSION`: API version (2024-12-01-preview)
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your deployment name
- `CHROMADB_LOC`: Database location
- `EC_ADMIN_PWD`: Hashed admin password
- `JWT_SECRET_KEY`: JWT signing key

### Directory Structure
```
/workspaces/mimir-api/
├── data/
│   ├── chromadb/     # Vector database storage
│   ├── uploads/      # Processed files
│   ├── tmp/          # Temporary files
│   └── logs/         # Application logs
├── app/              # Application code
├── static/           # Static files
└── tmp/uploads/      # Upload staging
```

## 🏥 Health Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-17T10:30:00",
  "version": "1.0.0",
  "azure_openai_configured": true,
  "chromadb_configured": true
}
```

### Log Files
- **Access Logs**: `data/logs/access.log`
- **Error Logs**: `data/logs/error.log`
- **Application Logs**: `data/logs/mimir-api.log`

## 🐳 Docker Deployment

### Build and Run
```bash
# Build the image
docker build -t mimir-api .

# Run the container
docker run -p 8000:8000 --env-file .env mimir-api
```

### Production with Docker Compose
```bash
# Start all services
docker-compose up -d

# Scale the API service
docker-compose up --scale mimir-api=3 -d

# View logs
docker-compose logs -f
```

## 📈 Performance Considerations

### Development Settings
- **Workers**: 1 (auto-reload enabled)
- **Timeout**: Default
- **Logging**: Debug level

### Production Settings
- **Workers**: 4 (adjust based on CPU cores)
- **Timeout**: 120 seconds
- **Max Requests**: 1000 per worker
- **Logging**: Info level
- **Preload**: Enabled for better performance

## 🔒 Security

### Environment Variables
- Never commit `.env` files with real credentials
- Use environment-specific configurations
- Rotate API keys regularly

### File Permissions
```bash
# Set proper permissions
chmod 600 .env
chmod 755 data/
chmod 700 data/chromadb/
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill process on port 8000
   sudo lsof -ti:8000 | xargs sudo kill -9
   ```

2. **Permission Denied**
   ```bash
   # Fix script permissions
   chmod +x start-*.sh
   ```

3. **Environment Variables Not Loading**
   ```bash
   # Check .env file
   cat .env
   
   # Test loading
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('AZURE_OPENAI_ENDPOINT'))"
   ```

4. **Dependencies Missing**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

## 🎯 Best Practices

### Development
- Use `start-devcontainer.sh` for consistent environment
- Enable auto-reload for faster development
- Use debug logging level
- Test with `python test_azure_openai.py`

### Production
- Use `start-prod.sh` or Docker Compose
- Configure proper logging
- Set up monitoring and health checks
- Use environment-specific `.env` files
- Implement proper backup strategies for `data/` directory

### Deployment
- Use Docker for consistent deployments
- Set up reverse proxy (nginx) for SSL termination
- Configure log rotation
- Monitor resource usage
- Implement graceful shutdown handling
