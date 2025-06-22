#!/bin/bash

# Azure AI Foundry & Machine Learning Allowlist & Connectivity Analysis Tool - Setup Script
# This script helps set up the development environment for the enhanced tool

set -e

echo "🚀 Setting up Azure AI Foundry & ML Allowlist & Connectivity Analysis Tool"
echo "============================================================================"
echo ""

# Create output and input directories
echo "📁 Creating directories..."
mkdir -p output
mkdir -p input
mkdir -p logs
mkdir -p connectivity-reports

echo "✅ Directories created"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
if ! command -v python3.12 &> /dev/null; then
    echo "⚠️  Python 3.12 not found. This tool requires Python 3.12+"
    echo "   You can continue with your current Python version, but some features may not work optimally."
    echo "   For optimal performance, especially for connectivity analysis, use Python 3.12+"
fi
echo ""

# Create virtual environment
echo "🔧 Setting up virtual environment..."
if [[ -d "azureml-package-tool" ]]; then
    echo "Virtual environment already exists"
else
    python3 -m venv azureml-package-tool
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source azureml-package-tool/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Check Azure CLI
echo "☁️  Checking Azure CLI..."
if command -v az &> /dev/null; then
    echo "✅ Azure CLI found: $(az --version | head -1)"
    
    # Check ML extension
    if az extension list | grep -q '"name": "ml"'; then
        echo "✅ Azure ML extension found"
    else
        echo "⚠️  Azure ML extension not found. Installing..."
        az extension add --name ml --yes
        echo "✅ Azure ML extension installed"
    fi
else
    echo "❌ Azure CLI not found!"
    echo ""
    echo "Please install Azure CLI:"
    echo "  macOS: brew install azure-cli"
    echo "  Ubuntu/Debian: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    echo "  Windows: https://aka.ms/installazurecliwindows"
    echo ""
    echo "After installing Azure CLI, run:"
    echo "  az extension add --name ml --yes"
    echo "  az login"
fi
echo ""

# Check package managers
echo "📋 Checking package managers..."
if command -v pip &> /dev/null; then
    echo "✅ pip: $(pip --version)"
fi

if command -v conda &> /dev/null; then
    echo "✅ conda: $(conda --version)"
fi

if command -v uv &> /dev/null; then
    echo "✅ uv: $(uv --version)"
else
    echo "⚠️  uv not found. Installing uv for faster package operations..."
    pip install uv
    echo "✅ uv installed"
fi

if command -v poetry &> /dev/null; then
    echo "✅ poetry: $(poetry --version)"
else
    echo "ℹ️  poetry not found (optional)"
fi
echo ""

# Check Docker for containerized usage
echo "🐳 Checking Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker found: $(docker --version)"
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose found: $(docker-compose --version)"
    else
        echo "⚠️  Docker Compose not found (optional for containerized usage)"
    fi
else
    echo "ℹ️  Docker not found (optional for containerized usage)"
fi
echo ""

# Test the tool
echo "🧪 Testing the tool..."
python main.py --help
echo ""

echo "🎉 Setup complete!"
echo ""
echo "========================================="
echo "🔮 AZURE AI FOUNDRY & ML ANALYSIS TOOL"
echo "========================================="
echo ""
echo "This tool supports two main actions:"
echo "1. 📦 Package Allowlist Generation"
echo "2. 🔍 Connectivity Analysis"
echo ""
echo "Hub Types Supported:"
echo "• Azure AI Foundry Hub (recommended)"
echo "• Azure Machine Learning Workspace"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source azureml-package-tool/bin/activate"
echo "2. Configure Azure CLI: az login"
echo "3. Set your subscription: az account set --subscription \"your-subscription-id\""
echo "4. Run examples: ./examples/run-examples.sh"
echo ""
echo "Quick start examples:"
echo ""
echo "📦 Package Allowlist Generation:"
echo "python main.py \\"
echo "  --action package-allowlist \\"
echo "  --hub-type ai-foundry \\"
echo "  --workspace-name \"your-workspace\" \\"
echo "  --resource-group \"your-rg\" \\"
echo "  --requirements-file \"examples/example-requirements.txt\""
echo ""
echo "🔍 Connectivity Analysis:"
echo "python main.py \\"
echo "  --action analyze-connectivity \\"
echo "  --hub-type ai-foundry \\"
echo "  --workspace-name \"your-workspace\" \\"
echo "  --resource-group \"your-rg\""
echo ""
echo "🐳 Docker usage:"
echo "docker build -t azure-ai-allowlist-tool ."
echo "docker-compose up azure-ai-allowlist-tool"
echo ""
echo "📚 For more examples and advanced usage:"
echo "• Check the examples/ directory"
echo "• Read the documentation in docs/"
echo "• Run: python main.py --help"
echo ""
echo "🚨 Remember to review the disclaimer when using this tool!" 