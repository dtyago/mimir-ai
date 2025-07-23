#!/bin/bash
# Deploy Mimir API container to Azure App Service

set -e

# Configuration
RESOURCE_GROUP="rg-mimir-api"
APP_NAME="mimir-api-prod"
LOCATION="East US"
ACR_NAME="mimirapi$(date +%s)"  # Unique ACR name
IMAGE_NAME="mimir-api"
TAG="latest"

echo "🚀 Deploying Mimir API container to Azure App Service"
echo "Resource Group: $RESOURCE_GROUP"
echo "App Name: $APP_NAME"
echo "ACR Name: $ACR_NAME"
echo "========================================="

# 1. Create resource group
echo "📁 Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# 2. Create Azure Container Registry
echo "🏗️ Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# 3. Get ACR credentials
echo "🔑 Getting ACR credentials..."
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

echo "ACR Server: $ACR_SERVER"

# 4. Build and push image to ACR
echo "🐳 Building and pushing Docker image..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:$TAG \
    .

# 5. Create App Service Plan
echo "📋 Creating App Service Plan..."
az appservice plan create \
    --name plan-$APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --is-linux \
    --sku B1

# 6. Create Web App with container
echo "🌐 Creating Web App..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan plan-$APP_NAME \
    --name $APP_NAME \
    --deployment-container-image-name $ACR_SERVER/$IMAGE_NAME:$TAG

# 7. Configure container registry credentials
echo "🔐 Configuring container registry credentials..."
az webapp config container set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name $ACR_SERVER/$IMAGE_NAME:$TAG \
    --docker-registry-server-url https://$ACR_SERVER \
    --docker-registry-server-user $ACR_USERNAME \
    --docker-registry-server-password $ACR_PASSWORD

# 8. Configure application settings (environment variables)
echo "⚙️ Configuring application settings..."

# Check if .env.azure exists and load it
if [ -f ".env.azure" ]; then
    echo "📁 Loading environment variables from .env.azure..."
    set -a  # Automatically export all variables
    source .env.azure
    set +a  # Stop auto-exporting
else
    echo "⚠️  .env.azure not found, checking individual environment variables..."
fi

# Validate required environment variables are set
required_env_vars=(
    "AZURE_OPENAI_ENDPOINT"
    "AZURE_OPENAI_API_KEY" 
    "AZURE_OPENAI_DEPLOYMENT_NAME"
    "EC_ADMIN_PWD"
    "JWT_SECRET_KEY"
)

echo "🔍 Validating required environment variables..."
missing_vars=()
for var in "${required_env_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "📋 To fix this, either:"
    echo "   1. Create .env.azure file with your production values"
    echo "   2. Or set these environment variables manually:"
    echo "      export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'"
    echo "      export AZURE_OPENAI_API_KEY='your-actual-api-key'"
    echo "      export AZURE_OPENAI_DEPLOYMENT_NAME='your-deployment-name'"
    echo "      export EC_ADMIN_PWD='your-bcrypt-hashed-password'"
    echo "      export JWT_SECRET_KEY='your-jwt-secret-key'"
    exit 1
fi

echo "✅ All required environment variables are set"

az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
    AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
    AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
    AZURE_OPENAI_API_VERSION="${AZURE_OPENAI_API_VERSION:-2024-12-01-preview}" \
    AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
    CHROMADB_LOC="${CHROMADB_LOC:-/tmp/chromadb}" \
    EC_ADMIN_PWD="$EC_ADMIN_PWD" \
    JWT_SECRET_KEY="$JWT_SECRET_KEY" \
    APP_ENV="${APP_ENV:-production}" \
    APP_HOST="${APP_HOST:-0.0.0.0}" \
    APP_PORT="${APP_PORT:-8000}" \
    DEBUG="${DEBUG:-false}" \
    AUTO_RELOAD="${AUTO_RELOAD:-false}" \
    USER_DATA_DIR="${USER_DATA_DIR:-/tmp/data}" \
    UPLOAD_DIR="${UPLOAD_DIR:-/tmp/uploads}" \
    LOG_FILE="${LOG_FILE:-/tmp/logs/mimir-api.log}" \
    LOG_LEVEL="${LOG_LEVEL:-INFO}" \
    CORS_ORIGINS="${CORS_ORIGINS:-}" \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE="false" \
    WEBSITES_PORT="8000"

# 9. Configure startup command
echo "🚀 Configuring startup command..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "./start.sh"

echo "✅ Deployment complete!"
echo "🌐 Your app URL: https://$APP_NAME.azurewebsites.net"
echo ""
echo "🔑 Environment variables configured from .env.azure"
echo "📊 Check deployment status:"
echo "   az webapp browse --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "📋 View logs:"
echo "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
