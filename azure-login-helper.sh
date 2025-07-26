#!/bin/bash
# Azure Authentication Helper for Deployment
# Explains different authentication methods and provides guidance

echo "🔐 Azure Authentication Methods for Container Deployment"
echo "========================================================="
echo ""

# Check current login status
if az account show &> /dev/null; then
    CURRENT_ACCOUNT=$(az account show --query "name" --output tsv)
    CURRENT_USER=$(az account show --query "user.name" --output tsv 2>/dev/null || echo "Service Principal")
    echo "✅ Already logged in to Azure"
    echo "   Account: $CURRENT_ACCOUNT"
    echo "   User: $CURRENT_USER"
    echo ""
    read -p "🤔 Continue with current authentication? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "🔄 Please choose a new authentication method below..."
    else
        echo "✅ Proceeding with current authentication..."
        exit 0
    fi
fi

echo "💡 Why login can't be fully automated in scripts:"
echo "   - Azure uses OAuth 2.0 flow requiring browser interaction"
echo "   - Security best practice to prevent credential exposure"
echo "   - Interactive consent required for first-time access"
echo ""

echo "🔐 Available Authentication Methods:"
echo ""

echo "1️⃣  INTERACTIVE LOGIN (Recommended for Development)"
echo "   - Opens browser for secure authentication"
echo "   - Best for personal development environments"
echo "   Command: az login"
echo ""

echo "2️⃣  DEVICE CODE LOGIN (Good for Remote/Codespaces)"
echo "   - No browser required on the machine"
echo "   - Use another device to complete authentication"
echo "   - Good for devcontainers, remote servers, etc."
echo "   Command: az login --use-device-code"
echo ""

echo "3️⃣  SERVICE PRINCIPAL (For CI/CD Automation)"
echo "   - Non-interactive authentication"
echo "   - Requires pre-created service principal"
echo "   - Best for automated deployments"
echo "   Setup:"
echo "     az ad sp create-for-rbac --name 'mimir-deploy' --role contributor"
echo "   Usage:"
echo "     az login --service-principal -u <app-id> -p <password> --tenant <tenant>"
echo ""

echo "4️⃣  MANAGED IDENTITY (For Azure Resources)"
echo "   - Automatic authentication for Azure VMs/App Service"
echo "   - No credentials to manage"
echo "   Command: az login --identity"
echo ""

echo "🎯 Recommendation for your setup:"
if [[ "$CODESPACE_NAME" != "" ]]; then
    echo "   You're in GitHub Codespaces - use DEVICE CODE LOGIN (option 2)"
    RECOMMENDED="device-code"
elif [[ "$VSCODE_REMOTE_CONTAINERS_SESSION" != "" ]]; then
    echo "   You're in VS Code devcontainer - use DEVICE CODE LOGIN (option 2)"
    RECOMMENDED="device-code"
else
    echo "   You're in local environment - use INTERACTIVE LOGIN (option 1)"
    RECOMMENDED="interactive"
fi
echo ""

read -p "🚀 Which method would you like to use? (1/2/3/4): " -n 1 -r
echo ""

case $REPLY in
    1)
        echo "🔑 Starting interactive login..."
        az login
        ;;
    2)
        echo "📱 Starting device code login..."
        echo "💡 You'll get a code to enter on another device"
        az login --use-device-code
        ;;
    3)
        echo "🤖 Service Principal Login"
        read -p "   App ID: " APP_ID
        read -s -p "   Password/Secret: " PASSWORD
        echo ""
        read -p "   Tenant ID: " TENANT_ID
        az login --service-principal -u "$APP_ID" -p "$PASSWORD" --tenant "$TENANT_ID"
        ;;
    4)
        echo "🎯 Managed Identity Login"
        az login --identity
        ;;
    *)
        echo "❌ Invalid option. Please run the script again."
        exit 1
        ;;
esac

# Verify login worked
if az account show &> /dev/null; then
    echo ""
    echo "✅ Successfully authenticated to Azure!"
    ACCOUNT_NAME=$(az account show --query "name" --output tsv)
    USER_NAME=$(az account show --query "user.name" --output tsv 2>/dev/null || echo "Service Principal")
    echo "   Account: $ACCOUNT_NAME"
    echo "   User: $USER_NAME"
    echo ""
    echo "🚀 Now you can run: ./deploy-container-to-azure.sh"
else
    echo ""
    echo "❌ Authentication failed. Please try again or check your credentials."
    exit 1
fi
