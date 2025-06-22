# Azure AI/ML Package Allowlist & Connectivity Analysis Tool
# Multi-stage build for optimized image size
FROM python:3.12.7-slim AS base

# Set build arguments for better caching and flexibility
ARG DEBIAN_FRONTEND=noninteractive
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Install system dependencies in one layer with security updates
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    # Essential tools
    curl \
    wget \
    gnupg \
    lsb-release \
    ca-certificates \
    # Build dependencies
    build-essential \
    git \
    # Network utilities for connectivity analysis
    iputils-ping \
    net-tools \
    dnsutils \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /workspace

# Install Azure CLI with better error handling and architecture detection
RUN echo "Installing Azure CLI for platform: ${TARGETPLATFORM:-unknown}" && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    az --version || (echo "Azure CLI installation failed" && exit 1)

# Install Azure ML extension with retry logic
RUN for i in 1 2 3; do \
        az extension add --name ml --yes && break || \
        (echo "Attempt $i failed, retrying..." && sleep 5); \
    done && \
    az extension list --query "[?name=='ml'].version" -o table

# Install Python package managers
# Upgrade pip and install essential tools
RUN python -m pip install --no-cache-dir --upgrade \
    pip>=23.0 \
    setuptools>=65.0 \
    wheel>=0.37.0 \
    uv>=0.1.0

# Install conda (miniconda) with architecture detection and error handling
RUN ARCH=$(uname -m) && \
    echo "Detected architecture: $ARCH" && \
    if [ "$ARCH" = "x86_64" ]; then \
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    echo "Downloading miniconda from: $MINICONDA_URL" && \
    curl -fsSL $MINICONDA_URL -o miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda clean -afy && \
    /opt/conda/bin/conda --version

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with better caching and error handling
RUN echo "Installing Python dependencies..." && \
    pip install --no-cache-dir -r requirements.txt && \
    echo "Verifying core installations..." && \
    python -c "import azure.cli.core; print('Azure CLI Python SDK installed')" && \
    python -c "import azure.ai.ml; print('Azure ML SDK installed')" && \
    python -c "import click; print('Click installed')"

# Copy application code (done late for better caching)
COPY . .

# Create non-root user for security with proper permissions
RUN groupadd -r azureml && \
    useradd -r -g azureml -m -s /bin/bash azureml-user && \
    chown -R azureml-user:azureml /workspace && \
    chmod -R 755 /workspace

# Switch to non-root user
USER azureml-user

# Set environment variables for better Python behavior
ENV PYTHONPATH=/workspace
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV AZURE_CLI_DISABLE_CONNECTION_VERIFICATION=1

# Create directories for volume mounts with proper permissions
RUN mkdir -p /workspace/input /workspace/output /workspace/connectivity-reports && \
    chmod 755 /workspace/input /workspace/output /workspace/connectivity-reports

# Health check to verify the tool is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python main.py --help > /dev/null || exit 1

# Create volume mount points for user files and reports
VOLUME ["/workspace/input", "/workspace/output", "/workspace/connectivity-reports"]

# Default command shows help
CMD ["python", "main.py", "--help"]

# Enhanced metadata labels following best practices
LABEL org.opencontainers.image.title="Azure AI/ML Allowlist & Connectivity Tool"
LABEL org.opencontainers.image.description="Comprehensive tool for package allowlist generation and connectivity analysis for Azure AI Foundry Hubs and ML Workspaces"
LABEL org.opencontainers.image.version="2.1.0"
LABEL org.opencontainers.image.created="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
LABEL org.opencontainers.image.authors="Azure AI/ML Community"
LABEL org.opencontainers.image.url="https://github.com/enu235/AzureAIAllowList"
LABEL org.opencontainers.image.documentation="https://github.com/enu235/AzureAIAllowList/blob/main/README.md"
LABEL org.opencontainers.image.source="https://github.com/enu235/AzureAIAllowList"
LABEL features="package-allowlist,connectivity-analysis,azure-ml,azure-ai-foundry,network-analysis,security-assessment"
LABEL platforms="linux/amd64,linux/arm64"
LABEL azure.services="ai-foundry,machine-learning,virtual-network,storage,key-vault,container-registry" 