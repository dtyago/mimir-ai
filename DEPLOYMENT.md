# Mimir API Deployment Guide

## 🚀 Starting the Application

### Universal Startup Script

The project now uses a single universal startup script that automatically detects your environment:

```bash
# Start the application (auto-detects environment)
./start.sh
```

**Environment Detection:**
- **DevContainer**: Auto-detected when running in VS Code DevContainer
- **Azure App Service**: Auto-detected when Azure environment variables are present  
- **Production**: Set `ENVIRONMENT=production` or `APP_ENV=production`
- **Development**: Default fallback for local development

### Environment-Specific Options

#### Option 1: DevContainer (Recommended)
```bash
# In VS Code DevContainer (auto-detected)
./start.sh
```
⚠️ **Important:** Use local DevContainer only. **GitHub Codespaces is NOT supported** due to incompatible SQLite version (3.34.1 vs required 3.35.0+).

#### Option 2: Docker Compose
```bash
# Docker Compose deployment
docker-compose up --build
```

#### Option 3: Local Development
```bash
# Local development with auto-detection
./start.sh

# Or explicitly set environment
ENVIRONMENT=development ./start.sh
```

#### Option 3: Production
```bash
# Production deployment
ENVIRONMENT=production ./start.sh

# Or with Docker
docker run -p 8000:8000 --env-file .env mimir-api
```

#### Option 4: Manual Development Start
```bash
# Load environment variables
source .env

# Start with auto-reload
uvicorn app.dependencies:app --host 0.0.0.0 --port 8000 --reload --log-level info
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

1. **Startup Hanging or Missing .env File**
   ```bash
   # Check if .env exists
   ls -la .env
   
   # If missing, copy from example and edit
   cp .env.example .env
   nano .env  # Edit with your Azure OpenAI credentials
   
   # Or create a basic development .env
   cat > .env << 'EOF'
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   EC_ADMIN_PWD=$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewAV2Y1R/yLo1Fy.
   JWT_SECRET_KEY=dev-secret-key-change-in-production
   CHROMADB_LOC=/app/data/chromadb
   APP_ENV=development
   EOF
   ```

2. **Port Already in Use**
   ```bash
   # Kill process on port 8000
   sudo lsof -ti:8000 | xargs sudo kill -9
   ```

3. **Permission Denied**
   ```bash
   # Fix script permissions
   chmod +x start.sh startup.sh
   ```

4. **Environment Variables Not Loading**
   ```bash
   # Check .env file
   cat .env
   
   # Test loading
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('AZURE_OPENAI_ENDPOINT'))"
   ```

5. **Dependencies Missing**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

## 🎯 Best Practices

### Development
- Use `./start.sh` for consistent environment
- Enable auto-reload for faster development  
- Use debug logging level
- Test with health endpoint: `curl http://localhost:8000/health`

### Production
- Use `./start.sh` or Docker Compose for deployment
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
