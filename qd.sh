#!/bin/bash
# Quick deployment script for continuous development
# Usage: 
#   ./qd.sh restart     - Just restart the service (~30 seconds)
#   ./qd.sh rebuild     - Rebuild and deploy (~3-5 minutes with caching)
#   ./qd.sh             - Same as rebuild (default)

set -e

# Configuration
RESOURCE_GROUP="dtyago-rg"
APP_NAME="mimir-ai-prod"
ACR_NAME="dc8f1b7ee44d46cc8329c8e71b4c2054"

ACTION=${1:-"rebuild"}

echo "🚀 Quick deploying Mimir API to Azure..."
echo "Action: $ACTION"

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Please login first: az login"
    exit 1
fi

# Get current timestamp for better tracking
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "📅 Starting deployment at: $TIMESTAMP"

if [ "$ACTION" = "restart" ]; then
    echo "🔄 Quick restart (no rebuild)..."
    echo "   This only restarts the service with the existing image"
    echo "   Use this when you want to test if the current deployment works"
    echo ""
    
    az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP
    
    if [ $? -eq 0 ]; then
        echo "✅ App Service restart completed"
    else
        echo "❌ App Service restart failed"
        exit 1
    fi
    
    echo "⏳ Waiting for service to come online..."
    sleep 15
    
elif [ "$ACTION" = "rebuild" ]; then
    echo "📦 Building and pushing image to Azure Container Registry..."
    echo "   Registry: $ACR_NAME"
    echo "   Image: mimir-ai:latest"
    echo "   This will use Docker layer caching to speed up builds"
    echo ""

    # Build and push using Azure Container Registry build service with caching
    az acr build --registry $ACR_NAME --image mimir-ai:latest . --platform linux --file Dockerfile.azure

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

else
    echo "❌ Unknown action: $ACTION"
    echo "Usage: $0 [restart|rebuild]"
    echo "  restart - Just restart the service (~30 seconds)"
    echo "  rebuild - Rebuild and deploy (~3-5 minutes)"
    exit 1
fi

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
echo "💡 Usage tips:"
echo "   • ./qd.sh restart  - Just restart (~30 seconds)"
echo "   • ./qd.sh rebuild  - Rebuild with caching (~3-5 minutes)"
echo "   • Use 'deploy-container-to-azure.sh' for major changes or environment updates"
echo "   • Use './start.sh' for local development with hot reload"
