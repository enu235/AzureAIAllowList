# Migration Guide: Using Connectivity Analysis

## Overview

This guide helps existing users of the Azure AI/ML Package Allowlist tool adopt the new connectivity analysis features.

## What's New?

The connectivity analysis feature is a **non-breaking addition** that:
- Maintains all existing functionality
- Adds new `--action` parameter
- Provides comprehensive network analysis
- Generates detailed security reports

## Migration Steps

### 1. Update Your Scripts

#### Before (Existing Usage)
```bash
python main.py \
  --hub-type azure-ml \
  --workspace-name my-workspace \
  --resource-group my-rg
```

#### After (With Explicit Action)
```bash
# For package allowlist (default behavior unchanged)
python main.py \
  --hub-type azure-ml \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --action package-allowlist

# For connectivity analysis
python main.py \
  --hub-type azure-ml \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --action analyze-connectivity
```

### 2. Update CI/CD Pipelines

#### Azure DevOps Pipeline
```yaml
- task: PythonScript@0
  displayName: 'Run Connectivity Analysis'
  inputs:
    scriptSource: 'filePath'
    scriptPath: 'main.py'
    arguments: '--hub-type $(HUB_TYPE) --workspace-name $(WORKSPACE_NAME) --resource-group $(RESOURCE_GROUP) --action analyze-connectivity'
```

#### GitHub Actions
```yaml
- name: Run Connectivity Analysis
  run: |
    python main.py \
      --hub-type ${{ env.HUB_TYPE }} \
      --workspace-name ${{ env.WORKSPACE_NAME }} \
      --resource-group ${{ env.RESOURCE_GROUP }} \
      --action analyze-connectivity
```

### 3. Handling Output

The new analysis creates reports in the `connectivity-reports/` directory:

```bash
# Archive reports in CI/CD
- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: 'connectivity-reports'
    artifactName: 'connectivity-analysis-reports'
```

## Backward Compatibility

### Default Behavior Unchanged
- Running without `--action` performs package allowlist (existing behavior)
- All existing parameters work as before
- Output format for package allowlist remains the same

### New Features Are Opt-In
- Connectivity analysis requires explicit `--action analyze-connectivity`
- New reports are saved to separate directory
- No changes to existing output locations

## Recommended Adoption Strategy

### Phase 1: Testing
1. Run connectivity analysis in non-production first
2. Review generated reports
3. Validate findings against known configuration

### Phase 2: Integration
1. Add connectivity analysis to existing automation
2. Run both actions in sequence if needed:
   ```bash
   # Run package allowlist
   python main.py --hub-type azure-ml --workspace-name my-ws --resource-group my-rg
   
   # Run connectivity analysis
   python main.py --hub-type azure-ml --workspace-name my-ws --resource-group my-rg --action analyze-connectivity
   ```

### Phase 3: Monitoring
1. Schedule regular connectivity analyses
2. Compare reports over time
3. Set up alerts for security score changes

## Feature Comparison

| Feature | Package Allowlist | Connectivity Analysis |
|---------|------------------|----------------------|
| Network testing | ✅ | ✅ |
| Package discovery | ✅ | ❌ |
| Resource discovery | ❌ | ✅ |
| Security scoring | ❌ | ✅ |
| Visual diagrams | ❌ | ✅ |
| JSON output | ✅ | ✅ |
| Markdown reports | ❌ | ✅ |

## Example Migration Scenarios

### Scenario 1: Security Team Integration

**Before**: Manual security reviews of workspace configurations
```bash
# Manual process: Review Azure portal, export configurations
```

**After**: Automated security analysis with reports
```bash
# Automated connectivity analysis
python main.py \
  --hub-type azure-ai-foundry \
  --workspace-name prod-hub \
  --resource-group prod-rg \
  --action analyze-connectivity

# Generate security summary for team
python -c "
from src.connectivity.summary_generator import SummaryGenerator
generator = SummaryGenerator()
# Custom reporting logic here
"
```

### Scenario 2: DevOps Pipeline Enhancement

**Before**: Basic package allowlist generation
```yaml
# .azure-pipelines.yml
- script: |
    python main.py \
      --workspace-name $(WORKSPACE_NAME) \
      --resource-group $(RESOURCE_GROUP) \
      --requirements-file requirements.txt
  displayName: 'Generate Package Allowlist'
```

