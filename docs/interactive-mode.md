# Interactive Mode Guide

**Version 1.0.0** | **Zero-Configuration Experience** 🚀

> **🚨 AS IS DISCLAIMER**: This tool is provided "AS IS" without warranty of any kind, express or implied. Always review and test configurations in non-production environments before applying to production systems.

## 🎯 Overview

Interactive Mode is the easiest way to use the Azure AI Foundry & ML Package Allowlist Tool. **No parameters required** - just run `python main.py` and the tool guides you through everything.

### ✨ What Interactive Mode Does

- 🔐 **Automatic Azure Authentication** - Detects login status and guides you through Azure CLI setup
- 📋 **Subscription Discovery** - Shows all available subscriptions in a beautiful table
- 🔍 **Workspace Auto-Discovery** - Finds all AI Foundry hubs and ML workspaces across resource groups
- 🎯 **Smart Analysis Selection** - Choose between standard analysis and workspace comparison
- 📦 **Package File Detection** - Automatically discovers package files in your current directory
- ⚙️ **Guided Configuration** - Step-by-step setup for AI Foundry features and custom options

---

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have the basic requirements:
```bash
# Check Python version (3.11+ required)
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Interactive Mode

```bash
# Simply run without any parameters
python main.py
```

**That's it!** 🎉 The interactive flow starts automatically when no workspace parameters are provided.

---

## 📋 Interactive Flow Walkthrough

### Step 1: Welcome & Disclaimer

```
╭──────────────────────────────────────────────── Welcome ─────────────────────────────────────────────────╮
│                                                                                                          │
│  🚀 Azure AI Foundry & ML Package Allowlist Tool                                                         │
│  Interactive Mode                                                                                        │
│                                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────────── Important Notice ────────────────────────────────────────────╮
│ ⚠️  DISCLAIMER: This tool is provided 'AS IS' without warranty. Review all recommendations before
│
│ implementation. Test in non-production environments first.                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**Purpose**: Clear introduction and important legal disclaimers.

### Step 2: Azure CLI Authentication Check

```
╭───────────────────────────────────╮
│ 🔐 Azure CLI Authentication Check │
╰───────────────────────────────────╯
```

**What Happens:**
- ✅ **Already logged in**: Shows current user and proceeds
- ❌ **Not logged in**: Automatically runs `az login` for you
- 🔧 **ML Extension Missing**: Automatically installs `az ml` extension

**Example Output:**
```
✅ Already logged in as: john.doe@company.com
✅ Azure ML extension is installed
```

**If Not Logged In:**
```
❌ Not logged in to Azure CLI
🔄 Starting Azure login process...
   Running: az login
   
✅ Successfully logged in as: john.doe@company.com
🔧 Installing Azure ML extension...
   Running: az extension add -n ml
   
✅ Azure ML extension installed successfully
```

### Step 3: Subscription Selection

```
╭─────────────────────────────────╮
│ 📋 Azure Subscription Selection │
╰─────────────────────────────────╯
                          Available Azure Subscriptions                           
┏━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ #   ┃ Subscription Name ┃ Subscription ID                          ┃ Status    ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1   │ Production        │ 12345678-1234-1234-1234-123456789012     │ CURRENT   │
│ 2   │ Development       │ 87654321-4321-4321-4321-210987654321     │ Available │
│ 3   │ Sandbox           │ 11111111-2222-3333-4444-555555555555     │ Available │
└─────┴───────────────────┴──────────────────────────────────────────┴───────────┘

? Select a subscription: 1. Production (12345678...) [CURRENT]
```

**Features:**
- 📊 **Rich Table Display** - Easy-to-read subscription information
- 🎯 **Current Subscription Highlighted** - Shows which subscription is currently active
- 🔄 **Automatic Context Switch** - Changes Azure CLI context to selected subscription

### Step 4: Analysis Type Selection

```
╭────────────────────────────╮
│ 📊 Analysis Type Selection │
╰────────────────────────────╯
? What type of analysis would you like to perform?
❯ 📋 Standard Analysis - Analyze one or more workspaces
  🔄 Comparison Analysis - Compare exactly 2 workspaces side-by-side
```

**Options:**

1. **📋 Standard Analysis**
   - Analyze 1 or more workspaces
   - Generate allowlist configurations
   - Comprehensive connectivity analysis
   - Best for: Regular configuration management

2. **🔄 Comparison Analysis**
   - Compare exactly 2 workspaces
   - Show differences in network configuration
   - Highlight security variations
   - Best for: Migration planning, security audits

### Step 5: Workspace Discovery

