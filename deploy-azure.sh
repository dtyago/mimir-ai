#!/bin/bash
# Azure App Service production deployment script

echo "🔷 Deploying Mimir API to Azure App Service"
echo "==========================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    echo "   Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo "🔑 Please login to Azure..."
    az login
fi

# Set variables
RESOURCE_GROUP="rg-mimir-api"
APP_SERVICE_PLAN="plan-mimir-api"
WEB_APP_NAME="mimir-api-prod"
LOCATION="East US"
PYTHON_VERSION="3.12"

echo "📋 Deployment Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   App Service Plan: $APP_SERVICE_PLAN"
echo "   Web App: $WEB_APP_NAME"
echo "   Location: $LOCATION"
echo "   Python Version: $PYTHON_VERSION"
echo ""

# Create resource group if it doesn't exist
echo "📁 Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION" --output table

# Create App Service Plan if it doesn't exist
echo "📊 Creating App Service Plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --is-linux \
    --sku B1 \
    --location "$LOCATION" \
    --output table

# Create Web App if it doesn't exist
echo "🌐 Creating Web App..."
az webapp create \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --runtime "PYTHON:$PYTHON_VERSION" \
    --output table

# Configure startup command
echo "⚙️ Configuring startup command..."
az webapp config set \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "startup.py" \
    --output table

# Set application settings from .env.azure
echo "🔧 Setting application settings..."
if [ -f ".env.azure" ]; then
    echo "⚠️  .env.azure contains template values. Please update with actual values."
    echo "You can set environment variables manually or use azure-config.sh"
    
    # Prompt for actual values instead of reading from file
    echo "Setting up Azure OpenAI configuration..."
    read -p "Enter your Azure OpenAI Endpoint: " AZURE_OPENAI_ENDPOINT
    read -p "Enter your Azure OpenAI API Key: " AZURE_OPENAI_API_KEY
    read -p "Enter your Azure OpenAI Deployment Name: " AZURE_OPENAI_DEPLOYMENT_NAME
    read -p "Enter your hashed admin password: " EC_ADMIN_PWD
    read -p "Enter your JWT secret key: " JWT_SECRET_KEY
    
    # Set application settings
    az webapp config appsettings set \
        --name $WEB_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --settings \
        AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
        AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
        AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
        AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
        CHROMADB_LOC="/tmp/chromadb" \
        EC_ADMIN_PWD="$EC_ADMIN_PWD" \
        JWT_SECRET_KEY="$JWT_SECRET_KEY" \
        APP_ENV="production" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
        --output table
else
    echo "⚠️  .env.azure file not found. Please create it with your configuration."
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."
zip -r mimir-api-deploy.zip app/ static/ requirements.txt startup.py web.config

# Deploy the application
echo "🚀 Deploying application..."
az webapp deployment source config-zip \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --src mimir-api-deploy.zip \
    --output table

# Clean up deployment package
rm mimir-api-deploy.zip

# Enable logging
echo "📝 Enabling application logging..."
az webapp log config \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --application-logging filesystem \
    --level information \
    --output table

# Get the application URL
APP_URL=$(az webapp show --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --query defaultHostName -o tsv)

echo ""
echo "🎉 Deployment completed successfully!"
echo "📍 Your application is available at: https://$APP_URL"
echo "🔍 Health check: https://$APP_URL/health"
echo "👨‍💼 Admin interface: https://$APP_URL"
echo ""
echo "📊 To monitor your application:"
echo "   az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "🔧 To restart your application:"
echo "   az webapp restart --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