**After**: Comprehensive analysis and reporting
```yaml
# .azure-pipelines.yml
- script: |
    # Generate package allowlist
    python main.py \
      --workspace-name $(WORKSPACE_NAME) \
      --resource-group $(RESOURCE_GROUP) \
      --requirements-file requirements.txt
    
    # Run connectivity analysis
    python main.py \
      --workspace-name $(WORKSPACE_NAME) \
      --resource-group $(RESOURCE_GROUP) \
      --action analyze-connectivity
  displayName: 'Complete Workspace Analysis'

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: 'connectivity-reports'
    artifactName: 'connectivity-reports'
  displayName: 'Publish Connectivity Reports'
```

### Scenario 3: Enterprise Compliance

**Before**: Manual compliance documentation
```bash
# Manual documentation process
# Export workspace configurations
# Create compliance reports manually
```

**After**: Automated compliance reporting
```bash
#!/bin/bash
# compliance-check.sh

WORKSPACES=("prod-hub" "staging-hub" "dev-hub")
RESOURCE_GROUP="enterprise-rg"

for workspace in "${WORKSPACES[@]}"; do
    echo "Analyzing $workspace..."
    python main.py \
      --hub-type azure-ai-foundry \
      --workspace-name "$workspace" \
      --resource-group "$RESOURCE_GROUP" \
      --action analyze-connectivity
done

echo "Compliance reports generated in connectivity-reports/"
```

## Environment Variables

Support for environment variables makes migration easier:

```bash
# Set common variables
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP="your-rg"
export AZURE_HUB_TYPE="azure-ai-foundry"

# Run analysis without repeating parameters
python main.py \
  --workspace-name my-workspace \
  --action analyze-connectivity
```

## Integration with Existing Tools

### PowerShell Integration
```powershell
# PowerShell wrapper for existing tools
function Invoke-WorkspaceAnalysis {
    param(
        [string]$WorkspaceName,
        [string]$ResourceGroup,
        [string]$Action = "package-allowlist"
    )
    
    python main.py `
        --workspace-name $WorkspaceName `
        --resource-group $ResourceGroup `
        --action $Action
}

# Usage
Invoke-WorkspaceAnalysis -WorkspaceName "my-workspace" -ResourceGroup "my-rg" -Action "analyze-connectivity"
```

### Terraform Integration
```hcl
# terraform/outputs.tf
resource "null_resource" "connectivity_analysis" {
  triggers = {
    workspace_id = azurerm_machine_learning_workspace.example.id
  }
  
  provisioner "local-exec" {
    command = <<EOF
      python main.py \
        --workspace-name ${azurerm_machine_learning_workspace.example.name} \
        --resource-group ${azurerm_resource_group.example.name} \
        --action analyze-connectivity
    EOF
  }
}
```

## Common Migration Issues

### Issue 1: Path Changes
**Problem**: Scripts assume specific output paths
**Solution**: Update paths to include `connectivity-reports/` directory

### Issue 2: JSON Format Differences
**Problem**: Different JSON schema between package allowlist and connectivity analysis
**Solution**: Use appropriate parsers for each output type

### Issue 3: CI/CD Integration
**Problem**: Build artifacts need updating
**Solution**: Include `connectivity-reports/` in artifact collections

## Testing Your Migration

### 1. Validate Existing Functionality
```bash
# Test that package allowlist still works
python main.py \
  --workspace-name test-workspace \
  --resource-group test-rg \
  --requirements-file test-requirements.txt
```

### 2. Test New Connectivity Analysis
```bash
# Test connectivity analysis
python main.py \
  --workspace-name test-workspace \
  --resource-group test-rg \
  --action analyze-connectivity
```

### 3. Verify Output Formats
```bash
# Check generated files
ls -la connectivity-reports/
cat connectivity-reports/*.json | jq '.'
```

## Getting Help

- Review the [Connectivity Analysis Guide](connectivity-analysis.md)
- Check [Troubleshooting](troubleshooting.md#connectivity-analysis-issues)
- Submit issues on GitHub with migration-specific tags

## Migration Checklist

- [ ] Test connectivity analysis in development environment
- [ ] Update CI/CD pipelines to include new action
- [ ] Update documentation and runbooks
- [ ] Train team on new report formats
- [ ] Set up artifact collection for reports
- [ ] Schedule regular connectivity analyses
- [ ] Review and act on security recommendations
- [ ] Integrate reports with existing security workflows

## Support

For migration-specific questions:
1. Check this guide for common scenarios
2. Review existing issues in the GitHub repository
3. Create new issues with `migration` label
4. Include your specific use case and configuration

The migration to connectivity analysis provides significant security and operational benefits while maintaining full backward compatibility with existing workflows. 