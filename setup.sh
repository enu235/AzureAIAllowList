#!/bin/bash

# Azure ML Package URL Allowlist Tool - Setup Script
# This script helps set up the development environment

set -e

echo "🚀 Setting up Azure ML Package URL Allowlist Tool"
echo "================================================="
echo ""

# Create output and input directories
echo "📁 Creating directories..."
mkdir -p output
mkdir -p input
mkdir -p logs

echo "✅ Directories created"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
if ! command -v python3.12 &> /dev/null; then
    echo "⚠️  Python 3.12 not found. This tool requires Python 3.12+"
    echo "   You can continue with your current Python version, but some features may not work optimally."
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
        az extension add --name ml
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
    echo "  az extension add --name ml"
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

# Test the tool
echo "🧪 Testing the tool..."
python main.py --help
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source azureml-package-tool/bin/activate"
echo "2. Configure Azure CLI: az login"
echo "3. Set your subscription: az account set --subscription \"your-subscription-id\""
echo "4. Run examples: ./examples/run-examples.sh"
echo ""
echo "Quick start:"
echo "python main.py --workspace-name \"your-workspace\" --resource-group \"your-rg\" --requirements-file \"examples/example-requirements.txt\""
echo ""
echo "For Docker usage:"
echo "docker build -t azureml-package-tool ."
echo "docker-compose up azureml-package-tool-interactive" 