```
╭──────────────────────────────╮
│ 🔍 Azure Workspace Discovery │
╰──────────────────────────────╯
🔄 Discovering workspaces across all resource groups...

           Discovered Azure AI Foundry Hubs & ML Workspaces            
┏━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ #   ┃ Name         ┃ Type           ┃ Resource Group       ┃ Location        ┃
┡━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 1   │ ProductionAI │ 🔮 AI Foundry  │ production-rg        │ eastus          │
│ 2   │ DevWorkspace │ 🤖 Azure ML    │ development-rg       │ westus2         │
│ 3   │ TestingHub   │ 🔮 AI Foundry  │ testing-rg           │ centralus       │
│ 4   │ SandboxML    │ 🤖 Azure ML    │ sandbox-rg           │ westus          │
└─────┴──────────────┴────────────────┴──────────────────────┴─────────────────┘

╭───────────────────────────────────────────────── Legend ─────────────────────────────────────────────────╮
│ 🔮 Azure AI Foundry Hub  |  🤖 Azure ML Workspace                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**Features:**
- 🔍 **Automatic Discovery** - Scans all resource groups in the subscription
- 🎨 **Color-Coded Types** - Visual distinction between AI Foundry and Azure ML
- 📍 **Location Display** - Shows Azure region for each workspace
- 🏷️ **Clear Legend** - Easy identification of workspace types

**Selection Options:**

**For Standard Analysis:**
```
📋 Standard Analysis: Select one or more workspaces
? Select workspace(s) to analyze: 
 ❯ ◯ 1. 🔮 ProductionAI (AI Foundry) - eastus
   ◯ 2. 🤖 DevWorkspace (Azure ML) - westus2
   ◯ 3. 🔮 TestingHub (AI Foundry) - centralus
   ◯ 4. 🤖 SandboxML (Azure ML) - westus
```

**For Comparison Analysis:**
```
🔄 Comparison Analysis: Select exactly 2 workspaces
? Select the first workspace to compare: 1. 🔮 ProductionAI (AI Foundry) - eastus
? Select the second workspace to compare: 2. 🤖 DevWorkspace (Azure ML) - westus2
```

### Step 6: Package Analysis Configuration

```
╭───────────────────────────────────╮
│ 📦 Package Analysis Configuration │
╰───────────────────────────────────╯
? Would you like to include package analysis (allowlist generation)? Yes
✅ Package analysis enabled

🔍 Discovered package files in current directory:
   📄 /path/to/requirements.txt (pip)
   📄 /path/to/environment.yml (conda)
   📄 /path/to/pyproject.toml (poetry)

? Use the discovered package files above? Yes
```

**If No Package Files Found:**
```
⚠️  No package files found in current directory
? Would you like to specify package files manually? No
⚡ Continuing with connectivity analysis only...
```

**Package Discovery Options:**
```
? Include transitive dependencies? Yes
? Target platform: 
❯ 🔄 Auto-detect platform
  🐧 Linux
  🪟 Windows
```

### Step 7: AI Foundry Features (if applicable)

```
🔮 Azure AI Foundry Features:
? Include Visual Studio Code integration FQDNs? Yes
? Include HuggingFace model access FQDNs? Yes  
? Include Prompt Flow service FQDNs? Yes
? Add custom FQDNs (internal services, etc.)? No
```

**If Custom FQDNs Selected:**
```
? Enter custom FQDNs (comma-separated): internal-api.company.com, models.corp.local
✅ Added custom domains: internal-api.company.com, models.corp.local
```

### Step 8: Configuration Summary

```
╭─────────────────────────────────╮
│ 🎯 Analysis Configuration Ready │
╰─────────────────────────────────╯
📋 Subscription: Production
   ID: 12345678-1234-1234-1234-123456789012
📊 Analysis Type: Standard Analysis
🏢 Workspaces (2):
   🔮 ProductionAI (production-rg)
   🤖 DevWorkspace (development-rg)
📦 Package Analysis: Enabled
   Files: 3 package file(s)
   AI Features: VS Code, HuggingFace, Prompt Flow

🚀 Starting analysis...
```

### Step 9: Analysis Execution

**Real-time Progress Display:**
```
🔍 Analyzing: ProductionAI (ai-foundry)
[1/6] Validating prerequisites: Checking Azure CLI and permissions
[2/6] Connecting to workspace/hub: Connecting to ProductionAI
[3/6] Analyzing network configuration: Discovering network isolation and connectivity settings
[4/6] Discovering connected resources: Finding all resources connected to the workspace
[5/6] Analyzing security settings: Performing comprehensive security analysis
[6/6] Generating report: Creating comprehensive connectivity analysis report
✅ Connectivity analysis completed for ProductionAI

📦 Running package analysis for ProductionAI...
✅ Package analysis completed for ProductionAI

🔍 Analyzing: DevWorkspace (azure-ml)
[1/6] Validating prerequisites: Checking Azure CLI and permissions
[2/6] Connecting to workspace/hub: Connecting to DevWorkspace
[3/6] Analyzing network configuration: Discovering network isolation and connectivity settings
[4/6] Discovering connected resources: Finding all resources connected to the workspace
[5/6] Analyzing security settings: Performing comprehensive security analysis
[6/6] Generating report: Creating comprehensive connectivity analysis report
✅ Connectivity analysis completed for DevWorkspace

