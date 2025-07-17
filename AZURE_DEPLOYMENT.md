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
```bash
# Set environment variables
az webapp config appsettings set \
    --name mimir-api-prod \
    --resource-group rg-mimir-api \
    --settings \
    AZURE_OPENAI_ENDPOINT="https://mimir-base.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="your-api-key" \
    AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o" \
    CHROMADB_LOC="/tmp/chromadb" \
    EC_ADMIN_PWD='$2b$12$yf9rId6L8X04aVIVE/jUluiyhBxyjIiP5lYW8xji4yiOFrfMlrPGu' \
    JWT_SECRET_KEY="WWjndJ4EOMvTxngjx8_1w6cc2YnsRy02HpydJ_NH40I" \
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

## 🔧 Configuration Files

### Application Settings (Environment Variables)
Set these in Azure Portal > App Service > Configuration:

| Setting | Value |
|---------|-------|
| `AZURE_OPENAI_ENDPOINT` | https://mimir-base.openai.azure.com/ |
| `AZURE_OPENAI_API_KEY` | Your actual API key |
| `AZURE_OPENAI_API_VERSION` | 2024-12-01-preview |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | gpt-4o |
| `CHROMADB_LOC` | /tmp/chromadb |
| `EC_ADMIN_PWD` | Your hashed password |
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
