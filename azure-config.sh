#!/bin/bash
# Azure App Service configuration helper script

echo "🔷 Azure App Service Configuration Helper"
echo "========================================"

WEB_APP_NAME="mimir-api-prod"
RESOURCE_GROUP="rg-mimir-api"

# Function to show current configuration
show_config() {
    echo "📋 Current Configuration:"
    az webapp config appsettings list \
        --name $WEB_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --output table
}

# Function to update Azure OpenAI settings
update_openai_config() {
    echo "🔧 Updating Azure OpenAI configuration..."
    
    read -p "Enter Azure OpenAI Endpoint: " endpoint
    read -p "Enter Azure OpenAI API Key: " api_key
    read -p "Enter Deployment Name: " deployment_name
    
    az webapp config appsettings set \
        --name $WEB_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --settings \
        AZURE_OPENAI_ENDPOINT="$endpoint" \
        AZURE_OPENAI_API_KEY="$api_key" \
        AZURE_OPENAI_DEPLOYMENT_NAME="$deployment_name" \
        --output table
}

# Function to restart the app
restart_app() {
    echo "🔄 Restarting application..."
    az webapp restart --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --output table
}

# Function to stream logs
stream_logs() {
    echo "📝 Streaming application logs..."
    az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP
}

# Function to check app status
check_status() {
    echo "🔍 Checking application status..."
    az webapp show --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --query "{name:name,state:state,defaultHostName:defaultHostName}" --output table
    
    echo ""
    echo "🏥 Health Check:"
    curl -s "https://$WEB_APP_NAME.azurewebsites.net/health" | python -m json.tool
}

# Function to scale the app
scale_app() {
    echo "📊 Current App Service Plan:"
    az appservice plan show --name plan-mimir-api --resource-group $RESOURCE_GROUP --query "{name:name,sku:sku}" --output table
    
    echo ""
    echo "Available SKUs: F1 (Free), B1 (Basic), S1 (Standard), P1v2 (Premium)"
    read -p "Enter new SKU (or press Enter to skip): " sku
    
    if [ ! -z "$sku" ]; then
        az appservice plan update --name plan-mimir-api --resource-group $RESOURCE_GROUP --sku $sku --output table
    fi
}

# Main menu
echo "Select an option:"
echo "1. Show current configuration"
echo "2. Update Azure OpenAI settings"
echo "3. Restart application"
echo "4. Stream logs"
echo "5. Check application status"
echo "6. Scale application"
echo "7. Exit"

read -p "Enter your choice (1-7): " choice

case $choice in
    1) show_config ;;
    2) update_openai_config ;;
    3) restart_app ;;
    4) stream_logs ;;
    5) check_status ;;
    6) scale_app ;;
    7) echo "Goodbye!" ;;
    *) echo "Invalid choice. Please run the script again." ;;
esac
