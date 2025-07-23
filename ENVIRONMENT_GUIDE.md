# 🚀 Environment-Aware Deployment Guide

This project now supports smart environment file detection:

## 📁 **Environment File Strategy**

### **Local Development** (.env)
- Used by: Docker Desktop, DevContainer, local development
- File: `.env` 
- Purpose: Development settings with local paths
- Security: Gitignored, safe for development secrets

### **Azure Deployment** (.env.azure)
- Used by: Terminal-based Azure deployments
- File: `.env.azure`
- Purpose: Production settings with Azure paths
- Security: Gitignored, contains production secrets

## 🎯 **How It Works**

### **Local Development:**
```bash
# Docker Desktop
docker-compose up --build

# DevContainer 
./start.sh
# → Automatically uses .env file
```

### **Azure Deployment:**
```bash
# Terminal deployment
./deploy-container-to-azure.sh
# → Automatically uses .env.azure file
```

## 📋 **Setup Instructions**

### 1. Configure Local Development
Your `.env` file is already set up for local development.

### 2. Configure Azure Deployment
```bash
# Your .env.azure is ready with production settings
# Just verify the values are correct for your Azure resources
```

### 3. Deploy to Azure
```bash
# Simple one-command deployment
./deploy-container-to-azure.sh
```

## 🔄 **Environment File Priority**

| Context | File Used | Description |
|---------|-----------|-------------|
| **Azure App Service** | Environment Variables | Set by Azure Portal/Deployment |
| **Azure Deployment** | `.env.azure` | Production config for deployment |
| **Local Development** | `.env` | Development config for local work |
| **DevContainer** | `.env` | Development config in container |

## 🛡️ **Security Features**

- ✅ **Both .env files are gitignored** - no secrets in version control
- ✅ **Automatic environment detection** - uses the right config for each context
- ✅ **Production vs Development separation** - different settings for each environment
- ✅ **Fallback to environment variables** - if files don't exist
- ✅ **Validation checks** - ensures all required variables are set

## 🔧 **Customization**

### Update Production Settings
Edit `.env.azure` to change:
- Azure OpenAI endpoints
- Security credentials
- CORS origins
- Logging levels

### Update Development Settings  
Edit `.env` to change:
- Local development paths
- Debug settings
- Development credentials

## 🚀 **Quick Commands**

```bash
# Local development
docker-compose up --build

# Deploy to Azure
./deploy-container-to-azure.sh

# Check environment variables are loaded
./start.sh --check-env
```

This approach gives you the best of both worlds: easy local development and secure Azure deployment! 🎉
