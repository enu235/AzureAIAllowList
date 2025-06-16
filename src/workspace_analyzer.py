"""
Azure ML Workspace analyzers for different network configurations
"""

import subprocess
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

from .utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class WorkspaceConfig:
    """Configuration information about an Azure ML workspace or AI Foundry hub."""
    name: str
    resource_group: str
    subscription_id: str
    network_mode: str  # "managed" or "customer_managed"
    isolation_mode: Optional[str]  # "allow_internet_outbound" or "allow_only_approved_outbound"
    existing_outbound_rules: List[Dict]
    existing_domains: Set[str]
    location: str
    private_endpoint_enabled: bool
    hub_type: str  # "azure-ml" or "ai-foundry"

class BaseWorkspaceAnalyzer(ABC):
    """Base class for workspace analyzers."""
    
    def __init__(self, workspace_name: str, resource_group: str, subscription_id: Optional[str] = None, hub_type: str = 'azure-ml'):
        self.workspace_name = workspace_name
        self.resource_group = resource_group
        self.subscription_id = subscription_id
        self.hub_type = hub_type
        
    @abstractmethod
    def analyze(self) -> WorkspaceConfig:
        """Analyze the workspace configuration."""
        pass
    
    @abstractmethod
    def get_missing_domains(self, required_domains: List[str]) -> List[str]:
        """Get domains that are not currently allowed in the workspace."""
        pass
    
    def _run_az_command(self, command: List[str]) -> Dict:
        """Run an Azure CLI command and return parsed JSON result."""
        try:
            cmd = ['az'] + command
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
            
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"Azure CLI command failed: {result.stderr}")
                raise RuntimeError(f"Azure CLI command failed: {result.stderr}")
            
            return json.loads(result.stdout) if result.stdout.strip() else {}
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Azure CLI command timed out")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Azure CLI output: {e}")
            raise RuntimeError(f"Failed to parse Azure CLI output: {e}")
        except Exception as e:
            logger.error(f"Error running Azure CLI command: {e}")
            raise

class ManagedVNetWorkspaceAnalyzer(BaseWorkspaceAnalyzer):
    """Analyzer for workspaces with managed virtual networks."""
    
    def analyze(self) -> WorkspaceConfig:
        """Analyze a managed virtual network workspace."""
        logger.info("Analyzing managed virtual network workspace...")
        
        # Get workspace details
        workspace_info = self._run_az_command([
            'ml', 'workspace', 'show',
            '--name', self.workspace_name,
            '--resource-group', self.resource_group
        ])
        
        # Extract managed network configuration
        managed_network = workspace_info.get('managed_network', {})
        isolation_mode = managed_network.get('isolation_mode', 'allow_internet_outbound')
        
        # Get existing outbound rules
        existing_rules = []
        existing_domains = set()
        
        try:
            rules_info = self._run_az_command([
                'ml', 'workspace', 'outbound-rule', 'list', 
                '--workspace-name', self.workspace_name,
                '--resource-group', self.resource_group
            ])
            
            if isinstance(rules_info, list):
                existing_rules = rules_info
            
            # Extract domains from existing FQDN rules
            for rule in existing_rules:
                if rule.get('type') == 'fqdn' and rule.get('destination'):
                    existing_domains.add(rule['destination'])
                    
        except Exception as e:
            logger.warning(f"Could not retrieve existing outbound rules: {e}")
        
        return WorkspaceConfig(
            name=self.workspace_name,
            resource_group=self.resource_group,
            subscription_id=workspace_info.get('id', '').split('/')[2] if workspace_info.get('id') else '',
            network_mode="managed",
            isolation_mode=isolation_mode,
            existing_outbound_rules=existing_rules,
            existing_domains=existing_domains,
            location=workspace_info.get('location', ''),
            private_endpoint_enabled=workspace_info.get('public_network_access', 'Enabled') == 'Disabled',
            hub_type=self.hub_type
        )
    
    def get_missing_domains(self, required_domains: List[str]) -> List[str]:
        """Get domains that need to be added to the workspace."""
        config = self.analyze()
        missing = []
        
        for domain in required_domains:
            # Check if domain or a parent wildcard domain is already configured
            domain_covered = False
            
            for existing_domain in config.existing_domains:
                if self._domain_matches(domain, existing_domain):
                    domain_covered = True
                    break
            
            if not domain_covered:
                missing.append(domain)
        
        return missing
    
    def _domain_matches(self, required_domain: str, existing_domain: str) -> bool:
        """Check if a required domain is covered by an existing domain rule."""
        # Remove wildcards for comparison
        required_clean = required_domain.replace('*.', '')
        existing_clean = existing_domain.replace('*.', '')
        
        # Exact match
        if required_domain == existing_domain:
            return True
        
        # Check if existing domain covers required domain
        if existing_domain.startswith('*.') and required_clean.endswith(existing_clean):
            return True
        
        return False

