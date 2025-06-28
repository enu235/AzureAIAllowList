# Analysis & Discovery Guide

> **⚠️ DISCLAIMER**: This analysis and discovery guide is provided "AS IS" without warranty of any kind, express or implied. Users implement these configurations at their own risk and should thoroughly test all configurations in non-production environments before deployment.

This comprehensive guide covers both connectivity analysis and package discovery capabilities of the Azure AI Foundry & Machine Learning Package Tool.

## 🎯 Overview

The tool provides two main analysis capabilities:

1. **🔍 Connectivity Analysis** - Network configuration, security assessment, and resource discovery
2. **📦 Package Discovery** - Python package dependency analysis and FQDN generation

Both can be run independently or together for comprehensive workspace analysis.

## 🔍 Connectivity Analysis

### What It Analyzes

Connectivity analysis examines your Azure AI Foundry hub or Azure ML workspace to provide:

- **Network Configuration**: VNet setup, isolation modes, private endpoints
- **Security Posture**: Security scores, compliance status, risk assessment  
- **Resource Inventory**: All connected Azure resources with security evaluation
- **Visual Diagrams**: Network relationships using Mermaid charts
- **Actionable Recommendations**: Specific steps to improve security

### Analysis Flow

```mermaid
graph TD
    A[Start Analysis] --> B[Authenticate Azure CLI]
    B --> C[Discover Workspace]
    C --> D[Analyze Network Config]
    D --> E[Inventory Resources]
    E --> F[Security Assessment]
    F --> G[Generate Visual Diagrams]
    G --> H[Create Recommendations]
    H --> I[Generate Reports]
    
    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style F fill:#fff3e0
```

### Network Configuration Types

#### 1. Managed Virtual Network

**Azure-managed network infrastructure:**

```mermaid
graph LR
    subgraph "Azure AI Foundry Hub"
        Hub[AI Foundry Hub]
        ManagedVNet[Managed VNet]
    end
    
    subgraph "Azure Services"
        Storage[Storage Account]
        KeyVault[Key Vault]
        ACR[Container Registry]
        AIServices[AI Services]
    end
    
    Hub --> ManagedVNet
    ManagedVNet --> Storage
    ManagedVNet --> KeyVault
    ManagedVNet --> ACR
    ManagedVNet --> AIServices
    
    style Hub fill:#e1f5fe
    style ManagedVNet fill:#f3e5f5
    style Storage fill:#e8f5e8
    style KeyVault fill:#fff3e0
    style ACR fill:#fce4ec
    style AIServices fill:#e0f2f1
```

**Characteristics:**
- Automatic subnet and IP management
- Built-in security configurations
- Simplified outbound rule management
- Two isolation modes: "Allow Internet Outbound" vs "Allow Only Approved Outbound"

#### 2. Customer-Managed Virtual Network

**User-controlled network infrastructure:**

```mermaid
graph LR
    subgraph "Customer VNet"
        Subnet1[ML Subnet]
        Subnet2[Compute Subnet]
        NSG[Network Security Group]
        UDR[User Defined Routes]
    end
    
    subgraph "Azure Services"
        Storage[Storage Account]
        KeyVault[Key Vault]
        ACR[Container Registry]
    end
    
    subgraph "On-Premises"
        OnPrem[Corporate Network]
        ExpressRoute[ExpressRoute]
    end
    
    Subnet1 --> NSG
    Subnet2 --> NSG
    NSG --> UDR
    UDR --> Storage
    UDR --> KeyVault
    UDR --> ACR
    OnPrem --> ExpressRoute
    ExpressRoute --> Subnet1
    
    style Subnet1 fill:#e1f5fe
    style Subnet2 fill:#e1f5fe
    style NSG fill:#fff3e0
    style UDR fill:#f3e5f5
```

**Characteristics:**
- Full control over network configuration
- Custom routing and security rules
- Integration with on-premises networks
- Manual private endpoint management

### Security Assessment

The tool calculates security scores based on multiple factors:

| Factor | Weight | Good Practice |
|--------|--------|---------------|
| **Private Endpoints** | 30% | All critical resources use private endpoints |
| **Public Access** | 25% | Public network access disabled |
| **Network Isolation** | 20% | "Allow Only Approved Outbound" mode |
| **Resource Configuration** | 15% | Secure defaults for storage, key vault, etc. |
| **Compliance** | 10% | Meets organizational security standards |

#### Security Score Interpretation

- **🟢 80-100**: Excellent security posture
- **🟡 60-79**: Good with room for improvement  
- **🟠 40-59**: Moderate security concerns
- **🔴 0-39**: Significant security issues requiring attention

### Sample Connectivity Report

