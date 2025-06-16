"""
Output formatters for generating Azure ML workspace configurations
"""

import json
import yaml
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

from .utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseOutputFormatter(ABC):
    """Base class for output formatters."""
    
    def __init__(self, workspace_name: str, resource_group: str, subscription_id: Optional[str] = None, hub_type: str = 'azure-ml'):
        self.workspace_name = workspace_name
        self.resource_group = resource_group
        self.subscription_id = subscription_id
        self.hub_type = hub_type
    
    @abstractmethod
    def format_domains(self, domains: List[str]) -> str:
        """Format domains into the appropriate output format."""
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """Get the format name."""
        pass

class AzureCliFormatter(BaseOutputFormatter):
    """Formatter for Azure CLI commands."""
    
    def get_format_name(self) -> str:
        return "Azure CLI"
    
    def format_domains(self, domains: List[str]) -> str:
        """Generate Azure CLI commands for adding FQDN rules."""
        if not domains:
            return "# No new domains to add - all required domains are already configured."
        
        commands = []
        
        # Add header comment
        hub_display = "Azure AI Foundry Hub" if self.hub_type == 'ai-foundry' else "Azure ML Workspace"
        commands.append("#!/bin/bash")
        commands.append("#")
        commands.append(f"# {hub_display} Outbound Rules Configuration")
        commands.append(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        commands.append(f"# Hub Type: {self.hub_type}")
        commands.append(f"# Workspace/Hub: {self.workspace_name}")
        commands.append(f"# Resource Group: {self.resource_group}")
        commands.append("#")
        commands.append("# 🚨 IMPORTANT: Review these commands before execution!")
        commands.append("# Test in non-production environment first.")
        commands.append("#")
        commands.append("")
        
        # Set common variables
        commands.append("# Set variables")
        commands.append(f'WORKSPACE_NAME="{self.workspace_name}"')
        commands.append(f'RESOURCE_GROUP="{self.resource_group}"')
        if self.subscription_id:
            commands.append(f'SUBSCRIPTION_ID="{self.subscription_id}"')
            commands.append("")
            commands.append("# Set subscription context")
            commands.append("az account set --subscription \"$SUBSCRIPTION_ID\"")
        commands.append("")
        
        # Add commands for each domain
        commands.append("# Add FQDN outbound rules for package domains")
        for i, domain in enumerate(sorted(domains), 1):
            rule_name = self._generate_rule_name(domain, i)
            
            cmd_parts = [
                "az ml workspace outbound-rule create",
                "--workspace-name \"$WORKSPACE_NAME\"",
                "--resource-group \"$RESOURCE_GROUP\"",
                f"--rule-name \"{rule_name}\"",
                "--type fqdn",
                f"--destination \"{domain}\""
            ]
            
            commands.append(" \\\n  ".join(cmd_parts))
            commands.append("")
        
        # Add validation commands
        commands.append("# Validate configuration")
        commands.append("echo \"Listing all outbound rules:\"")
        commands.append("az ml workspace outbound-rule list \\")
        commands.append("  --workspace-name \"$WORKSPACE_NAME\" \\")
        commands.append("  --resource-group \"$RESOURCE_GROUP\" \\")
        commands.append("  --output table")
        commands.append("")
        
        # Add final notes
        commands.append("# Configuration complete!")
        commands.append("# Next steps:")
        commands.append("# 1. Test package installation in your workspace")
        commands.append("# 2. Monitor for any additional domain requirements")
        commands.append("# 3. Update this configuration as needed")
        
        return "\n".join(commands)
    
    def _generate_rule_name(self, domain: str, index: int) -> str:
        """Generate a descriptive rule name for a domain."""
        # Clean domain for rule name (remove wildcards and special chars)
        clean_domain = domain.replace("*.", "").replace(".", "-")
        
        # Map common domains to descriptive names
        domain_mapping = {
            "pypi-org": "pypi-packages",
            "pythonhosted-org": "python-hosted-packages", 
            "anaconda-org": "conda-packages",
            "conda-io": "conda-forge-packages",
            "anaconda-com": "anaconda-packages",
            "github-com": "github-content",
            "gitlab-com": "gitlab-content",
            "bitbucket-org": "bitbucket-content"
        }
        
        return domain_mapping.get(clean_domain, f"package-domain-{index:02d}")

class JsonFormatter(BaseOutputFormatter):
    """Formatter for JSON output."""
    
    def get_format_name(self) -> str:
        return "JSON"
    
    def format_domains(self, domains: List[str]) -> str:
        """Generate JSON configuration for domains."""
        config = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "workspace_name": self.workspace_name,
                "resource_group": self.resource_group,
                "subscription_id": self.subscription_id,
                "tool": "Azure ML Package URL Allowlist Tool"
            },
            "outbound_rules": []
        }
        
        for i, domain in enumerate(sorted(domains), 1):
            rule = {
                "name": self._generate_rule_name(domain, i),
                "type": "fqdn",
                "destination": domain,
                "description": f"Allow access to {domain} for package downloads"
            }
            config["outbound_rules"].append(rule)
        
        return json.dumps(config, indent=2)
    
    def _generate_rule_name(self, domain: str, index: int) -> str:
        """Generate a descriptive rule name for a domain."""
        clean_domain = domain.replace("*.", "").replace(".", "-")
        return f"package-domain-{clean_domain}-{index:02d}"

