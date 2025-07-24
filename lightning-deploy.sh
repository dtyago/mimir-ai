#!/bin/bash
# Ultra-fast development deployment using code injection
# This copies only changed Python files into the running container

set -e

echo "⚡ Lightning-fast code deployment to Azure..."

# Configuration
RESOURCE_GROUP="dtyago-rg"
APP_NAME="mimir-api-prod"
ACR_NAME="dc8f1b7ee44d46cc8329c8e71b4c2054"

# Create a minimal update image that just copies new code
TEMP_DIR=$(mktemp -d)
echo "📁 Creating minimal update in: $TEMP_DIR"

# Create a lightweight Dockerfile for code updates only
cat > "$TEMP_DIR/Dockerfile" << 'EOF'
FROM dc8f1b7ee44d46cc8329c8e71b4c2054.azurecr.io/mimir-api:latest
COPY app/ ./app/
COPY static/ ./static/
USER mimir
EOF

# Copy only the application code (not the entire context)
cp -r app/ "$TEMP_DIR/"
cp -r static/ "$TEMP_DIR/"

# Build minimal update image
echo "🚀 Building code-only update..."
cd "$TEMP_DIR"

az acr build --registry $ACR_NAME --image mimir-api:latest .

if [ $? -eq 0 ]; then
    echo "✅ Code update built successfully"
    
    # Restart the app service
    echo "🔄 Restarting App Service..."
    az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP
    
    echo "✅ Lightning deployment complete!"
    echo "⏱️  This should take ~2-3 minutes instead of 11-12 minutes"
else
    echo "❌ Code update failed"
    exit 1
fi

# Cleanup
cd /workspaces/mimir-api
rm -rf "$TEMP_DIR"

# Quick health check
echo "🧪 Testing service..."
HEALTH_URL="https://$APP_NAME-bbdadveqe2dha6hp.canadacentral-01.azurewebsites.net/health"
sleep 20

if curl -s --max-time 10 "$HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ Service is responding!"
else
    echo "⚠️  Service may still be starting up..."
fi

echo ""
echo "💡 Use this for code changes only. Use qd.sh for dependency changes."
