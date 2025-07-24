#!/bin/bash
# Deploy Mimir API container to Azure App Service
# Updated based on successful deployment experience

set -e

# Check dependencies
echo "🔍 Checking dependencies..."
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is required but not installed."
    echo "   Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "❌ jq is required but not installed."
    echo "   Install with: apt-get install jq (Linux) or brew install jq (macOS)"
    exit 1
fi

# Verify Azure login
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

echo "✅ All dependencies satisfied"

# Configuration - Update these values for your deployment
RESOURCE_GROUP="dtyago-rg"  # Use existing resource group or create new
APP_NAME="mimir-api-prod"
LOCATION="Canada Central"
ACR_NAME=""  # Will be auto-detected or you can specify existing ACR
IMAGE_NAME="mimir-api"
TAG="latest"

echo "🚀 Deploying Mimir API container to Azure App Service"
echo "Resource Group: $RESOURCE_GROUP"
echo "App Name: $APP_NAME"
echo "Location: $LOCATION"
echo "========================================="

# 1. Ensure resource group exists
echo "📁 Ensuring resource group exists..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# 2. Auto-detect existing ACR or create new one
echo "🔍 Checking for existing Azure Container Registry..."
ACR_LIST=$(az acr list --resource-group $RESOURCE_GROUP --query "[].name" --output tsv)

if [ -n "$ACR_LIST" ]; then
    ACR_NAME=$(echo $ACR_LIST | head -n1)
    echo "✅ Found existing ACR: $ACR_NAME"
else
    ACR_NAME="mimirapi$(date +%s)"
    echo "🏗️ Creating new Azure Container Registry: $ACR_NAME"
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Basic \
        --admin-enabled true
fi

# Ensure admin is enabled for simple authentication
echo "🔧 Enabling admin access on ACR..."
az acr update --name $ACR_NAME --admin-enabled true

# 3. Get ACR server and credentials
echo "🔑 Getting ACR server and credentials..."
ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
ACR_CREDENTIALS=$(az acr credential show --name $ACR_NAME --query '{username:username, password:passwords[0].value}' --output json)
ACR_USERNAME=$(echo $ACR_CREDENTIALS | jq -r '.username')
ACR_PASSWORD=$(echo $ACR_CREDENTIALS | jq -r '.password')

echo "ACR Server: $ACR_SERVER"
echo "ACR Username: $ACR_USERNAME"

# 4. Build and push image to ACR
echo "🐳 Building and pushing Docker image..."
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:$TAG \
    .

# 5. Check if App Service already exists
echo "� Checking if App Service exists..."
APP_EXISTS=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "name" --output tsv 2>/dev/null || echo "")

if [ -n "$APP_EXISTS" ]; then
    echo "✅ Found existing App Service: $APP_NAME"
    echo "🔄 Updating existing deployment..."
    
    # Update container configuration
    az webapp config container set \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --container-image-name $ACR_SERVER/$IMAGE_NAME:$TAG \
        --container-registry-url https://$ACR_SERVER \
        --container-registry-user $ACR_USERNAME \
        --container-registry-password $ACR_PASSWORD
    
    # Disable managed identity for ACR (use credentials instead)
    az webapp config set \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --generic-configurations '{"acrUseManagedIdentityCreds": false}'
        
else
    echo "🏗️ Creating new App Service..."
    
    # Create App Service Plan
    echo "📋 Creating App Service Plan..."
    PLAN_EXISTS=$(az appservice plan show --name plan-$APP_NAME --resource-group $RESOURCE_GROUP --query "name" --output tsv 2>/dev/null || echo "")
    
    if [ -z "$PLAN_EXISTS" ]; then
        az appservice plan create \
            --name plan-$APP_NAME \
            --resource-group $RESOURCE_GROUP \
            --is-linux \
            --sku B1
    fi

    # Create Web App with container
    echo "🌐 Creating Web App..."
    az webapp create \
        --resource-group $RESOURCE_GROUP \
        --plan plan-$APP_NAME \
        --name $APP_NAME \
        --deployment-container-image-name $ACR_SERVER/$IMAGE_NAME:$TAG
    
    # Configure container with credentials (not managed identity)
    az webapp config container set \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --container-registry-url https://$ACR_SERVER \
        --container-registry-user $ACR_USERNAME \
        --container-registry-password $ACR_PASSWORD
fi

# 6. Configure application settings (environment variables)
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
    CORS_ORIGINS="https://$APP_NAME.azurewebsites.net" \
    L2_FACE_THRESHOLD="${L2_FACE_THRESHOLD:-0.85}" \
    SESSION_VALIDITY_MINUTES="${SESSION_VALIDITY_MINUTES:-1440}" \
    MAX_FILE_SIZE="${MAX_FILE_SIZE:-50000000}" \
    ALLOWED_FILE_TYPES="${ALLOWED_FILE_TYPES:-application/pdf}" \
    TEMP_UPLOAD_DIR="${TEMP_UPLOAD_DIR:-/tmp/uploads}" \
    USER_DATA_DIR="${USER_DATA_DIR:-/tmp/data}" \
    UPLOAD_DIR="${UPLOAD_DIR:-/tmp/uploads}" \
    FACE_TEMP_DIR="${FACE_TEMP_DIR:-/tmp/face_images}" \
    LOG_LEVEL="${LOG_LEVEL:-INFO}" \
    LOG_FILE="${LOG_FILE:-/tmp/logs/mimir-api.log}" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    PYTHONPATH="/home/site/wwwroot" \
    PORT="8000" \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE="false" \
    WEBSITES_PORT="8000" \
    WEBSITES_CONTAINER_START_TIME_LIMIT="1800" \
    ENVIRONMENT="azure"

# 7. Configure container startup
echo "🚀 Configuring container startup..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "./start.sh"

# 8. Restart the app to apply all changes
echo "🔄 Restarting app to apply changes..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your app URL: https://$APP_NAME.azurewebsites.net"
echo "📖 API Documentation: https://$APP_NAME.azurewebsites.net/docs"
echo ""
echo "🔑 Environment variables configured from .env.azure"
echo "📊 Check deployment status:"
echo "   az webapp browse --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "📋 View logs:"
echo "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "🔧 Download logs:"
echo "   az webapp log download --name $APP_NAME --resource-group $RESOURCE_GROUP --log-file webapp_logs.zip"