```markdown
# Azure AI Foundry Connectivity Analysis

## 📋 Executive Summary

**Workspace:** production-ai-hub  
**Type:** Azure AI Foundry Hub  
**Location:** East US  
**Analysis Date:** 2024-06-28 15:30:25

### Security Overview
- **Overall Score:** 85/100 🟢
- **Network Type:** Managed Virtual Network
- **Isolation Mode:** Allow Only Approved Outbound
- **Public Access:** ✅ Disabled

## 🔗 Connected Resources

| Resource | Type | Access Method | Security Status |
|----------|------|---------------|-----------------|
| prodstorageaccount | Storage Account | Private Endpoint | ✅ Secure |
| prodkeyvault | Key Vault | Private Endpoint | ✅ Secure |
| prodregistry | Container Registry | Public Access | ⚠️ Review Needed |

## 🛡️ Recommendations

1. **High Priority**: Enable private endpoint for Container Registry
2. **Medium Priority**: Review outbound rules for completeness
3. **Low Priority**: Consider enabling diagnostic logging
```

## 📦 Package Discovery

### What It Discovers

Package discovery analyzes your Python dependencies to generate network allowlists:

- **Package Sources**: PyPI, Conda, private repositories
- **Direct Dependencies**: Packages explicitly listed in your files
- **Transitive Dependencies**: Indirect dependencies of your packages
- **Download URLs**: All FQDNs needed for package installation
- **Platform Variations**: OS-specific package requirements

### Supported Package File Formats

```mermaid
graph TD
    subgraph "Input Files"
        A[requirements.txt]
        B[environment.yml]
        C[pyproject.toml]
        D[Pipfile/Pipfile.lock]
        E[setup.py/setup.cfg]
    end
    
    subgraph "Package Managers"
        F[pip]
        G[conda]
        H[poetry]
        I[pipenv]
        J[setuptools]
    end
    
    subgraph "Output"
        K[FQDN List]
        L[Azure CLI Commands]
        M[Firewall Rules]
    end
    
    A --> F
    B --> G
    C --> H
    D --> I
    E --> J
    
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L
    K --> M
    
    style A fill:#e1f5fe
    style B fill:#e1f5fe
    style C fill:#e1f5fe
    style D fill:#e1f5fe
    style E fill:#e1f5fe
    style K fill:#c8e6c9
    style L fill:#c8e6c9
    style M fill:#c8e6c9
```

### Package Resolution Process

```mermaid
sequenceDiagram
    participant User
    participant Tool
    participant PyPI
    participant Conda
    participant Private
    
    User->>Tool: Provide package files
    Tool->>Tool: Parse package specifications
    Tool->>PyPI: Query package metadata
    Tool->>Conda: Query conda packages
    Tool->>Private: Query private repositories
    PyPI-->>Tool: Package URLs
    Conda-->>Tool: Channel URLs
    Private-->>Tool: Repository URLs
    Tool->>Tool: Extract FQDNs
    Tool->>User: Generate allowlist
```

### AI Foundry Enhanced Features

When analyzing Azure AI Foundry hubs, additional package sources are included:

#### VS Code Server Integration
```
*.vscode-cdn.net
marketplace.visualstudio.com
*.vo.msecnd.net
code.visualstudio.com
```

#### HuggingFace Model Access
```
huggingface.co
*.huggingface.co
cdn-lfs.huggingface.co
datasets-server.huggingface.co
```

#### Prompt Flow Dependencies
```
api.github.com
github.com
raw.githubusercontent.com
```

### Package Discovery Flow

```mermaid
graph TD
    A[Input Package Files] --> B{File Type Detection}
    
    B -->|requirements.txt| C[Pip Parser]
    B -->|environment.yml| D[Conda Parser] 
    B -->|pyproject.toml| E[Poetry Parser]
    B -->|Pipfile| F[Pipenv Parser]
    B -->|setup.py| G[Setuptools Parser]
    
    C --> H[Dependency Resolution]
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> I{Include Transitive?}
    I -->|Yes| J[Resolve Transitive Dependencies]
    I -->|No| K[Direct Dependencies Only]
    
    J --> L[Extract Package URLs]
    K --> L
    
    L --> M[Map to FQDNs]
    M --> N[Platform Analysis]
    N --> O[Generate Allowlist]
    
    style A fill:#e1f5fe
    style O fill:#c8e6c9
    style I fill:#fff3e0
```

### Example Package Analysis Output

```bash
# Required FQDNs for Package Installation

## Python Package Index
pypi.org
*.pythonhosted.org
files.pythonhosted.org

## GitHub Repositories  
github.com
api.github.com
codeload.github.com
raw.githubusercontent.com

## Conda Repositories
anaconda.org
*.anaconda.org
conda.anaconda.org
repo.anaconda.com

## AI Foundry Enhanced (if enabled)
*.vscode-cdn.net
marketplace.visualstudio.com
huggingface.co
*.huggingface.co
```

## 🔄 Workspace Comparison Analysis

Compare two workspaces to identify configuration differences:

### Comparison Process

