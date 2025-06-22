#!/bin/bash

# Azure AI Foundry & ML Package Allowlist Tool - Example Usage
# Version 0.5.0 (Prerelease)
#
# ⚠️ DISCLAIMER: This example is provided "AS IS" without warranty.
# Always test configurations in non-production environments first.

set -e

# Configuration Variables
WORKSPACE_NAME="${WORKSPACE_NAME:-my-ai-foundry-hub}"
RESOURCE_GROUP="${RESOURCE_GROUP:-my-resource-group}"
SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-your-subscription-id}"
REQUIREMENTS_FILE="${REQUIREMENTS_FILE:-requirements.txt}"
CONDA_ENV="${CONDA_ENV:-environment.yml}"

echo "🔮 Azure AI Foundry & ML Package Allowlist Tool - Example Usage"
echo "============================================================="
echo ""

# Example 1: Basic Azure AI Foundry Hub (Recommended for new projects)
echo "📋 Example 1: Basic AI Foundry Hub Configuration"
echo "Generating allowlist rules for AI Foundry hub with enhanced features..."

python main.py \
  --hub-type ai-foundry \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --requirements-file "$REQUIREMENTS_FILE" \
  --include-vscode \
  --include-huggingface \
  --output-format cli \
  --output-file "output/ai-foundry-basic-rules.sh"

echo "✅ Basic AI Foundry rules generated: output/ai-foundry-basic-rules.sh"
echo ""

# Example 2: Full-Featured AI Foundry Hub
echo "📋 Example 2: Full-Featured AI Foundry Hub"
echo "Including all AI features and Prompt Flow capabilities..."

python main.py \
  --hub-type ai-foundry \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --requirements-file "$REQUIREMENTS_FILE" \
  --conda-env "$CONDA_ENV" \
  --include-vscode \
  --include-huggingface \
  --include-prompt-flow \
  --custom-fqdns "custom-api.company.com,internal-models.corp.com" \
  --output-format cli \
  --output-file "output/ai-foundry-full-rules.sh"

echo "✅ Full-featured AI Foundry rules generated: output/ai-foundry-full-rules.sh"
echo ""

# Example 3: Azure ML Workspace (Fully Supported)
echo "📋 Example 3: Azure ML Workspace Configuration"
echo "Demonstrating complete Azure ML workspace support..."

python main.py \
  --hub-type azure-ml \
  --workspace-name "my-ml-workspace" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --requirements-file "$REQUIREMENTS_FILE" \
  --output-format cli \
  --output-file "output/azure-ml-rules.sh"

echo "✅ Azure ML workspace rules generated: output/azure-ml-rules.sh"
echo ""

# Example 4: Multi-format Package Discovery
echo "📋 Example 4: Multi-format Package Discovery"
echo "Processing multiple package manager files simultaneously..."

python main.py \
  --hub-type ai-foundry \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --requirements-file "requirements.txt" \
  --conda-env "environment.yml" \
  --pyproject-toml "pyproject.toml" \
  --include-vscode \
  --include-huggingface \
  --output-format json \
  --output-file "output/multi-format-config.json"

echo "✅ Multi-format configuration generated: output/multi-format-config.json"
echo ""

# Example 5: Dry Run Testing
echo "📋 Example 5: Dry Run Testing (No API Calls)"
echo "Testing configuration without making external API calls..."

python main.py \
  --dry-run \
  --verbose \
  --hub-type ai-foundry \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --requirements-file "$REQUIREMENTS_FILE" \
  --include-vscode \
  --include-huggingface \
  --include-prompt-flow

echo "✅ Dry run completed - configuration validated"
echo ""

# Docker Examples
echo "📋 Docker Usage Examples"
echo "========================"
echo ""

echo "🐳 Docker Compose - Basic Usage:"
echo "docker-compose run azure-ai-foundry-package-tool"
echo ""

echo "🐳 Docker Compose - Interactive Mode:"
echo "docker-compose run azure-ai-foundry-package-tool-interactive"
echo ""

echo "🐳 Direct Docker Run:"
cat << 'EOF'
docker run -it \
  -v $(pwd)/input:/workspace/input \
  -v $(pwd)/output:/workspace/output \
  -v ~/.azure:/home/azureml-user/.azure:ro \
  azure-ai-foundry-package-tool \
  python main.py --hub-type ai-foundry \
  --workspace-name "your-hub" \
  --resource-group "your-rg" \
  --requirements-file "/workspace/input/requirements.txt" \
  --include-vscode --include-huggingface
EOF

echo ""
echo ""

# Common Patterns
echo "📋 Common Usage Patterns"
echo "========================"
echo ""

echo "🔍 Discovery without applying rules:"
echo "python main.py --dry-run --verbose [your-options]"
echo ""

echo "🔧 Include specific AI features:"
echo "python main.py --include-vscode --include-huggingface --include-prompt-flow [other-options]"
echo ""

echo "🏢 Enterprise custom domains:"
echo "python main.py --custom-fqdns \"api.company.com,models.corp.com\" [other-options]"
echo ""

echo "📊 Multiple output formats:"
echo "python main.py --output-format json --output-file config.json [other-options]"
echo "python main.py --output-format yaml --output-file config.yaml [other-options]"
echo ""

# Best Practices
echo "📋 Best Practices & Tips"
echo "========================"
echo ""

echo "✅ Always test in non-production environments first"
echo "✅ Use --dry-run to validate configuration before applying"
echo "✅ Enable --verbose for troubleshooting"
echo "✅ Consider AI Foundry for new projects (enhanced features)"
echo "✅ Azure ML remains fully supported for existing workspaces"
echo "✅ Include transitive dependencies for complete coverage"
echo "✅ Review private repository warnings carefully"
echo ""

echo "🎉 Example usage script completed!"
echo "📖 For more information, see the documentation in docs/"
echo ""
echo "⚠️  REMINDER: This tool is provided 'AS IS' without warranty."
echo "   Always review and test generated configurations before production use." 