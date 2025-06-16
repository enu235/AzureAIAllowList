# Azure ML Package URL Allowlist Tool
FROM python:3.12-slim

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install Azure ML extension
RUN az extension add --name ml

# Install Python package managers
# pip is already included with Python
# Install conda (miniconda) - automatically detect architecture
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    curl -sL $MINICONDA_URL -o miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda clean -a

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Install uv (fast Python package installer)
RUN pip install uv

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -s /bin/bash azureml-user && \
    chown -R azureml-user:azureml-user /workspace

USER azureml-user

# Set environment variables
ENV PYTHONPATH=/workspace
ENV PYTHONUNBUFFERED=1

# Create volume mount point for user files
VOLUME ["/workspace/input", "/workspace/output"]

# Default command
CMD ["python", "main.py", "--help"]

# Labels for metadata
LABEL maintainer="Azure ML Package URL Allowlist Tool"
LABEL description="Tool to discover package URLs and configure Azure ML workspace outbound rules"
LABEL version="1.0.0" 