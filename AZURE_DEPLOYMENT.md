# Azure App Service Deployment Guide for Mimir API

This guide covers deploying the Mimir API to Azure App Service using our streamlined deployment script.

## 🚀 Quick Start

### Prerequisites
- Azure CLI installed and logged in (`az login`)
- Access to an Azure subscription
- VS Code DevContainer environment (recommended)

### One-Command Deployment

```bash
# 1. Configure your deployment
cp .env.azure.example .env.azure
# Edit .env.azure with your values

# 2. Deploy to Azure
./deploy-container-to-azure.sh
```

## ⚙️ Configuration

### Step 1: Configure Environment Variables

Copy the example configuration and customize it:

```bash
cp .env.azure.example .env.azure
```

Edit `.env.azure` with your values:

```bash
## Azure Deployment Configuration
RESOURCE_GROUP=your-resource-group-name
LOCATION="Canada Central"  # or your preferred region
APP_NAME=your-app-service-name
ACR_NAME=your-container-registry-name  # optional, auto-detected if empty

## Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

## Security Configuration
EC_ADMIN_PWD=your-bcrypt-hashed-password
JWT_SECRET_KEY=your-jwt-secret
```

### Step 2: Generate Security Credentials

Generate a secure admin password hash:
```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'YourSecurePassword123!', bcrypt.gensalt()).decode())"
```

Generate a JWT secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 🛠️ Deployment Process

### Automated Deployment

The `deploy-container-to-azure.sh` script handles everything:

```bash
./deploy-container-to-azure.sh
```

**What it does:**
1. ✅ Validates configuration and dependencies
2. ✅ Creates/detects Azure Resource Group
3. ✅ Creates/detects Azure Container Registry
4. ✅ Builds Docker image using Azure Container Registry (cloud-based)
5. ✅ Creates/updates Azure App Service
6. ✅ Configures all environment variables
7. ✅ Deploys the container and restarts the service

**No local Docker required** - everything builds in Azure!

### What Gets Created

The deployment script creates/manages these Azure resources:

- **Resource Group**: Contains all your resources
- **App Service Plan**: Linux-based, B1 SKU (Basic tier)
- **App Service**: Your web application
- **Container Registry**: Stores your Docker images

## 🎯 Key Features

### Intelligent Resource Management
- **Auto-detection**: Finds existing resources to avoid duplicates
- **Smart Updates**: Updates existing deployments seamlessly
- **Validation**: Checks configuration before deployment

### Security Best Practices
- **Container Registry**: Private registry with admin credentials
- **Environment Variables**: Securely configured in Azure App Service
- **Bcrypt Hashing**: Admin passwords are properly hashed
- **JWT Tokens**: Secure session management

### Production Ready
- **Health Checks**: Built-in container health monitoring
- **Logging**: Azure App Service log streams
- **Performance**: Optimized startup and runtime configuration
- **Scalability**: Easy to scale up/out as needed

## 🔍 Monitoring & Troubleshooting

### View Application Logs
```bash
# Stream live logs
az webapp log tail --name your-app-name --resource-group your-resource-group

# Download log files
az webapp log download --name your-app-name --resource-group your-resource-group --log-file webapp_logs.zip
```

### Check Deployment Status
```bash
# Open app in browser
az webapp browse --name your-app-name --resource-group your-resource-group

# Check app service status
az webapp show --name your-app-name --resource-group your-resource-group --query "state"
```

### Common Issues

#### Container Won't Start
- Check environment variables are set correctly
- Verify Docker image was built successfully
- Review container logs in Azure Portal

#### Authentication Issues
- Verify Azure OpenAI credentials
- Check admin password hash is correct
- Ensure JWT secret is properly configured

#### Performance Issues
- Consider scaling up to higher SKU (S1, P1V2, etc.)
- Monitor resource usage in Azure Portal
- Check for memory/CPU limits

## 🔄 Updates & Maintenance

### Quick Updates (Code Only)
If you only changed application code and not environment variables:

```bash
# Quick rebuild and redeploy container
./qd.sh rebuild
```

### Full Updates (Code + Configuration)
If you changed environment variables or configuration:

```bash
# Full deployment with environment sync
./deploy-container-to-azure.sh
```

### Configuration Changes Only
If you only changed environment variables:

```bash
# Just update configuration (faster than full deployment)
./deploy-container-to-azure.sh
# The script detects existing resources and only updates settings
```

## 🔐 Security Considerations

### Environment Variables
- Never commit `.env.azure` to version control
- Use strong, unique passwords
- Rotate credentials regularly
- Use Azure Key Vault for additional security

### Network Security
- Consider using Private Endpoints for production
- Configure custom domains with SSL certificates
- Set up IP restrictions if needed

### Access Control
- Use Azure AD for team access
- Set up proper RBAC roles
- Monitor access logs

## 📊 Cost Optimization

### App Service Plan Sizing
- **B1 Basic**: Good for development/testing ($13-15/month)
- **S1 Standard**: Production workloads ($56-70/month)
- **P1V2 Premium**: High-performance applications ($146-182/month)

### Container Registry
- **Basic**: Sufficient for most use cases ($5/month)
- Includes 10 GB storage and unlimited private repositories

### Tips
- Scale down during off-hours
- Use deployment slots for zero-downtime updates
- Monitor usage with Azure Cost Management

## 🚀 Next Steps

After successful deployment:

1. **Access your application**: `https://your-app-name.azurewebsites.net`
2. **Admin login**: `/admin` with username `admin` and your configured password
3. **API documentation**: `/docs` for interactive API explorer
4. **Set up monitoring**: Configure Application Insights
5. **Custom domain**: Add your own domain name
6. **SSL certificate**: Enable HTTPS with custom domains

## 📚 Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure Container Registry Documentation](https://docs.microsoft.com/en-us/azure/container-registry/)
- [Mimir API Documentation](./README.md)
- [Manual Deployment Steps](./DEPLOYMENT.md)
