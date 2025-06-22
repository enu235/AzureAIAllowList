# Azure Machine Learning Network Configuration Guide

> **⚠️ DISCLAIMER**: This documentation is provided "AS IS" without warranty of any kind, express or implied. Users implement these configurations at their own risk and should thoroughly test all network rules in non-production environments before deployment.

This comprehensive guide focuses on Azure Machine Learning workspace network configurations for secured environments. Azure ML remains fully supported with complete feature parity in our package allowlist tool.

## ✨ **Full Azure ML Support & Backward Compatibility**

This tool provides complete support for Azure Machine Learning workspaces with:
- 🏗️ **Complete Workspace Support**: Full compatibility with Azure ML workspaces
- 🔒 **All Network Modes**: Managed VNet, customer-managed VNet, and hybrid configurations  
- 📦 **Complete Package Discovery**: All package manager formats supported
- 🔄 **Flexible Integration**: Seamless integration with other Azure services
- 🛠️ **Enterprise Integration**: Existing workflows and automation continue to work

## Table of Contents

- [Overview](#overview)
- [Network Isolation Modes](#network-isolation-modes)
- [Managed Virtual Networks](#managed-virtual-networks)
- [Customer-Managed Virtual Networks](#customer-managed-virtual-networks)
- [Required Outbound Traffic](#required-outbound-traffic)
- [Package Download URLs](#package-download-urls)
- [Configuration Examples](#configuration-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

Azure Machine Learning workspaces can be configured with different levels of network isolation to meet security and compliance requirements. When network restrictions are in place, you must explicitly allow outbound traffic to specific domains for package downloads and ML operations.

### Key Concepts

- **Managed Virtual Network**: Azure ML manages the network configuration
- **Customer-Managed Virtual Network**: You control the network infrastructure
- **Isolation Modes**: Different levels of network restriction
- **Outbound Rules**: Explicit allowlists for external traffic

## Network Isolation Modes

Azure ML supports two primary isolation modes for managed virtual networks:

### 1. Allow Internet Outbound

```yaml
managed_network:
  isolation_mode: allow_internet_outbound
  outbound_rules:
    - name: custom-rule
      type: fqdn
      destination: your-private-service.com
```

**Characteristics:**
- Default behavior allows most internet traffic
- You can add specific rules for private resources
- Suitable for development and less restrictive environments
- Package downloads work without additional configuration

### 2. Allow Only Approved Outbound

```yaml
managed_network:
  isolation_mode: allow_only_approved_outbound
  outbound_rules:
    - name: pypi-packages
      type: fqdn
      destination: "*.pypi.org"
    - name: conda-packages
      type: fqdn
      destination: "*.anaconda.org"
```

**Characteristics:**
- Blocks all internet traffic by default
- Requires explicit rules for all external access
- Highest security level
- Requires careful configuration for package downloads

## Managed Virtual Networks

Azure ML managed virtual networks automatically handle network infrastructure while allowing you to control access policies.

### Benefits

- Automatic subnet and IP management
- Built-in security configurations
- Easy outbound rule management
- Integration with Azure services

### Configuration

Managed virtual networks are configured through the workspace definition:

```yaml
name: secure-workspace
managed_network:
  isolation_mode: allow_only_approved_outbound
  outbound_rules:
    # Package repositories
    - name: pypi-packages
      type: fqdn
      destination: "*.pypi.org"
    - name: python-hosted-packages
      type: fqdn
      destination: "*.pythonhosted.org"
    - name: conda-packages
      type: fqdn
      destination: "*.anaconda.org"
    
    # Private endpoints for your resources
    - name: private-storage
      type: private_endpoint
      destination:
        service_resource_id: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{name}
        subresource_target: blob
```

### Rule Types

1. **FQDN Rules**: Allow access to specific domains
   ```yaml
   - name: example-domain
     type: fqdn
     destination: "*.example.com"
   ```

2. **Service Tag Rules**: Allow access to Azure service categories
   ```yaml
   - name: storage-access
     type: service_tag
     destination:
       service_tag: Storage
       protocol: TCP
       port_ranges: 443
   ```

3. **Private Endpoint Rules**: Connect to private Azure resources
   ```yaml
   - name: private-storage
     type: private_endpoint
     destination:
       service_resource_id: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage}
       subresource_target: blob
   ```

## Customer-Managed Virtual Networks

With customer-managed virtual networks, you control the entire network infrastructure including subnets, routing, and security rules.

### Key Components

- **Network Security Groups (NSGs)**: Control traffic at the subnet level
- **Azure Firewall**: Centralized network security
- **User-Defined Routes (UDRs)**: Custom routing rules
- **Private Endpoints**: Secure connections to Azure services

### Configuration Example

For customer-managed VNets, configure network access through NSG rules:

```json
{
  "securityRules": [
    {
      "name": "AllowPyPIOutbound",
      "properties": {
        "protocol": "TCP",
        "sourcePortRange": "*",
        "destinationPortRange": "443",
        "sourceAddressPrefix": "VirtualNetwork",
        "destinationAddressPrefix": "*.pypi.org",
        "access": "Allow",
        "priority": 1000,
        "direction": "Outbound"
      }
    }
  ]
}
```

## Required Outbound Traffic

All Azure ML workspaces require access to specific domains for core functionality:

### Azure ML Core Services

| Domain | Purpose | Ports |
|--------|---------|--------|
| *.azureml.ms | Azure ML API | 443 |
| *.azureml.net | Azure ML API | 443 |
| *.modelmanagement.azureml.net | Model management | 443 |
| ml.azure.com | Azure ML Studio | 443 |

### Authentication and Management

| Domain | Purpose | Ports |
|--------|---------|--------|
| login.microsoftonline.com | Authentication | 443 |
| management.azure.com | Azure Resource Manager | 443 |
| *.vault.azure.net | Key Vault access | 443 |

### Storage and Content

| Domain | Purpose | Ports |
|--------|---------|--------|
| *.blob.core.windows.net | Blob storage | 443 |
| *.file.core.windows.net | File storage | 443, 445 |
| *.table.core.windows.net | Table storage | 443 |

## Package Download URLs

Different package managers use different domains for downloading packages:

### Python (pip)

| Domain | Purpose |
|--------|---------|
| *.pypi.org | Primary Python package index |
| *.pythonhosted.org | Package file hosting |
| files.pythonhosted.org | Direct package downloads |

### Conda

| Domain | Purpose |
|--------|---------|
| *.anaconda.org | Anaconda package repository |
| *.conda.io | Conda-forge packages |
| *.anaconda.com | Commercial Anaconda packages |
| conda.anaconda.org | Default conda channel |

### Alternative Package Managers

| Tool | Domains |
|------|---------|
| uv | *.pypi.org, *.pythonhosted.org |
| poetry | *.pypi.org, *.pythonhosted.org |
| pipenv | *.pypi.org, *.pythonhosted.org |

## Configuration Examples

### Basic Managed VNet Configuration

```yaml
# Minimal configuration for Python packages
managed_network:
  isolation_mode: allow_only_approved_outbound
  outbound_rules:
    - name: pypi-packages
      type: fqdn
      destination: "*.pypi.org"
    - name: python-hosted
      type: fqdn
      destination: "*.pythonhosted.org"
```

### Comprehensive Configuration

```yaml
# Complete configuration for mixed environment
managed_network:
  isolation_mode: allow_only_approved_outbound
  outbound_rules:
    # Python packages
    - name: pypi-packages
      type: fqdn
      destination: "*.pypi.org"
    - name: python-hosted
      type: fqdn
      destination: "*.pythonhosted.org"
    
    # Conda packages
    - name: conda-packages
      type: fqdn
      destination: "*.anaconda.org"
    - name: conda-forge
      type: fqdn
      destination: "*.conda.io"
    
    # Git repositories (if using git+https installs)
    - name: github-packages
      type: fqdn
      destination: "*.github.com"
    
    # Private storage for custom packages
    - name: private-storage
      type: private_endpoint
      destination:
        service_resource_id: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{name}
        subresource_target: blob
```

### Azure CLI Commands

```bash
# Add FQDN rules for package domains
az ml workspace outbound-rule create \
  --workspace-name "my-workspace" \
  --resource-group "my-rg" \
  --rule-name "pypi-packages" \
  --type fqdn \
  --destination "*.pypi.org"

az ml workspace outbound-rule create \
  --workspace-name "my-workspace" \
  --resource-group "my-rg" \
  --rule-name "python-hosted" \
  --type fqdn \
  --destination "*.pythonhosted.org"
```

## Best Practices

### 1. Start with Minimal Rules

Begin with the most restrictive configuration and add rules as needed:

```yaml
managed_network:
  isolation_mode: allow_only_approved_outbound
  outbound_rules:
    # Start with only essential domains
    - name: pypi-packages
      type: fqdn
      destination: "*.pypi.org"
```

### 2. Use Wildcards Appropriately

Wildcards reduce the number of rules but may be overly permissive:

```yaml
# Good: Specific subdomain wildcard
destination: "*.pypi.org"

# Avoid: Overly broad wildcards
destination: "*.com"
```

### 3. Document Your Rules

Always document why each rule is needed:

```yaml
outbound_rules:
  - name: pypi-packages
    type: fqdn
    destination: "*.pypi.org"
    # Purpose: Allow pip package downloads for ML training
```

### 4. Monitor and Audit

Regularly review outbound rules and remove unused ones:

```bash
# List all outbound rules
az ml workspace outbound-rule list \
  --workspace-name "my-workspace" \
  --resource-group "my-rg" \
  --output table
```

### 5. Test in Non-Production

Always test new rules in a development environment first:

1. Apply rules to dev workspace
2. Test package installation
3. Monitor for connection failures
4. Apply to production after validation

## Troubleshooting

### Common Issues

1. **Package Installation Failures**
   - Check if required domains are allowed
   - Verify rule names don't conflict
   - Ensure wildcards cover all subdomains

2. **Authentication Errors**
   - Verify Azure AD domains are accessible
   - Check token endpoint access
   - Ensure proper authentication flow

3. **Storage Access Issues**
   - Confirm storage domains are allowed
   - Check private endpoint configuration
   - Verify storage account networking settings

### Diagnostic Commands

```bash
# Check workspace configuration
az ml workspace show \
  --name "my-workspace" \
  --resource-group "my-rg"

# List outbound rules
az ml workspace outbound-rule list \
  --workspace-name "my-workspace" \
  --resource-group "my-rg"

# Test connectivity (from compute instance)
curl -I https://pypi.org
nslookup files.pythonhosted.org
```

### Log Analysis

Monitor Azure ML logs for network-related errors:

1. Check Activity Logs for rule creation failures
2. Review Application Insights for connectivity issues
3. Monitor compute instance logs for package installation errors

## Additional Resources

- [Azure ML Network Security Overview](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-access-azureml-behind-firewall)
- [Managed Virtual Network Documentation](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-managed-network)
- [Private Endpoint Configuration](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-secure-workspace-vnet)
- [Azure CLI ML Extension](https://learn.microsoft.com/en-us/cli/azure/ml) 