```mermaid
graph TD
    A[Select Workspace 1] --> C[Analyze Workspace 1]
    B[Select Workspace 2] --> D[Analyze Workspace 2]
    
    C --> E[Connectivity Analysis 1]
    D --> F[Connectivity Analysis 2]
    
    E --> G[Compare Network Configs]
    F --> G
    
    G --> H[Compare Security Settings]
    H --> I[Compare Resources]
    I --> J[Generate Diff Report]
    
    style A fill:#e1f5fe
    style B fill:#e1f5fe
    style J fill:#c8e6c9
```

### Sample Comparison Report

```markdown
# Workspace Comparison: Production vs Development

## Configuration Differences

| Setting | Production | Development | Status |
|---------|------------|-------------|--------|
| **Network Isolation** | Allow Only Approved | Allow Internet | ⚠️ Different |
| **Public Access** | Disabled | Enabled | ⚠️ Different |
| **Private Endpoints** | 4/4 enabled | 2/4 enabled | ⚠️ Different |

## Security Score Comparison
- **Production**: 85/100 🟢
- **Development**: 65/100 🟡
- **Gap**: 20 points

## Recommendations
1. Align development environment with production security settings
2. Enable missing private endpoints in development
3. Consider separate security policies for dev/prod
```

## 🎯 Combined Analysis

Running both connectivity analysis and package discovery together provides the most comprehensive view:

### Benefits of Combined Analysis

1. **Complete FQDN Coverage**: Network requirements + package requirements
2. **Holistic Security View**: Infrastructure security + dependency security
3. **Actionable Recommendations**: Both network and package management guidance
4. **Compliance Reporting**: Complete documentation for security reviews

### Combined Analysis Flow

```mermaid
graph TD
    A[Start Combined Analysis] --> B[Workspace Discovery]
    B --> C[Connectivity Analysis]
    B --> D[Package Discovery]
    
    C --> E[Network Configuration]
    C --> F[Resource Inventory]
    C --> G[Security Assessment]
    
    D --> H[Package Resolution]
    D --> I[FQDN Extraction]
    D --> J[Private Repo Detection]
    
    E --> K[Merge Results]
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L[Generate Comprehensive Report]
    L --> M[Security Recommendations]
    L --> N[Implementation Guide]
    
    style A fill:#e1f5fe
    style L fill:#c8e6c9
    style M fill:#fff3e0
    style N fill:#f3e5f5
```

## 🛠️ Implementation Examples

### Azure Firewall Application Rules

```json
{
  "applicationRuleCollections": [
    {
      "name": "AzureMLPackages",
      "priority": 100,
      "action": "Allow",
      "rules": [
        {
          "name": "PythonPackages",
          "protocols": [
            {"port": 443, "protocolType": "Https"}
          ],
          "targetFqdns": [
            "pypi.org",
            "*.pythonhosted.org", 
            "github.com",
            "api.github.com"
          ],
          "sourceAddresses": ["10.0.0.0/8"]
        }
      ]
    }
  ]
}
```

### Network Security Group Rules

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

## 🚨 Troubleshooting

### Common Analysis Issues

1. **Authentication Failures**
   ```bash
   # Ensure Azure CLI is configured
   az login
   az account set --subscription "your-subscription-id"
   ```

2. **Permission Errors**
   ```bash
   # Required roles:
   # - Reader on workspace and resources
   # - Contributor for network modifications
   ```

3. **Package Resolution Failures**
   ```bash
   # Test package file syntax
   pip install --dry-run -r requirements.txt
   ```

4. **Network Timeout Issues**
   ```bash
   # Check network connectivity
   curl -I https://pypi.org
   curl -I https://api.github.com
   ```

### Performance Optimization

- **Use caching**: Results are cached for repeated analyses
- **Parallel processing**: Multiple workspaces analyzed concurrently
- **Incremental updates**: Only analyze changed components
- **Resource filtering**: Focus on specific resource types

## 📊 Best Practices

### For Connectivity Analysis

1. **Regular Monitoring**: Schedule monthly connectivity reviews
2. **Security Baselines**: Establish security score targets  
3. **Change Tracking**: Monitor configuration drift over time
4. **Compliance**: Use reports for security audits

### For Package Discovery

1. **Version Pinning**: Use exact package versions in production
2. **Dependency Auditing**: Regular security scans of dependencies
3. **Private Repository Strategy**: Clear policies for internal packages
4. **Platform Consistency**: Ensure cross-platform compatibility

### For Combined Analysis

1. **Holistic Reviews**: Analyze both network and package security together
2. **Environment Parity**: Compare dev/staging/prod configurations
3. **Documentation**: Maintain current network diagrams and package inventories
4. **Automation**: Integrate analysis into CI/CD pipelines

---

> **Note**: This analysis framework provides comprehensive visibility into your Azure AI/ML environment security posture. Always validate recommendations in non-production environments before implementing changes. 