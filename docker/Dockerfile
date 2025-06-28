# Azure AI Foundry & Machine Learning Package Tool
# Containerized version for users who prefer not to install dependencies locally

FROM python:3.11-slim

# Set metadata
LABEL maintainer="Azure AI/ML Community"
LABEL description="Azure AI Foundry & Machine Learning Package Allowlist Tool"
LABEL version="0.8.0"

# Set environment variables for better Python behavior
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies required for Azure CLI and the tool
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    lsb-release \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install Azure ML extension
RUN az extension add --name ml --yes

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r azureuser && \
    useradd -r -g azureuser -m -s /bin/bash azureuser && \
    chown -R azureuser:azureuser /app

# Switch to non-root user
USER azureuser

# Create volume mount points for reports
RUN mkdir -p /app/connectivity-reports

# Health check to verify the tool is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python main.py --help > /dev/null || exit 1

# Default command shows help, but can be overridden
CMD ["python", "main.py", "--help"] 