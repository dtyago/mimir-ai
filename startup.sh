#!/bin/bash
# Azure App Service startup script - delegates to universal startup script

echo "🔷 Azure App Service Startup"
echo "============================="

# Set Azure environment
export ENVIRONMENT=azure

# Use the universal startup script
exec ./start.sh