class CustomerManagedVNetWorkspaceAnalyzer(BaseWorkspaceAnalyzer):
    """Analyzer for workspaces with customer-managed virtual networks."""
    
    def analyze(self) -> WorkspaceConfig:
        """Analyze a customer-managed virtual network workspace."""
        logger.info("Analyzing customer-managed virtual network workspace...")
        
        # Get workspace details
        workspace_info = self._run_az_command([
            'ml', 'workspace', 'show',
            '--name', self.workspace_name,
            '--resource-group', self.resource_group
        ])
        
        # For customer-managed VNets, network rules are typically handled
        # through NSGs, Firewalls, or Route Tables rather than workspace-level rules
        existing_rules = []
        existing_domains = set()
        
        # Try to get any workspace-level rules if they exist
        try:
            rules_info = self._run_az_command([
                'ml', 'workspace', 'outbound-rule', 'list',
                '--workspace-name', self.workspace_name,
                '--resource-group', self.resource_group
            ])
            
            if isinstance(rules_info, list):
                existing_rules = rules_info
                
        except Exception as e:
            logger.debug(f"No workspace-level outbound rules found (expected for customer-managed VNet): {e}")
        
        return WorkspaceConfig(
            name=self.workspace_name,
            resource_group=self.resource_group,
            subscription_id=workspace_info.get('id', '').split('/')[2] if workspace_info.get('id') else '',
            network_mode="customer_managed",
            isolation_mode=None,  # Not applicable for customer-managed VNets
            existing_outbound_rules=existing_rules,
            existing_domains=existing_domains,
            location=workspace_info.get('location', ''),
            private_endpoint_enabled=workspace_info.get('public_network_access', 'Enabled') == 'Disabled',
            hub_type=self.hub_type
        )
    
    def get_missing_domains(self, required_domains: List[str]) -> List[str]:
        """For customer-managed VNets, all domains are considered 'missing' since they need to be configured at the network level."""
        return required_domains

class WorkspaceAnalyzerFactory:
    """Factory to create appropriate workspace analyzer based on workspace configuration."""
    
    def create_analyzer(self, workspace_name: str, resource_group: str, 
                       subscription_id: Optional[str] = None, hub_type: str = 'azure-ml') -> BaseWorkspaceAnalyzer:
        """
        Create the appropriate analyzer for the workspace.
        
        Args:
            workspace_name: Name of the Azure ML workspace
            resource_group: Resource group name
            subscription_id: Optional subscription ID
            
        Returns:
            Appropriate workspace analyzer instance
        """
        try:
            # Create a temporary analyzer to check workspace type
            temp_analyzer = ManagedVNetWorkspaceAnalyzer(workspace_name, resource_group, subscription_id, hub_type)
            
            # Get workspace info to determine network configuration
            workspace_info = temp_analyzer._run_az_command([
                'ml', 'workspace', 'show',
                '--name', workspace_name,
                '--resource-group', resource_group
            ])
            
            # Check if workspace has managed network configuration
            managed_network = workspace_info.get('managed_network')
            
            if managed_network:
                logger.info(f"Detected managed virtual network {hub_type}")
                return ManagedVNetWorkspaceAnalyzer(workspace_name, resource_group, subscription_id, hub_type)
            else:
                logger.info(f"Detected customer-managed virtual network {hub_type}")
                return CustomerManagedVNetWorkspaceAnalyzer(workspace_name, resource_group, subscription_id, hub_type)
                
        except Exception as e:
            logger.error(f"Failed to determine workspace type: {e}")
            # Default to managed VNet analyzer
            logger.warning("Defaulting to managed virtual network analyzer")
            return ManagedVNetWorkspaceAnalyzer(workspace_name, resource_group, subscription_id, hub_type) 