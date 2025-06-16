#!/bin/bash

# Example usage scenarios for the Azure ML Package URL Allowlist Tool
# Run these examples to test different scenarios

set -e

echo "🚀 Azure ML Package URL Allowlist Tool - Examples"
echo "================================================="
echo ""

# Set your workspace details
WORKSPACE_NAME="${WORKSPACE_NAME:-your-workspace-name}"
RESOURCE_GROUP="${RESOURCE_GROUP:-your-resource-group}"
SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-your-subscription-id}"

echo "Using workspace: $WORKSPACE_NAME"
echo "Resource group: $RESOURCE_GROUP"
echo "Subscription: $SUBSCRIPTION_ID"
echo ""

# Example 1: Azure AI Foundry Hub with VS Code and HuggingFace
echo "🔮 Example 1: Azure AI Foundry Hub with AI features..."
python main.py \
  --hub-type ai-foundry \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --requirements-file "examples/example-requirements.txt" \
  --include-vscode \
  --include-huggingface \
  --output-format cli \
  --output-file "output/example1-ai-foundry.sh" \
  --verbose

echo "✅ Output saved to: output/example1-ai-foundry.sh"
echo ""

# Example 2: Traditional Azure ML Workspace
echo "🤖 Example 2: Traditional Azure ML workspace..."
python main.py \
  --hub-type azure-ml \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --conda-env "examples/example-environment.yml" \
  --output-format cli \
  --output-file "output/example2-azure-ml.sh" \
  --verbose

echo "✅ Output saved to: output/example2-azure-ml.sh"
echo ""

# Example 3: JSON output format
echo "📦 Example 3: JSON output format..."
python main.py \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --requirements-file "examples/example-requirements.txt" \
  --output-format json \
  --output-file "output/example3-config.json" \
  --verbose

echo "✅ Output saved to: output/example3-config.json"
echo ""

# Example 4: YAML output format (template snippets)
echo "📦 Example 4: YAML template snippets..."
python main.py \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --requirements-file "examples/example-requirements.txt" \
  --output-format yaml \
  --output-file "output/example4-template.yml" \
  --verbose

echo "✅ Output saved to: output/example4-template.yml"
echo ""

# Example 5: Dry run mode (no Azure API calls)
echo "📦 Example 5: Dry run mode..."
python main.py \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --requirements-file "examples/example-requirements.txt" \
  --output-format cli \
  --dry-run \
  --verbose

echo "✅ Dry run completed"
echo ""

# Example 6: Full AI Foundry with all features
echo "🌊 Example 6: Full AI Foundry Hub with all features..."
python main.py \
  --hub-type ai-foundry \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --requirements-file "examples/example-requirements.txt" \
  --conda-env "examples/example-environment.yml" \
  --include-vscode \
  --include-huggingface \
  --include-prompt-flow \
  --custom-fqdns "internal-models.company.com,api.corp.com" \
  --output-format cli \
  --output-file "output/example6-full-ai-foundry.sh" \
  --include-transitive \
  --verbose

echo "✅ Output saved to: output/example6-full-ai-foundry.sh"
echo ""

echo "🎉 All examples completed!"
echo ""
echo "📁 Check the output/ directory for generated files:"
ls -la output/
echo ""
echo "💡 Next steps:"
echo "1. Review the generated Azure CLI commands"
echo "2. Test in a non-production environment first"
echo "3. Apply to your workspace after validation"
echo "4. Monitor package installations" 