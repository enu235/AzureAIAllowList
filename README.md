# Azure AI Foundry & Machine Learning Package Tool

> **⚠️ DISCLAIMER**: This tool is provided "AS IS" without warranty of any kind, express or implied. You use this tool and implement its recommendations at your own risk. Always review and test configurations in non-production environments before applying to production systems.

[![Version](https://img.shields.io/badge/version-0.8.0-blue.svg)](https://github.com/yourusername/AzureAIAllowList)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🚀 What This Tool Does

Analyze Azure AI Foundry Hubs and Azure Machine Learning workspaces to generate comprehensive network allowlists and connectivity reports for secured environments. Get the FQDNs you need to configure firewalls, NSGs, and private endpoints.

### ✨ Key Features

- 🎯 **Interactive Mode**: Zero-configuration startup with guided analysis
- 🔍 **Auto-Discovery**: Automatically find workspaces in your subscriptions  
- 🔮 **Azure AI Foundry Support**: Full support for AI Foundry hubs with enhanced features
- 🤖 **Azure ML Support**: Complete Azure Machine Learning workspace analysis
- 📦 **Package Analysis**: Discover FQDNs from requirements.txt, environment.yml, and more
- 🔄 **Workspace Comparison**: Side-by-side analysis of two workspaces
- 📊 **Rich Reports**: Detailed connectivity analysis with security assessments

## 🎯 Quick Start

### Prerequisites

- **Python 3.8+** 
- **Azure CLI** with ML extension
- **Azure subscription** with access to AI Foundry or ML workspaces

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/enu235/AzureAIAllowList.git
   cd AzureAIAllowList
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Using venv
   python -m venv azureml-tool
   source azureml-tool/bin/activate  # Linux/Mac
   # azureml-tool\Scripts\activate  # Windows

   # OR using conda
   conda create -n azureml-tool python=3.9
   conda activate azureml-tool

   # OR using uv (if you have it)
   uv venv azureml-tool
   source azureml-tool/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Azure CLI** (if not already installed):
   ```bash
   # macOS
   brew install azure-cli
   
   # Ubuntu/Debian
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # Windows (PowerShell)
   winget install Microsoft.AzureCLI
   ```

5. **Install Azure ML extension**:
   ```bash
   az extension add --name ml
   ```

6. **Login to Azure**:
   ```bash
   az login
   ```

## 🎮 Interactive Mode (Recommended)

The easiest way to use the tool:

```bash
python main.py
```

The interactive mode will guide you through:

1. **🔐 Authentication**: Auto-detects Azure CLI login status
2. **📋 Subscription Selection**: Choose from available subscriptions
3. **🔍 Workspace Discovery**: Auto-discover workspaces with visual indicators:
   - 🔮 **Azure AI Foundry Hubs** (magenta)
   - 🤖 **Azure ML Workspaces** (green)
4. **🎯 Analysis Type**: Choose standard analysis or workspace comparison
5. **📦 Package Analysis**: Optionally include package dependency analysis

### Example Interactive Session

```
🚀 Azure AI Foundry & ML Package Allowlist Tool
Interactive Mode

🔐 Azure CLI Authentication Check
✅ Logged in as: user@company.com

📋 Available Subscriptions
┌─────────────────────────────────────┬──────────────────────────┐
│ Subscription Name                   │ Subscription ID          │
├─────────────────────────────────────┼──────────────────────────┤
│ Production Subscription             │ 12345678-1234-5678-...   │
│ Development Subscription            │ 87654321-4321-8765-...   │
└─────────────────────────────────────┴──────────────────────────┘

🔍 Available Workspaces
┌─────────────────────────┬─────────────────┬──────────────┬───────────┐
│ Name                    │ Type            │ Location     │ RG        │
├─────────────────────────┼─────────────────┼──────────────┼───────────┤
│ 🔮 ai-foundry-prod     │ AI Foundry Hub  │ East US      │ prod-rg   │
│ 🤖 ml-workspace-dev    │ Azure ML        │ West US 2    │ dev-rg    │
└─────────────────────────┴─────────────────┴──────────────┴───────────┘

? Select analysis type:
  ▸ Standard Analysis (1+ workspaces)
    Comparison Analysis (exactly 2 workspaces)

? Include package analysis? (Y/n): Y
? Package file path (optional): requirements.txt

🔄 Analyzing ai-foundry-prod...
✅ Analysis complete! Reports saved to connectivity-reports/
```

## ⚡ Command Line Mode

For automation and scripting:

### Basic Analysis

```bash
# Analyze a single workspace
python main.py \
  --workspace-name my-ai-foundry-hub \
  --resource-group my-rg \
  --subscription 12345678-1234-5678-9012-123456789012

# With package analysis  
python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --subscription 12345678-1234-5678-9012-123456789012 \
  --requirements-file requirements.txt
```

### Workspace Comparison

```bash
python main.py \
  --workspace-name prod-workspace \
  --resource-group prod-rg \
  --workspace-name-2 dev-workspace \
  --resource-group-2 dev-rg \
  --subscription 12345678-1234-5678-9012-123456789012 \
  --comparison-mode
```

### Advanced Options

```bash
# Bash/Linux Azure CLI commands (default)
python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --subscription 12345678-1234-5678-9012-123456789012 \
  --requirements-file requirements.txt \
  --environment-file environment.yml \
  --include-vscode \
  --include-huggingface \
  --output-format cli \
  --verbose

# PowerShell Azure CLI commands (Windows)
python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --subscription 12345678-1234-5678-9012-123456789012 \
  --requirements-file requirements.txt \
  --output-format powershell \
  --verbose
```

## 📊 What You Get

### Network Allowlist Report

- **Required FQDNs** for package repositories (PyPI, Conda, etc.)
- **Azure service endpoints** for ML/AI operations
- **Enhanced features** for AI Foundry (VS Code, HuggingFace, Prompt Flow)
- **Custom FQDNs** from your package dependencies

### Connectivity Analysis Report

- **Network configuration** details and security posture
- **Resource inventory** with security assessments
- **Mermaid diagrams** showing network relationships
- **Security recommendations** with actionable guidance
- **Compliance status** and risk assessment

### Example Output Structure

```
connectivity-reports/
├── my-workspace-connectivity-report.md
├── my-workspace-allowlist.json
├── my-workspace-security-summary.md
└── azure-firewall-rules.json
```

## 🔧 Configuration Options

### Package File Formats Supported

| Format | File | Description |
|--------|------|-------------|
| **pip** | `requirements.txt` | Standard Python packages |
| **conda** | `environment.yml` | Conda environment files |
| **poetry** | `pyproject.toml` | Poetry dependency management |
| **pipenv** | `Pipfile`/`Pipfile.lock` | Pipenv virtual environments |
| **setup** | `setup.py`/`setup.cfg` | Package setup files |

### AI Foundry Enhanced Features

When analyzing Azure AI Foundry hubs, additional FQDNs are included:

- **VS Code Integration**: `*.vscode-cdn.net`, `marketplace.visualstudio.com`
- **HuggingFace Models**: `*.huggingface.co`, `cdn-lfs.huggingface.co`  
- **Prompt Flow**: Additional GitHub and API endpoints
- **Enhanced Package Discovery**: AI/ML specific repositories

### Output Formats

| Format | Usage | Description |
|--------|-------|-------------|
| `cli` | Default | Bash/Linux commands for Azure CLI |
| `powershell` | Windows | PowerShell commands for Azure CLI |
| `json` | Automation | Machine-readable structured data |
| `yaml` | Configuration | YAML format for config files |

## 🛡️ Security Considerations

- **No credential storage**: All authentication handled by Azure CLI
- **Local processing**: No data sent to external services
- **Input validation**: Comprehensive validation of all inputs
- **Error handling**: No sensitive information exposed in error messages

## 🔄 Backward Compatibility

This tool maintains **100% backward compatibility** with existing scripts:

- All existing command-line parameters work unchanged
- Same output formats and file structures  
- No breaking changes to CLI interface
- Existing automation and CI/CD pipelines continue to work

## 🐳 Docker Support

For users who prefer containerized execution without installing local dependencies:

```bash
# Interactive mode with Docker
cd docker
docker-compose up

# Command line mode with Docker
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --output-format powershell
```

**Benefits:**
- Zero local dependencies (only Docker required)
- Pre-configured Python, Azure CLI, and all dependencies
- Reports output to local `connectivity-reports/` folder
- Uses your existing Azure CLI authentication

See **[Docker Documentation](docker/README.md)** for complete setup and usage guide.

## 📚 Documentation

- **[Interactive Mode Guide](docs/interactive-mode.md)** - Comprehensive guide to interactive features
- **[Analysis & Discovery Guide](docs/analysis-discovery.md)** - Detailed analysis capabilities
- **[Private Repositories](docs/private-repositories.md)** - Handling private package repositories
- **[Docker Usage Guide](docker/README.md)** - Containerized execution guide
- **[Contributing Guide](docs/contributing.md)** - How to contribute to this project

## 🚨 Common Issues

### Azure CLI Not Found

```bash
# Install Azure CLI first
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash  # Linux
brew install azure-cli  # macOS
winget install Microsoft.AzureCLI  # Windows

# Install ML extension
az extension add --name ml
```

### Authentication Issues

```bash
# Login to Azure
az login

# Set subscription (if multiple)
az account set --subscription "your-subscription-id"

# Verify access
az account show
```

### Permission Errors

Required Azure RBAC roles:
- **Azure AI Foundry**: `AzureML Data Scientist` role minimum
- **Azure ML**: `Machine Learning Workspace Contributor` role minimum  
- **Network Analysis**: `Reader` role on workspace and connected resources

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for details on:

- Code style and standards
- Testing requirements  
- Submitting pull requests
- Reporting issues

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Version History

**v0.8.0** - Major Interactive Enhancement
- ✨ Interactive mode with rich UI
- 🔍 Auto-discovery of workspaces
- 🔄 Workspace comparison analysis
- 🎨 Enhanced user experience
- 📚 Comprehensive documentation rewrite

---

> **Remember**: This tool is provided "AS IS" without warranty. Always test configurations in non-production environments before applying to production systems. 