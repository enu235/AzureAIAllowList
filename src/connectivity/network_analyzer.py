from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from .base_analyzer import BaseAnalyzer, AnalysisResult
import json
import subprocess

@dataclass
class NetworkConfiguration:
    """Network configuration details"""
    isolation_mode: Optional[str] = None
    network_type: str = "unknown"  # managed, customer, or none
    public_network_access: bool = True
    private_endpoints: List[Dict] = field(default_factory=list)
    service_endpoints: List[Dict] = field(default_factory=list)
    outbound_rules: List[Dict] = field(default_factory=list)
    virtual_network: Optional[Dict] = None
    subnets: List[Dict] = field(default_factory=list)
    firewall_rules: List[Dict] = field(default_factory=list)

class NetworkAnalyzer(BaseAnalyzer):
    """Analyzes network configuration for AI Foundry and ML workspaces"""
    
    def __init__(self, workspace_name: str, resource_group: str,
                 subscription_id: Optional[str] = None, hub_type: str = 'azure-ml'):
        super().__init__(workspace_name, resource_group, subscription_id, hub_type)
        self.network_config = NetworkConfiguration()
        
    def analyze(self) -> AnalysisResult:
        """Perform network analysis"""
        try:
            # Get workspace details
            workspace_info = self._get_workspace_info()
            
            # Determine network type
            self._analyze_network_type(workspace_info)
            
            # Analyze based on network type
            if self.network_config.network_type == "managed":
                self._analyze_managed_network(workspace_info)
            elif self.network_config.network_type == "customer":
                self._analyze_customer_network(workspace_info)
            
            # Analyze private endpoints
            self._analyze_private_endpoints()
            
            # Analyze outbound rules
            self._analyze_outbound_rules()
            
            return AnalysisResult(
                success=True,
                message="Network analysis completed successfully",
                data=self._format_network_data()
            )
            
        except Exception as e:
            self.logger.error(f"Network analysis failed: {str(e)}")
            return AnalysisResult(
                success=False,
                message=f"Network analysis failed: {str(e)}",
                error=str(e)
            )
    
    def _get_workspace_info(self) -> Dict:
        """Get detailed workspace information"""
        cmd = ['az', 'ml', 'workspace', 'show',
               '--name', self.workspace_name,
               '--resource-group', self.resource_group,
               '--output', 'json']
        
        if self.subscription_id:
            cmd.extend(['--subscription', self.subscription_id])
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to get workspace info: {result.stderr}")
            
        return json.loads(result.stdout)
    
    def _analyze_network_type(self, workspace_info: Dict):
        """Determine network configuration type"""
        # Check for managed network
        managed_network = workspace_info.get('managed_network', {})
        if managed_network:
            self.network_config.network_type = "managed"
            self.network_config.isolation_mode = managed_network.get('isolation_mode')
        
        # Check for customer VNet
        elif workspace_info.get('private_endpoint_connections'):
            self.network_config.network_type = "customer"
        else:
            # Default network configuration
            self.network_config.network_type = "none"
            
        # Check public network access
        self.network_config.public_network_access = (
            workspace_info.get('public_network_access', 'Enabled') == 'Enabled'
        )
    
    def _analyze_managed_network(self, workspace_info: Dict):
        """Analyze managed virtual network configuration"""
        managed_network = workspace_info.get('managed_network', {})
        
        # Get outbound rules from workspace info
        outbound_rules = managed_network.get('outbound_rules', [])
        for rule in outbound_rules:
            rule_info = {
                'name': rule.get('name'),
                'type': rule.get('type'),
                'destination': self._parse_destination(rule),
                'category': rule.get('category', 'user-defined'),
                'status': rule.get('status', 'Unknown')
            }
            self.network_config.outbound_rules.append(rule_info)
    
    def _analyze_customer_network(self, workspace_info: Dict):
        """Analyze customer-managed virtual network"""
        # Extract VNet information from private endpoint connections
        pe_connections = workspace_info.get('private_endpoint_connections', [])
        
        for pe_conn in pe_connections:
            private_endpoint = pe_conn.get('private_endpoint', {})
            if private_endpoint:
                pe_info = {
                    'id': private_endpoint.get('id'),
                    'provisioning_state': pe_conn.get('provisioning_state'),
                    'connection_state': pe_conn.get('private_link_service_connection_state', {})
                }
                self.network_config.private_endpoints.append(pe_info)
    
    def _analyze_private_endpoints(self):
        """Analyze private endpoints connected to the workspace"""
        try:
            # List private endpoints in the resource group
            cmd = ['az', 'network', 'private-endpoint', 'list',
                   '--resource-group', self.resource_group,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                all_endpoints = json.loads(result.stdout)
                
                # Build workspace resource ID pattern for filtering
                workspace_pattern = f"/workspaces/{self.workspace_name}"
                
                for endpoint in all_endpoints:
                    connections = endpoint.get('privateLinkServiceConnections', [])
                    for conn in connections:
                        service_id = conn.get('privateLinkServiceId', '')
                        if workspace_pattern.lower() in service_id.lower():
                            endpoint_info = {
                                'name': endpoint.get('name'),
                                'location': endpoint.get('location'),
                                'subnet': endpoint.get('subnet', {}).get('id'),
                                'network_interfaces': [ni.get('id') for ni in endpoint.get('networkInterfaces', [])],
                                'provisioning_state': endpoint.get('provisioningState'),
                                'connection_state': conn.get('privateLinkServiceConnectionState', {})
                            }
                            # Avoid duplicates
                            if not any(pe['name'] == endpoint_info['name'] for pe in self.network_config.private_endpoints):
                                self.network_config.private_endpoints.append(endpoint_info)
                            
        except Exception as e:
            self.logger.warning(f"Failed to analyze private endpoints: {str(e)}")
    
    def _analyze_outbound_rules(self):
        """Analyze outbound rules for managed networks"""
        if self.network_config.network_type != "managed":
            return
            
        try:
            # List outbound rules using Azure ML CLI
            cmd = ['az', 'ml', 'workspace', 'outbound-rule', 'list',
                   '--workspace-name', self.workspace_name,
                   '--resource-group', self.resource_group,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                rules = json.loads(result.stdout)
                
                for rule in rules:
                    rule_info = {
                        'name': rule.get('name'),
                        'type': rule.get('type'),
                        'destination': self._parse_destination(rule),
                        'status': rule.get('status'),
                        'category': rule.get('category', 'user-defined')
                    }
                    
                    # Avoid duplicates from workspace info
                    if not any(r['name'] == rule_info['name'] for r in self.network_config.outbound_rules):
                        self.network_config.outbound_rules.append(rule_info)
                        
        except Exception as e:
            self.logger.warning(f"Failed to analyze outbound rules: {str(e)}")
    
    def _parse_destination(self, rule: Dict) -> str:
        """Parse destination from outbound rule"""
        rule_type = rule.get('type', '').lower()
        
        if rule_type == 'fqdn':
            return rule.get('destination', '')
        elif rule_type == 'service_tag':
            dest = rule.get('destination', {})
            if isinstance(dest, dict):
                service_tag = dest.get('service_tag', '')
                port_ranges = dest.get('port_ranges', 'Any')
                return f"{service_tag} (Ports: {port_ranges})"
            else:
                return str(dest)
        elif rule_type == 'private_endpoint':
            dest = rule.get('destination', {})
            if isinstance(dest, dict):
                service_resource_id = dest.get('service_resource_id', '')
                return service_resource_id.split('/')[-1] if service_resource_id else 'Unknown'
            else:
                return str(dest)
        else:
            return str(rule.get('destination', ''))
    
    def _format_network_data(self) -> Dict:
        """Format network configuration data for output"""
        return {
            'network_type': self.network_config.network_type,
            'isolation_mode': self.network_config.isolation_mode,
            'public_network_access': self.network_config.public_network_access,
            'private_endpoints': {
                'count': len(self.network_config.private_endpoints),
                'endpoints': self.network_config.private_endpoints
            },
            'outbound_rules': {
                'count': len(self.network_config.outbound_rules),
                'rules': self._categorize_outbound_rules()
            },
            'virtual_network': self.network_config.virtual_network,
            'subnets': self.network_config.subnets,
            'summary': self.generate_network_summary()
        }
    
    def _categorize_outbound_rules(self) -> Dict:
        """Categorize outbound rules by type"""
        categorized = {
            'fqdn': [],
            'service_tag': [],
            'private_endpoint': [],
            'required': []
        }
        
        for rule in self.network_config.outbound_rules:
            rule_type = rule.get('type', '').lower()
            category = rule.get('category', 'user-defined')
            
            if category == 'required':
                categorized['required'].append(rule)
            elif rule_type in categorized:
                categorized[rule_type].append(rule)
            else:
                # Handle unknown types
                if 'other' not in categorized:
                    categorized['other'] = []
                categorized['other'].append(rule)
                
        return categorized
    
    def generate_network_summary(self) -> Dict:
        """Generate a summary of network configuration"""
        summary = {
            'configuration_type': self.network_config.network_type,
            'security_level': self._assess_security_level(),
            'connectivity': {
                'inbound': self._analyze_inbound_connectivity(),
                'outbound': self._analyze_outbound_connectivity()
            },
            'key_findings': self._identify_key_findings(),
            'recommendations': self._generate_recommendations()
        }
        
        return summary
    
    def _assess_security_level(self) -> str:
        """Assess overall security level"""
        if not self.network_config.public_network_access:
            if self.network_config.isolation_mode == 'allow_only_approved_outbound':
                return "High - Private with approved outbound only"
            elif self.network_config.isolation_mode == 'allow_internet_outbound':
                return "Medium - Private with internet outbound"
            else:
                return "Medium - Private access only"
        else:
            return "Low - Public access enabled"
    
    def _analyze_inbound_connectivity(self) -> Dict:
        """Analyze inbound connectivity options"""
        return {
            'public_access': self.network_config.public_network_access,
            'private_endpoints': len(self.network_config.private_endpoints),
            'service_endpoints': len(self.network_config.service_endpoints)
        }
    
    def _analyze_outbound_connectivity(self) -> Dict:
        """Analyze outbound connectivity rules"""
        rules_by_type = {}
        for rule in self.network_config.outbound_rules:
            rule_type = rule.get('type', 'unknown')
            rules_by_type[rule_type] = rules_by_type.get(rule_type, 0) + 1
            
        return rules_by_type
    
    def _identify_key_findings(self) -> List[str]:
        """Identify key findings from the analysis"""
        findings = []
        
        if self.network_config.public_network_access:
            findings.append("⚠️ Public network access is enabled")
        else:
            findings.append("✅ Public network access is disabled")
            
        if not self.network_config.private_endpoints:
            findings.append("ℹ️ No private endpoints configured")
        else:
            findings.append(f"✅ {len(self.network_config.private_endpoints)} private endpoint(s) configured")
            
        if self.network_config.isolation_mode == 'allow_only_approved_outbound':
            findings.append("✅ Strict outbound control enabled")
        elif self.network_config.isolation_mode == 'allow_internet_outbound':
            findings.append("⚠️ Internet outbound access allowed")
            
        if self.network_config.network_type == "managed":
            findings.append(f"ℹ️ Managed VNet with {len(self.network_config.outbound_rules)} outbound rule(s)")
        elif self.network_config.network_type == "customer":
            findings.append("ℹ️ Customer-managed VNet configuration")
        else:
            findings.append("ℹ️ No special network configuration detected")
            
        return findings
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if self.network_config.public_network_access:
            recommendations.append("Consider disabling public network access for enhanced security")
            
        if not self.network_config.private_endpoints and self.network_config.network_type != "managed":
            recommendations.append("Consider adding private endpoints for secure access")
            
        if self.network_config.isolation_mode == 'allow_internet_outbound':
            recommendations.append("Consider switching to 'allow_only_approved_outbound' for stricter control")
            
        if self.network_config.network_type == "none":
            recommendations.append("Consider implementing network isolation for better security")
            
        return recommendations 