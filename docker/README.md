# Docker Usage Guide - Azure AI Foundry & ML Package Tool

> **⚠️ DISCLAIMER**: This containerized version is provided "AS IS" without warranty of any kind, express or implied. Users should thoroughly test all functionality in non-production environments before deploying to production systems.

This guide covers running the Azure AI Foundry & Machine Learning Package Tool in a Docker container for users who prefer not to install Python, Azure CLI, and dependencies locally.

## 🎯 Overview

The Docker version provides:
- **Zero local dependencies**: Only Docker required on your system
- **Pre-configured environment**: Python 3.11, Azure CLI, and all dependencies included
- **Local output**: Reports generated in your local `connectivity-reports/` folder
- **Azure CLI integration**: Uses your existing Azure authentication
- **Package file access**: Reads `requirements.txt`, `environment.yml`, etc. from your current directory

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** installed ([Download here](https://docs.docker.com/get-docker/))
- **Azure CLI authentication** configured on your host machine (`az login`)

### Basic Usage

1. **Navigate to project directory**:
   ```bash
   cd /path/to/AzureAIAllowList
   ```

2. **Run interactive mode**:
   ```bash
   # From the docker/ directory
   cd docker
   docker-compose up
   ```

3. **View results**: Reports will be generated in `../connectivity-reports/`

## 📋 Detailed Usage

### Interactive Mode (Recommended)

The easiest way to use the containerized tool:

```bash
cd docker
docker-compose up
```

**What happens:**
- Container builds automatically (first run only)
- Tool starts in interactive mode
- Guides you through Azure authentication check
- Auto-discovers workspaces in your subscriptions
- Generates reports in local `connectivity-reports/` folder

### Command Line Mode

For automation and scripting:

```bash
cd docker
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --subscription 12345678-1234-5678-9012-123456789012
```

### Package Analysis with Docker

```bash
# Ensure your package files are in the project root
ls ../requirements.txt  # Should exist

cd docker
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --requirements-file input/requirements.txt \
  --output-format powershell
```

## 🔧 Configuration Options

### Build the Container

If you make changes to the tool or want to rebuild:

```bash
cd docker
docker-compose build
```

### Run Different Output Formats

```bash
# Generate PowerShell commands (new!)
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --output-format powershell

# Generate JSON output
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --output-format json

# Generate YAML output  
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --output-format yaml
```

### Workspace Comparison in Docker

```bash
# Compare two workspaces
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name prod-workspace \
  --resource-group prod-rg \
  --workspace-name-2 dev-workspace \
  --resource-group-2 dev-rg \
  --comparison-mode
```

## 📁 File Structure & Volumes

The Docker setup mounts the following directories:

```
Host Machine                    →    Container
├── connectivity-reports/      →    /app/connectivity-reports (read/write)
├── requirements.txt           →    /app/input/requirements.txt (read-only)
├── environment.yml            →    /app/input/environment.yml (read-only)
├── pyproject.toml             →    /app/input/pyproject.toml (read-only)
├── ~/.azure/                  →    /root/.azure (read-only)
└── [project root]             →    /app/input (read-only)
```

### Output Files

All reports are saved to your local `connectivity-reports/` directory:

```
connectivity-reports/
├── workspace-connectivity-report.md     # Detailed analysis
├── workspace-allowlist.json            # Network allowlist
├── workspace-azure-cli-commands.sh     # Bash commands
├── workspace-azure-cli-commands.ps1    # PowerShell commands (new!)
└── workspace-security-summary.md       # Security assessment
```

## 🔒 Authentication

### Azure CLI Authentication

The container uses your host machine's Azure CLI authentication:

1. **Login on host** (if not already done):
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   ```

2. **Verify authentication**:
   ```bash
   az account show
   ```

3. **Run container**: Authentication is automatically shared

### Troubleshooting Authentication

If you encounter authentication issues:

```bash
# Check if ~/.azure directory exists and has content
ls -la ~/.azure/

# Re-login if needed
az login --use-device-code

# Verify ML extension is installed
az extension add --name ml
```

## 🎯 Common Use Cases

### 1. Quick Package Analysis

```bash
# Place your requirements.txt in project root
cd docker
docker-compose up
# Follow interactive prompts
```

### 2. Automated CI/CD Integration

```bash
#!/bin/bash
# ci-analysis.sh
cd docker
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name "$WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --subscription "$SUBSCRIPTION_ID" \
  --requirements-file input/requirements.txt \
  --output-format json \
  --output-file connectivity-reports/allowlist-output.json
```

### 3. Windows PowerShell Users

```bash
# Generate PowerShell commands instead of bash
cd docker
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name my-workspace \
  --resource-group my-rg \
  --output-format powershell \
  --output-file connectivity-reports/azure-commands.ps1
```

### 4. Multi-Environment Analysis

```bash
# Analyze production environment
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name prod-workspace \
  --resource-group prod-rg \
  --subscription "$PROD_SUBSCRIPTION" \
  --output-file connectivity-reports/prod-analysis.json

# Analyze development environment
docker-compose run azure-ai-allowlist-cli python main.py \
  --workspace-name dev-workspace \
  --resource-group dev-rg \
  --subscription "$DEV_SUBSCRIPTION" \
  --output-file connectivity-reports/dev-analysis.json
```

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check Docker daemon is running
docker version

# Check for port conflicts
docker-compose down
docker-compose up
```

### Azure CLI Issues

```bash
# Verify Azure CLI works in container
docker-compose run azure-ai-allowlist-cli az account show

# Check extension installation
docker-compose run azure-ai-allowlist-cli az extension list --query "[?name=='ml']"
```

### Volume Mount Issues

```bash
# Verify directory structure
ls -la ../connectivity-reports/
ls -la ../requirements.txt

# Check Docker permissions (Linux/Mac)
sudo chown -R $USER:$USER ../connectivity-reports/
```

### Package File Not Found

```bash
# Ensure package files are in project root, not docker/ directory
cd ..  # Go to project root
ls requirements.txt environment.yml  # Should exist here

# Run from docker/ directory
cd docker
docker-compose run azure-ai-allowlist-cli python main.py \
  --requirements-file input/requirements.txt
```

## 🔧 Advanced Configuration

### Custom Azure CLI Configuration

If you need to use different Azure CLI configuration:

```yaml
# In docker-compose.yml, modify the volumes section:
volumes:
  - /path/to/custom/azure/config:/root/.azure:ro
```

### Development Mode

For developing the tool itself:

```yaml
# Add to docker-compose.yml volumes:
volumes:
  - ../src:/app/src:ro  # Mount source code for development
```

### Resource Limits

For large analyses, you might want to increase container resources:

```yaml
# Add to docker-compose.yml service:
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

## 📊 Performance Notes

- **First run**: Container build takes 2-3 minutes
- **Subsequent runs**: Start in seconds
- **Analysis time**: Same as local execution
- **Output generation**: Reports written directly to host filesystem

## 🔄 Updates

To update to the latest version:

```bash
# Rebuild container with latest changes
cd docker
docker-compose build --no-cache

# Or pull latest code and rebuild
git pull origin main
docker-compose build
```

## 💡 Tips & Best Practices

1. **Keep package files in project root**: `requirements.txt`, `environment.yml`, etc.
2. **Use descriptive output filenames**: Specify `--output-file` for multiple analyses
3. **Check reports locally**: All output goes to your local `connectivity-reports/` folder
4. **PowerShell users**: Use `--output-format powershell` for Windows-compatible commands
5. **CI/CD integration**: Use the `azure-ai-allowlist-cli` service for automated runs

---

> **Note**: This containerized version provides the same functionality as the local installation while eliminating the need to install dependencies on your host machine. Perfect for team environments where standardization is important.

**Container Version**: 0.8.0  
**Base Image**: python:3.11-slim  
**Included**: Python 3.11, Azure CLI, ML Extension, All Dependencies 