📦 Running package analysis for DevWorkspace...
✅ Package analysis completed for DevWorkspace
```

### Step 10: Results Summary

```
📊 Combined Analysis Summary (2 workspaces)
   • 🔮 ProductionAI (ai-foundry) - production-rg
   • 🤖 DevWorkspace (azure-ml) - development-rg

📈 Analysis Results:
   • Connectivity reports: 2 generated
   • Package allowlists: 2 generated
   • Total domains discovered: 47 unique
   • Security recommendations: 8 items

📄 Generated Reports:
   • connectivity-reports/ProductionAI_connectivity_20241228_143022.md
   • connectivity-reports/DevWorkspace_connectivity_20241228_143022.md
```

---

## 🎛️ Advanced Interactive Features

### Smart Error Handling

**Permission Issues:**
```
❌ Error: Access denied to resource group 'production-rg'
💡 Suggestions:
   • Check if you have Contributor or Reader access to the resource group
   • Verify your Azure subscription permissions
   • Contact your Azure administrator for access
? Would you like to try a different resource group? Yes
```

**Missing Dependencies:**
```
❌ Azure ML extension not found
🔄 Installing Azure ML extension automatically...
   Running: az extension add -n ml
✅ Azure ML extension installed successfully
```

### Validation & Confirmation

**Before Running Analysis:**
```
⚠️  You're about to analyze 2 workspaces with package analysis enabled.
   This will:
   • Connect to Azure resources
   • Analyze network configurations  
   • Generate configuration files
   • May take 2-5 minutes to complete

? Proceed with analysis? Yes
```

**Workspace Access Validation:**
```
🔍 Validating workspace access...
✅ ProductionAI: Access confirmed
❌ DevWorkspace: Access denied - insufficient permissions
? Continue with accessible workspaces only? Yes
```

---

## 🛠️ Troubleshooting Interactive Mode

### Common Issues

**1. Azure CLI Not Found**
```
❌ Azure CLI not found in PATH
💡 Please install Azure CLI:
   • Windows: Download from https://aka.ms/installazurecliwindows
   • macOS: brew install azure-cli
   • Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**2. No Workspaces Discovered**
```
⚠️  No Azure ML workspaces or AI Foundry hubs found
💡 Possible reasons:
   • No workspaces exist in this subscription
   • Insufficient permissions to list resources
   • Workspaces in different subscription
? Try a different subscription? Yes
```

**3. Package Files Not Found**
```
ℹ️  No package files found in current directory
💡 Supported files: requirements.txt, environment.yml, pyproject.toml, Pipfile
? Specify package files manually? No
⚡ Continuing with connectivity analysis only...
```

### Manual Override Options

**Force CLI Mode:**
```bash
# Skip interactive mode and use traditional CLI
python main.py --workspace-name "my-workspace" --resource-group "my-rg"
```

**Debug Mode:**
```bash
# Enable verbose logging in interactive mode
python main.py --verbose
```

---

## 🎯 Best Practices

### Before Running Interactive Mode

1. **Prepare Your Environment**
   ```bash
   # Ensure Azure CLI is logged in
   az login
   
   # Verify subscription access
   az account show
   
   # Check workspace permissions
   az ml workspace list
   ```

2. **Organize Package Files**
   - Place package files (requirements.txt, environment.yml) in current directory
   - Use descriptive names for better file discovery
   - Ensure files are valid and properly formatted

3. **Review Permissions**
   - Verify subscription access level
   - Ensure resource group permissions
   - Check workspace access rights

### During Interactive Sessions

1. **Read Each Step Carefully**
   - Review disclaimers and warnings
   - Understand what each analysis does
   - Choose appropriate analysis type for your needs

2. **Validate Selections**
   - Double-check workspace selections
   - Verify subscription context
   - Confirm package file choices

3. **Monitor Progress**
   - Watch for error messages
   - Note any warnings or recommendations
   - Be patient during analysis phases

### After Analysis

1. **Review Generated Reports**
   - Read connectivity analysis summaries
   - Examine package allowlist configurations
   - Check security recommendations

2. **Test in Non-Production**
   - Always test configurations in development environments first
   - Validate package installations work as expected
   - Verify network connectivity remains functional

3. **Document Changes**
   - Save generated CLI commands for future use
   - Document any custom configurations
   - Keep reports for compliance and auditing

---

## 📚 Related Documentation

- 📘 **[Package Discovery Guide](package-discovery.md)** - Understanding how package analysis works
- 📙 **[Connectivity Analysis Guide](connectivity-analysis.md)** - Deep dive into network analysis
- 📕 **[Azure AI Foundry Networking](ai-foundry-networking.md)** - AI Foundry specific configurations
- 🔧 **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

---

> **💡 TIP**: Interactive mode is perfect for first-time users and exploratory analysis. For automation and CI/CD pipelines, use the traditional CLI mode with specific parameters.

> **🚨 REMINDER**: This tool is provided "AS IS" without warranty. Always review and test configurations in non-production environments before applying to production systems. 