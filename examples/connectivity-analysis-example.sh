#!/bin/bash
# Example: Connectivity Analysis for Azure AI Foundry Hub

# Set variables
WORKSPACE_NAME="${WORKSPACE_NAME:-my-ai-foundry-hub}"
RESOURCE_GROUP="${RESOURCE_GROUP:-my-resource-group}"
SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-00000000-0000-0000-0000-000000000000}"

echo "🔍 Starting connectivity analysis for Azure AI Foundry Hub: $WORKSPACE_NAME"
echo "=============================================================================="

# Run connectivity analysis
python main.py \
  --hub-type ai-foundry \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription-id "$SUBSCRIPTION_ID" \
  --action analyze-connectivity \
  --verbose

# Check if report was generated
REPORT_DIR="connectivity-reports"
if [ -d "$REPORT_DIR" ]; then
    echo ""
    echo "📄 Reports generated in $REPORT_DIR:"
    # List the most recent 5 reports
    ls -la "$REPORT_DIR"/*.md 2>/dev/null | tail -5
    
    # Open the latest report (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        LATEST_REPORT=$(ls -t "$REPORT_DIR"/*.md 2>/dev/null | head -1)
        if [ -f "$LATEST_REPORT" ]; then
            echo ""
            echo "📖 Opening latest report: $LATEST_REPORT"
            open "$LATEST_REPORT"
        fi
    fi
    
    # Show report summary
    LATEST_JSON=$(ls -t "$REPORT_DIR"/*.json 2>/dev/null | head -1)
    if [ -f "$LATEST_JSON" ]; then
        echo ""
        echo "📊 Analysis Summary:"
        echo "==================="
        
        # Extract key metrics using jq if available
        if command -v jq >/dev/null 2>&1; then
            echo "Total Resources: $(cat "$LATEST_JSON" | jq -r '.connected_resources.total_resources // "N/A"')"
            echo "Security Score: $(cat "$LATEST_JSON" | jq -r '.connected_resources.security_summary.average_security_score // "N/A"')/100"
            echo "Network Type: $(cat "$LATEST_JSON" | jq -r '.network_configuration.configuration_type // "N/A"')"
            
            # Count private endpoints
            PE_COUNT=$(cat "$LATEST_JSON" | jq -r '[.connected_resources.resources[] | select(.has_private_endpoint == true)] | length')
            TOTAL_COUNT=$(cat "$LATEST_JSON" | jq -r '.connected_resources.resources | length')
            echo "Private Endpoints: $PE_COUNT/$TOTAL_COUNT resources"
        else
            echo "Install 'jq' for detailed JSON analysis"
            echo "Report saved to: $LATEST_JSON"
        fi
    fi
else
    echo "❌ No reports directory found. Check for errors above."
fi

echo ""
echo "✅ Connectivity analysis complete!"
echo ""
echo "Next steps:"
echo "• Review the generated report for security recommendations"
echo "• Share the report with your security team"
echo "• Implement suggested improvements"
echo "• Schedule regular analysis runs" 