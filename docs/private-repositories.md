# Private Repository Handling Guide

This guide explains how to handle private package repositories when configuring Azure Machine Learning workspace outbound rules.

## Table of Contents

- [Overview](#overview)
- [Detection of Private Repositories](#detection-of-private-repositories)
- [Azure Storage Approach](#azure-storage-approach)
- [Azure Container Registry](#azure-container-registry)
- [Azure Artifacts](#azure-artifacts)
- [Private Endpoints](#private-endpoints)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

Private repositories cannot be directly added to Azure ML outbound rules because they typically require authentication and may not be publicly accessible. This guide provides several approaches to handle private packages in secured Azure ML environments.

## Detection of Private Repositories

The tool automatically detects private repositories based on common patterns:

### Private Repository Indicators

- **Localhost/Internal IPs**: `localhost`, `127.0.0.1`, `10.x.x.x`, `172.x.x.x`, `192.168.x.x`
- **Corporate domains**: `internal`, `corp`, `company`, `private`
- **Private hosting**: `artifactory`, `nexus`, `intranet`
- **Non-standard ports**: Custom ports other than 80/443
- **Unknown domains**: Domains not in the public repository allow list

### Example Private Repository URLs

```text
# Internal corporate repositories
https://artifactory.company.com/pypi/simple/
https://nexus.internal.corp/repository/pypi-proxy/simple/
https://packages.company.internal/simple/

# Private network addresses
https://10.0.1.100:8080/pypi/simple/
https://192.168.1.50/packages/
https://internal-pypi.local/simple/
```

## Azure Storage Approach

Upload private packages to Azure Blob Storage and install directly from blob URLs.

### Step 1: Upload Packages to Blob Storage

```bash
# Create storage container for packages
az storage container create \
  --name packages \
  --account-name yourstorageaccount \
  --public-access off

# Upload wheel files
az storage blob upload \
  --file your-private-package-1.0.0-py3-none-any.whl \
  --container packages \
  --name packages/your-private-package-1.0.0-py3-none-any.whl \
  --account-name yourstorageaccount
```

### Step 2: Configure Workspace Storage Access

Add storage account to workspace outbound rules:

```yaml
outbound_rules:
  - name: private-package-storage
    type: private_endpoint
    destination:
      service_resource_id: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage}
      subresource_target: blob
```

### Step 3: Install Packages

```python
# In your training script or environment
pip install https://yourstorageaccount.blob.core.windows.net/packages/your-private-package-1.0.0-py3-none-any.whl
```

### Step 4: Automate with Requirements File

Create a requirements.txt with blob URLs:

```text
# requirements.txt
numpy==1.21.0
https://yourstorageaccount.blob.core.windows.net/packages/your-private-package-1.0.0-py3-none-any.whl
pandas>=1.3.0
```

## Azure Container Registry

Pre-install private packages in custom Docker images.

### Step 1: Create Custom Docker Image

```dockerfile
# Dockerfile
FROM mcr.microsoft.com/azureml/base:latest

# Copy private packages
COPY private-packages/ /tmp/private-packages/

# Install private packages
RUN pip install /tmp/private-packages/*.whl

# Clean up
RUN rm -rf /tmp/private-packages/

# Install additional requirements
COPY requirements.txt .
RUN pip install -r requirements.txt
```

### Step 2: Build and Push to ACR

```bash
# Build image
docker build -t your-custom-ml-image .

# Tag for ACR
docker tag your-custom-ml-image youracr.azurecr.io/custom-ml-image:latest

# Push to ACR
docker push youracr.azurecr.io/custom-ml-image:latest
```

### Step 3: Configure Environment

```yaml
# environment.yml
name: custom-env
docker:
  image: youracr.azurecr.io/custom-ml-image:latest
```

### Step 4: Configure ACR Access

Add ACR to workspace outbound rules:

```yaml
outbound_rules:
  - name: private-container-registry
    type: private_endpoint
    destination:
      service_resource_id: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ContainerRegistry/registries/{acr}
      subresource_target: registry
```

## Azure Artifacts

Use Azure DevOps Artifacts as a private Python feed.

### Step 1: Create Artifacts Feed

```bash
# Create feed in Azure DevOps
az artifacts universal publish \
  --organization https://dev.azure.com/yourorg \
  --project yourproject \
  --scope project \
  --feed yourfeed \
  --name your-package \
  --version 1.0.0 \
  --path ./dist/
```

### Step 2: Configure Feed Access

```bash
# Generate personal access token (PAT)
# Configure pip to use Azure Artifacts

# Create pip.conf or pip.ini
[global]
extra-index-url = https://pkgs.dev.azure.com/yourorg/yourproject/_packaging/yourfeed/pypi/simple/
```

### Step 3: Add Artifacts Domain

Add Azure DevOps domains to workspace outbound rules:

```yaml
outbound_rules:
  - name: azure-artifacts
    type: fqdn
    destination: "*.dev.azure.com"
  - name: azure-artifacts-packages
    type: fqdn
    destination: "pkgs.dev.azure.com"
```

### Step 4: Authentication in Environment

```python
# Use managed identity or service principal for authentication
import os
from azure.identity import DefaultAzureCredential

# Configure authentication for Azure Artifacts
credential = DefaultAzureCredential()
token = credential.get_token("https://packaging.visualstudio.com/.default")

# Set environment variable for pip authentication
os.environ["PIP_EXTRA_INDEX_URL"] = f"https://pkgs.dev.azure.com/yourorg/yourproject/_packaging/yourfeed/pypi/simple/"
```

## Private Endpoints

Create private endpoints for your private repositories if they support it.

### Step 1: Create Private Endpoint

```bash
# Create private endpoint for your private service
az network private-endpoint create \
  --name private-repo-endpoint \
  --resource-group your-rg \
  --vnet-name your-vnet \
  --subnet your-subnet \
  --connection-name private-repo-connection \
  --private-connection-resource-id /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.{Service}/{service-name} \
  --group-id {subresource}
```

### Step 2: Configure DNS

```bash
# Create private DNS zone
az network private-dns zone create \
  --resource-group your-rg \
  --name privatelink.your-service.com

# Link to VNet
az network private-dns link vnet create \
  --resource-group your-rg \
  --zone-name privatelink.your-service.com \
  --name your-dns-link \
  --virtual-network your-vnet \
  --registration-enabled false
```

### Step 3: Add Private Endpoint Rule

```yaml
outbound_rules:
  - name: private-repo-endpoint
    type: private_endpoint
    destination:
      service_resource_id: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.{Service}/{service-name}
      subresource_target: {target}
```

## Best Practices

### 1. Security Considerations

- **Minimize Exposure**: Only allow access to necessary storage/registry resources
- **Use Managed Identity**: Avoid storing credentials in code or configuration
- **Regular Auditing**: Review private package access regularly
- **Version Control**: Track private package versions and dependencies

### 2. Package Management

- **Mirror Public Packages**: Consider mirroring public packages in your private repository
- **Dependency Management**: Maintain clear dependency trees for private packages
- **Testing**: Test private package installations in isolated environments
- **Documentation**: Document private package sources and installation procedures

### 3. Performance Optimization

- **Local Caching**: Cache frequently used packages in storage
- **Regional Storage**: Use storage accounts in the same region as your workspace
- **CDN Integration**: Consider Azure CDN for global package distribution
- **Compression**: Use compressed package formats to reduce download time

### 4. Monitoring and Maintenance

- **Access Logging**: Monitor access to private package repositories
- **Health Checks**: Regularly verify private package availability
- **Update Procedures**: Establish processes for updating private packages
- **Backup Strategy**: Maintain backups of critical private packages

## Examples

### Example 1: Mixed Public and Private Environment

```bash
# requirements.txt with mixed sources
numpy==1.21.0  # Public PyPI
scipy>=1.7.0   # Public PyPI
https://yourstorageaccount.blob.core.windows.net/packages/internal-ml-lib-1.0.0-py3-none-any.whl  # Private storage
company-utils @ git+https://github.com/yourcompany/utils.git@v1.2.3  # Private GitHub (if accessible)
```

### Example 2: Complete Storage-Based Solution

```yaml
# Workspace configuration
managed_network:
  isolation_mode: allow_only_approved_outbound
  outbound_rules:
    # Public repositories
    - name: pypi-packages
      type: fqdn
      destination: "*.pypi.org"
    - name: python-hosted
      type: fqdn
      destination: "*.pythonhosted.org"
    
    # Private package storage
    - name: private-packages
      type: private_endpoint
      destination:
        service_resource_id: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage}
        subresource_target: blob
```

### Example 3: ACR-Based Custom Environment

```yaml
# Custom environment with pre-installed private packages
name: secure-ml-env
docker:
  image: youracr.azurecr.io/secure-ml-base:latest
conda_file: |
  name: secure-ml-env
  channels:
    - conda-forge
  dependencies:
    - python=3.9
    - pip
    - pip:
      - numpy
      - scikit-learn
      # Private packages are pre-installed in the Docker image
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify managed identity has access to storage/registry
   - Check access policies and RBAC permissions
   - Ensure service principal credentials are valid

2. **Network Connectivity**
   - Verify private endpoints are properly configured
   - Check DNS resolution for private domains
   - Confirm firewall rules allow required traffic

3. **Package Installation Errors**
   - Validate package file integrity
   - Check Python version compatibility
   - Verify dependency resolution

### Diagnostic Steps

```bash
# Test storage access
az storage blob list \
  --container packages \
  --account-name yourstorageaccount

# Test ACR access
az acr repository list --name youracr

# Test network connectivity from compute instance
curl -I https://yourstorageaccount.blob.core.windows.net/
nslookup youracr.azurecr.io
```

## Additional Resources

- [Azure Storage Private Endpoints](https://docs.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [Azure Container Registry Authentication](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-authentication)
- [Azure Artifacts Python Packages](https://docs.microsoft.com/en-us/azure/devops/artifacts/quickstarts/python-packages)
- [Azure ML Custom Environments](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-manage-environments-v2) 