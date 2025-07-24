# Deployment Scripts Guide

## Scripts Overview

### 🚀 `start.sh` - Local Development
- **Purpose**: Universal startup script for local development
- **Usage**: `./start.sh`
- **Features**: 
  - Auto-detects environment (DevContainer, production, etc.)
  - Hot reload for development
  - Handles all environment setup
- **When to use**: Local development in DevContainer or Docker

### ⚡ `qd.sh` - Quick Azure Deployment
- **Purpose**: Fast deployment to Azure App Service
- **Usage**: 
  - `./qd.sh restart` - Just restart service (~30 seconds)
  - `./qd.sh rebuild` - Rebuild with Docker caching (~3-5 minutes)
- **When to use**: 
  - Code changes that don't require dependency updates
  - Testing deployments
  - Quick iterations

### 🏗️ `deploy-container-to-azure.sh` - Full Deployment
- **Purpose**: Complete deployment with environment setup
- **Usage**: `./deploy-container-to-azure.sh`
- **Features**:
  - Creates Azure resources if needed
  - Sets up environment variables
  - Configures health checks
  - Full production deployment
- **When to use**: 
  - First-time deployment
  - Major changes (dependencies, environment variables)
  - Production releases

## Recommended Workflow

1. **Development**: Use `./start.sh` for local development with hot reload
2. **Quick Testing**: Use `./qd.sh restart` to test current deployment
3. **Code Changes**: Use `./qd.sh rebuild` for new code deployment
4. **Major Changes**: Use `./deploy-container-to-azure.sh` for full deployment

## Performance Comparison

| Script | Time | Use Case |
|--------|------|----------|
| `start.sh` | ~10 seconds | Local development |
| `qd.sh restart` | ~30 seconds | Test current deployment |
| `qd.sh rebuild` | ~3-5 minutes | Code changes |
| `deploy-container-to-azure.sh` | ~8-12 minutes | Full deployment |
