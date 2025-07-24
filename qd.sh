#!/bin/bash
# Quick deployment script for continuous development
# Use this for small changes, use deploy-container-to-azure.sh for major changes

set -e

echo "🚀 Quick deploying Mimir API to Azure..."

# Configuration
RESOURCE_GROUP="dtyago-rg"
APP_NAME="mimir-api-prod"
ACR_NAME="dc8f1b7ee44d46cc8329c8e71b4c2054"

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Please login first: az login"
    exit 1
fi

# Get current timestamp for better tracking
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "📅 Starting deployment at: $TIMESTAMP"

echo "📦 Building and pushing image to Azure Container Registry..."
echo "   Registry: $ACR_NAME"
echo "   Image: mimir-api:latest"

# Build and push using Azure Container Registry build service
az acr build --registry $ACR_NAME --image mimir-api:latest .

if [ $? -eq 0 ]; then
    echo "✅ Image built and pushed successfully"
else
    echo "❌ Image build failed"
    exit 1
fi

echo "🔄 Restarting App Service to pull new image..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

if [ $? -eq 0 ]; then
    echo "✅ App Service restart initiated"
else
    echo "❌ App Service restart failed"
    exit 1
fi

echo "⏳ Waiting for deployment to complete..."
sleep 30

# Test if the service is responding
echo "🧪 Testing deployment..."
HEALTH_URL="https://$APP_NAME-bbdadveqe2dha6hp.canadacentral-01.azurewebsites.net/health"

# Try to get health status with timeout
if curl -s --max-time 10 "$HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ Service is responding!"
else
    echo "⚠️  Service may still be starting up..."
fi

COMPLETE_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo ""
echo "🎉 Quick deployment complete!"
echo "📅 Completed at: $COMPLETE_TIMESTAMP"
echo "🌐 URL: https://$APP_NAME-bbdadveqe2dha6hp.canadacentral-01.azurewebsites.net/"
echo ""
echo "💡 Tip: Use 'deploy-container-to-azure.sh' for major changes or environment updates"
