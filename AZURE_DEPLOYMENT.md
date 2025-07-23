# Azure App Service Deployment Guide for Mimir API

## 🚀 Azure App Service Deployment

### Prerequisites
- Azure subscription
- Azure CLI installed
- Azure OpenAI resource already created
- GitHub repository (for CI/CD)

## 📋 Step-by-Step Deployment

### 1. Create Azure App Service
```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-mimir-api --location "East US"

# Create App Service Plan (Linux)
az appservice plan create \
    --name plan-mimir-api \
    --resource-group rg-mimir-api \
    --is-linux \
    --sku B1

# Create Web App
az webapp create \
    --name mimir-api-prod \
    --resource-group rg-mimir-api \
    --plan plan-mimir-api \
    --runtime "PYTHON:3.12"
```

### 2. Configure Application Settings

⚠️ **Security Notice**: Never commit secrets to version control. Use Azure App Service Configuration for all sensitive values.

```bash
# Set environment variables in Azure App Service
# IMPORTANT: Replace placeholder values with your actual secrets
az webapp config appsettings set \
    --name mimir-api-prod \
    --resource-group rg-mimir-api \
    --settings \
    AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="your-actual-api-key-here" \
    AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
    AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name" \
    CHROMADB_LOC="/tmp/chromadb" \
    EC_ADMIN_PWD="your-bcrypt-hashed-password-here" \
    JWT_SECRET_KEY="your-jwt-secret-key-here" \
    APP_ENV="production" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# Configure startup command
az webapp config set \
    --name mimir-api-prod \
    --resource-group rg-mimir-api \
    --startup-file "gunicorn --bind 0.0.0.0:8000 app.dependencies:app"
```

### 3. Deploy from GitHub (Recommended)
```bash
# Enable GitHub Actions deployment
az webapp deployment github-actions add \
    --name mimir-api-prod \
    --resource-group rg-mimir-api \
    --repo "https://github.com/dtyago/mimir-api" \
    --branch main \
    --runtime python \
    --runtime-version 3.12
```

### 4. Manual ZIP Deployment (Alternative)
```bash
# Create deployment package
zip -r mimir-api.zip app/ static/ requirements.txt .env.production

# Deploy ZIP file
az webapp deployment source config-zip \
    --name mimir-api-prod \
    --resource-group rg-mimir-api \
    --src mimir-api.zip
```

## � Security Best Practices

### Environment Variables Management
- **✅ DO**: Set all secrets in Azure Portal > App Service > Configuration > Application Settings
- **✅ DO**: Use Azure Key Vault for highly sensitive data
- **✅ DO**: Reference `.env.azure.example` for required variables
- **❌ DON'T**: Commit `.env.azure` with real secrets to version control
- **❌ DON'T**: Hardcode secrets in deployment scripts
- **❌ DON'T**: Share API keys in documentation or chat

### Required Application Settings
Set these in Azure Portal > App Service > Configuration:

| Setting | Example/Description |
|---------|---------------------|
| `AZURE_OPENAI_ENDPOINT` | https://your-resource-name.openai.azure.com/ |
| `AZURE_OPENAI_API_KEY` | Your actual Azure OpenAI API key |
| `AZURE_OPENAI_API_VERSION` | 2024-12-01-preview |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Your model deployment name |
| `CHROMADB_LOC` | /tmp/chromadb |
| `EC_ADMIN_PWD` | Bcrypt hashed admin password |
| `JWT_SECRET_KEY` | Cryptographically secure random key |
| `CORS_ORIGINS` | https://your-app-name.azurewebsites.net |

## 🔧 Configuration Files

### Application Settings (Environment Variables)
Use the table above to configure all required environment variables in Azure Portal.
| `JWT_SECRET_KEY` | Your JWT secret |
| `APP_ENV` | production |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | true |

### Startup Command
```bash
gunicorn --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker --workers 4 --timeout 120 app.dependencies:app
```

## 📊 Monitoring & Logging

