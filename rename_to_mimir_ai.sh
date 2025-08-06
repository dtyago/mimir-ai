#!/bin/bash
echo "🔄 Renaming mimir-api to mimir-ai..."
echo "=================================================="

# Update README.md and all documentation
echo "📝 Updating documentation files..."
find . -name "*.md" -type f -exec sed -i 's/mimir-api/mimir-ai/g' {} \;

# Update deployment scripts
echo "🚀 Updating deployment scripts..."
if [ -f "deploy-container-to-azure.sh" ]; then
    sed -i 's/mimir-api/mimir-ai/g' deploy-container-to-azure.sh
    sed -i 's/mimirapiacr/mimiraiacr/g' deploy-container-to-azure.sh
    sed -i 's/DEFAULT_ACR_NAME="mimirap"/DEFAULT_ACR_NAME="mimirai"/g' deploy-container-to-azure.sh
fi

if [ -f "qd.sh" ]; then
    sed -i 's/mimir-api/mimir-ai/g' qd.sh
fi

# Update docker-compose.yml
echo "🐳 Updating Docker configuration..."
if [ -f "docker-compose.yml" ]; then
    sed -i 's/mimir-api/mimir-ai/g' docker-compose.yml
fi

# Update GitHub URLs in documentation
echo "🔗 Updating GitHub repository URLs..."
find . -name "*.md" -exec sed -i 's/github.com\/dtyago\/mimir-api/github.com\/dtyago\/mimir-ai/g' {} \;

# Update project structure references in README
echo "📁 Updating project structure references..."
sed -i 's/mimir-api\//mimir-ai\//g' README.md

# Update any remaining references in shell scripts
echo "📜 Updating shell scripts..."
find . -name "*.sh" -not -name "rename_to_mimir_ai.sh" -exec sed -i 's/mimir-api/mimir-ai/g' {} \;

echo ""
echo "✅ File updates completed!"
echo ""
echo "📋 Summary of changes:"
echo "   ✓ All documentation updated"
echo "   ✓ Deployment scripts updated"
echo "   ✓ Container names updated"
echo "   ✓ GitHub URLs updated"
echo "   ✓ Project structure references updated"
echo ""
echo "🔍 Files affected:"
git diff --name-only 2>/dev/null || echo "   (Changes will be visible after git add)"
echo ""
echo "📝 Next steps:"
echo "1. Review changes: git diff"
echo "2. Test locally: ./start.sh"
echo "3. Commit changes"
echo "4. Update Git remote"