class YamlFormatter(BaseOutputFormatter):
    """Formatter for YAML output (ARM/Bicep template snippets)."""
    
    def get_format_name(self) -> str:
        return "YAML"
    
    def format_domains(self, domains: List[str]) -> str:
        """Generate YAML configuration snippets."""
        # Generate managed network outbound rules section
        outbound_rules = []
        
        for i, domain in enumerate(sorted(domains), 1):
            rule = {
                "name": self._generate_rule_name(domain, i),
                "type": "fqdn", 
                "destination": domain
            }
            outbound_rules.append(rule)
        
        config = {
            "# Azure ML Workspace Outbound Rules Configuration": None,
            "# Add this to your workspace ARM/Bicep template": None,
            "managed_network": {
                "isolation_mode": "allow_only_approved_outbound",
                "outbound_rules": outbound_rules
            }
        }
        
        # Custom YAML output with comments
        yaml_output = []
        yaml_output.append("# Azure ML Workspace Outbound Rules Configuration")
        yaml_output.append(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        yaml_output.append(f"# Workspace: {self.workspace_name}")
        yaml_output.append(f"# Resource Group: {self.resource_group}")
        yaml_output.append("#")
        yaml_output.append("# Add this section to your Azure ML workspace configuration")
        yaml_output.append("")
        
        # Add managed network configuration
        yaml_output.append("managed_network:")
        yaml_output.append("  isolation_mode: allow_only_approved_outbound")
        yaml_output.append("  outbound_rules:")
        
        for rule in outbound_rules:
            yaml_output.append(f"  - name: {rule['name']}")
            yaml_output.append(f"    type: {rule['type']}")
            yaml_output.append(f"    destination: {rule['destination']}")
        
        yaml_output.append("")
        yaml_output.append("# Alternative: Individual rule snippets for existing workspace")
        yaml_output.append("# Use these if adding to an existing configuration:")
        yaml_output.append("")
        
        for rule in outbound_rules:
            yaml_output.append(f"- name: {rule['name']}")
            yaml_output.append(f"  type: {rule['type']}")
            yaml_output.append(f"  destination: {rule['destination']}")
            yaml_output.append("")
        
        return "\n".join(yaml_output)
    
    def _generate_rule_name(self, domain: str, index: int) -> str:
        """Generate a descriptive rule name for a domain."""
        clean_domain = domain.replace("*.", "").replace(".", "-")
        domain_mapping = {
            "pypi-org": "pypi-packages",
            "pythonhosted-org": "python-hosted-packages",
            "anaconda-org": "conda-packages", 
            "conda-io": "conda-forge-packages",
            "anaconda-com": "anaconda-packages"
        }
        return domain_mapping.get(clean_domain, f"package-domain-{index:02d}")

class PowerShellFormatter(BaseOutputFormatter):
    """Formatter for Azure PowerShell commands."""
    
    def get_format_name(self) -> str:
        return "PowerShell"
    
    def format_domains(self, domains: List[str]) -> str:
        """Generate Azure PowerShell commands for adding FQDN rules."""
        if not domains:
            return "# No new domains to add - all required domains are already configured."
        
        commands = []
        
        # Add header comment
        commands.append("# Azure ML Workspace Outbound Rules Configuration")
        commands.append(f"# Generated on: {(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
        commands.append(f"# Workspace: {self.workspace_name}")
        commands.append(f"# Resource Group: {self.resource_group}")
        commands.append("#")
        commands.append("# 🚨 IMPORTANT: Review these commands before execution!")
        commands.append("# Test in non-production environment first.")
        commands.append("#")
        commands.append("")
        
        # Set variables
        commands.append("# Set variables")
        commands.append(f'$WorkspaceName = "{self.workspace_name}"')
        commands.append(f'$ResourceGroupName = "{self.resource_group}"')
        if self.subscription_id:
            commands.append(f'$SubscriptionId = "{self.subscription_id}"')
            commands.append("")
            commands.append("# Set subscription context")
            commands.append("Set-AzContext -SubscriptionId $SubscriptionId")
        commands.append("")
        
        # Add commands for each domain
        commands.append("# Add FQDN outbound rules for package domains")
        for i, domain in enumerate(sorted(domains), 1):
            rule_name = self._generate_rule_name(domain, i)
            
            commands.append(f"# Adding rule for {domain}")
            commands.append("az ml workspace outbound-rule create `")
            commands.append(f"  --workspace-name $WorkspaceName `")
            commands.append(f"  --resource-group $ResourceGroupName `")
            commands.append(f"  --rule-name '{rule_name}' `")
            commands.append(f"  --type fqdn `")
            commands.append(f"  --destination '{domain}'")
            commands.append("")
        
        # Add validation
        commands.append("# Validate configuration")
        commands.append("Write-Host 'Listing all outbound rules:'")
        commands.append("az ml workspace outbound-rule list `")
        commands.append("  --workspace-name $WorkspaceName `")
        commands.append("  --resource-group $ResourceGroupName `")
        commands.append("  --output table")
        
        return "\n".join(commands)
    
    def _generate_rule_name(self, domain: str, index: int) -> str:
        """Generate a descriptive rule name for a domain."""
        clean_domain = domain.replace("*.", "").replace(".", "-")
        domain_mapping = {
            "pypi-org": "pypi-packages",
            "pythonhosted-org": "python-hosted-packages",
            "anaconda-org": "conda-packages",
            "conda-io": "conda-forge-packages",
            "anaconda-com": "anaconda-packages"
        }
        return domain_mapping.get(clean_domain, f"package-domain-{index:02d}")

class OutputFormatterFactory:
    """Factory to create appropriate output formatter."""
    
    @staticmethod
    def create_formatter(format_type: str, workspace_name: str, resource_group: str, 
                        subscription_id: Optional[str] = None, hub_type: str = 'azure-ml') -> BaseOutputFormatter:
        """
        Create the appropriate formatter for the output type.
        
        Args:
            format_type: Type of output format (cli, json, yaml, powershell)
            workspace_name: Azure ML workspace name
            resource_group: Resource group name
            subscription_id: Optional subscription ID
            
        Returns:
            Appropriate output formatter instance
        """
        format_type = format_type.lower()
        
        if format_type == 'cli':
            return AzureCliFormatter(workspace_name, resource_group, subscription_id, hub_type)
        elif format_type == 'json':
            return JsonFormatter(workspace_name, resource_group, subscription_id, hub_type)
        elif format_type == 'yaml':
            return YamlFormatter(workspace_name, resource_group, subscription_id, hub_type)
        elif format_type == 'powershell':
            return PowerShellFormatter(workspace_name, resource_group, subscription_id, hub_type)
        else:
            raise ValueError(f"Unsupported output format: {format_type}")
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported output formats."""
        return ['cli', 'json', 'yaml', 'powershell'] 