### Enable Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
    --app mimir-api-insights \
    --location "East US" \
    --resource-group rg-mimir-api

# Link to App Service
az webapp config appsettings set \
    --name mimir-api-prod \
    --resource-group rg-mimir-api \
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING="your-connection-string"
```

### View Logs
```bash
# Stream logs
az webapp log tail --name mimir-api-prod --resource-group rg-mimir-api

# Download logs
az webapp log download --name mimir-api-prod --resource-group rg-mimir-api
```

## 🔒 Security Considerations

### Key Vault Integration (Recommended)
```bash
# Create Key Vault
az keyvault create \
    --name kv-mimir-api \
    --resource-group rg-mimir-api \
    --location "East US"

# Store secrets
az keyvault secret set --vault-name kv-mimir-api --name "AzureOpenAIKey" --value "your-api-key"
az keyvault secret set --vault-name kv-mimir-api --name "JWTSecret" --value "your-jwt-secret"

# Enable managed identity
az webapp identity assign --name mimir-api-prod --resource-group rg-mimir-api

# Grant Key Vault access
az keyvault set-policy \
    --name kv-mimir-api \
    --object-id $(az webapp identity show --name mimir-api-prod --resource-group rg-mimir-api --query principalId -o tsv) \
    --secret-permissions get list
```

## 🎯 Production Optimizations

### Scaling Configuration
```bash
# Enable auto-scaling
az monitor autoscale create \
    --name mimir-api-autoscale \
    --resource-group rg-mimir-api \
    --resource mimir-api-prod \
    --min-count 1 \
    --max-count 5 \
    --count 2

# Add CPU scaling rule
az monitor autoscale rule create \
    --name cpu-high \
    --resource-group rg-mimir-api \
    --autoscale-name mimir-api-autoscale \
    --condition "Percentage CPU > 70 avg 5m" \
    --scale out 1
```

### Custom Domain & SSL
```bash
# Add custom domain
az webapp config hostname add \
    --webapp-name mimir-api-prod \
    --resource-group rg-mimir-api \
    --hostname "mimir-api.yourdomain.com"

# Enable SSL
az webapp config ssl bind \
    --name mimir-api-prod \
    --resource-group rg-mimir-api \
    --certificate-thumbprint "your-cert-thumbprint" \
    --ssl-type SNI
```

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` for conflicting versions
   - Verify Python version compatibility
   - Check build logs in Deployment Center

2. **Startup Issues**
   - Verify startup command syntax
   - Check application logs
   - Ensure all environment variables are set

3. **Performance Issues**
   - Monitor CPU and memory usage
   - Adjust worker count based on load
   - Enable Application Insights for detailed metrics

### Debugging Commands
```bash
# Check app status
az webapp show --name mimir-api-prod --resource-group rg-mimir-api --query state

# Restart app
az webapp restart --name mimir-api-prod --resource-group rg-mimir-api

# Check configuration
az webapp config appsettings list --name mimir-api-prod --resource-group rg-mimir-api
```

## 📈 Cost Optimization

### Recommended Pricing Tiers
- **Development**: Free (F1) or Basic (B1)
- **Production**: Standard (S1) or Premium (P1v2)
- **High Traffic**: Premium (P2v2) or higher

### Cost Monitoring
```bash
# Set up cost alerts
az consumption budget create \
    --amount 100 \
    --budget-name mimir-api-budget \
    --time-grain Monthly \
    --time-period-start-date "2025-01-01" \
    --time-period-end-date "2025-12-31"
```

## 🎊 Final Checklist

- [ ] Azure App Service created
- [ ] Environment variables configured
- [ ] GitHub Actions deployment set up
- [ ] Application Insights enabled
- [ ] Key Vault integration (optional)
- [ ] Custom domain configured (optional)
- [ ] SSL certificate enabled
- [ ] Auto-scaling configured
- [ ] Cost monitoring enabled
- [ ] Health checks configured
- [ ] Backup strategy implemented
