from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from .base_analyzer import BaseAnalyzer, AnalysisResult
import json
import subprocess

@dataclass
class ConnectedResource:
    """Represents a connected Azure resource"""
    resource_id: str
    resource_type: str
    name: str
    resource_group: str
    connection_type: str  # 'default', 'associated', 'user-defined'
    access_method: str    # 'private-endpoint', 'service-endpoint', 'public'
    private_endpoints: List[Dict] = field(default_factory=list)
    public_access_enabled: bool = True
    firewall_rules: List[Dict] = field(default_factory=list)
    network_acls: Dict = field(default_factory=dict)
    
    def get_security_score(self) -> int:
        """Calculate security score (0-100)"""
        score = 100
        
        if self.public_access_enabled:
            score -= 30
        if self.access_method == 'public':
            score -= 20
        if not self.private_endpoints:
            score -= 10
        if not self.firewall_rules:
            score -= 10
            
        return max(0, score)

class ResourceDiscovery(BaseAnalyzer):
    """Discovers and analyzes connected resources"""
    
    def __init__(self, workspace_name: str, resource_group: str,
                 subscription_id: Optional[str] = None, hub_type: str = 'azure-ml'):
        super().__init__(workspace_name, resource_group, subscription_id, hub_type)
        self.connected_resources: List[ConnectedResource] = []
        self.resource_graph: Dict[str, List[str]] = {}
        
    def analyze(self) -> AnalysisResult:
        """Discover and analyze all connected resources"""
        try:
            # Get workspace configuration
            workspace_info = self._get_workspace_info()
            
            # Discover default resources
            self._discover_default_resources(workspace_info)
            
            # Discover associated resources
            self._discover_associated_resources(workspace_info)
            
            # Discover user connections (AI Foundry specific)
            if self.hub_type == 'azure-ai-foundry':
                self._discover_user_connections()
            
            # Analyze each resource
            for resource in self.connected_resources:
                self._analyze_resource(resource)
            
            # Build resource dependency graph
            self._build_dependency_graph()
            
            return AnalysisResult(
                success=True,
                message="Resource discovery completed successfully",
                data=self._format_discovery_results()
            )
            
        except Exception as e:
            self.logger.error(f"Resource discovery failed: {str(e)}")
            return AnalysisResult(
                success=False,
                message=f"Resource discovery failed: {str(e)}",
                error=str(e)
            )
    
    def _get_workspace_info(self) -> Dict:
        """Get workspace information"""
        try:
            cmd = ['az', 'ml', 'workspace', 'show',
                   '--name', self.workspace_name,
                   '--resource-group', self.resource_group,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                raise RuntimeError(f"Failed to get workspace info: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"Failed to get workspace info: {str(e)}")
            raise
    
    def _discover_default_resources(self, workspace_info: Dict):
        """Discover default workspace resources"""
        # Storage account
        storage_account = workspace_info.get('storage_account')
        if storage_account:
            self._add_resource(
                resource_id=storage_account,
                resource_type='Microsoft.Storage/storageAccounts',
                connection_type='default'
            )
        
        # Key Vault
        key_vault = workspace_info.get('key_vault')
        if key_vault:
            self._add_resource(
                resource_id=key_vault,
                resource_type='Microsoft.KeyVault/vaults',
                connection_type='default'
            )
        
        # Container Registry
        container_registry = workspace_info.get('container_registry')
        if container_registry:
            self._add_resource(
                resource_id=container_registry,
                resource_type='Microsoft.ContainerRegistry/registries',
                connection_type='default'
            )
        
        # Application Insights
        app_insights = workspace_info.get('application_insights')
        if app_insights:
            self._add_resource(
                resource_id=app_insights,
                resource_type='Microsoft.Insights/components',
                connection_type='default'
            )
    
    def _discover_associated_resources(self, workspace_info: Dict):
        """Discover associated resources (compute, datastores, etc.)"""
        # Discover compute resources
        self._discover_compute_resources()
        
        # Discover datastores
        self._discover_datastores()
        
        # Discover linked services (for AI Foundry)
        if self.hub_type == 'azure-ai-foundry':
            self._discover_linked_services()
    
    def _discover_compute_resources(self):
        """Discover compute resources"""
        try:
            cmd = ['az', 'ml', 'compute', 'list',
                   '--workspace-name', self.workspace_name,
                   '--resource-group', self.resource_group,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                computes = json.loads(result.stdout)
                
                for compute in computes:
                    compute_type = compute.get('type', '').lower()
                    
                    # Handle different compute types
                    if compute_type == 'computeinstance':
                        self._add_compute_instance(compute)
                    elif compute_type == 'amlcompute':
                        self._add_compute_cluster(compute)
                    elif compute_type == 'kubernetes':
                        self._add_kubernetes_compute(compute)
                        
        except Exception as e:
            self.logger.warning(f"Failed to discover compute resources: {str(e)}")
    
    def _discover_datastores(self):
        """Discover connected datastores"""
        try:
            cmd = ['az', 'ml', 'datastore', 'list',
                   '--workspace-name', self.workspace_name,
                   '--resource-group', self.resource_group,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                datastores = json.loads(result.stdout)
                
                for datastore in datastores:
                    datastore_type = datastore.get('type', '').lower()
                    
                    if datastore_type == 'azure_blob':
                        account_name = datastore.get('account_name')
                        if account_name:
                            # Construct storage account resource ID
                            resource_id = f"/subscriptions/{self.subscription_id or 'unknown'}/resourceGroups/*/providers/Microsoft.Storage/storageAccounts/{account_name}"
                            self._add_resource(
                                resource_id=resource_id,
                                resource_type='Microsoft.Storage/storageAccounts',
                                connection_type='user-defined'
                            )
                            
        except Exception as e:
            self.logger.warning(f"Failed to discover datastores: {str(e)}")
    
    def _discover_user_connections(self):
        """Discover user-defined connections (AI Foundry specific)"""
        try:
            # Use AI Foundry specific API
            cmd = ['az', 'ml', 'connection', 'list',
                   '--workspace-name', self.workspace_name,
                   '--resource-group', self.resource_group,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                connections = json.loads(result.stdout)
                
                for conn in connections:
                    conn_type = conn.get('type', '').lower()
                    
                    # Handle different connection types
                    if conn_type == 'azure_openai':
                        self._add_azure_openai_connection(conn)
                    elif conn_type == 'cognitive_services':
                        self._add_cognitive_services_connection(conn)
                    elif conn_type == 'custom':
                        self._add_custom_connection(conn)
                        
        except Exception as e:
            self.logger.warning(f"Failed to discover user connections: {str(e)}")
    
    def _discover_linked_services(self):
        """Discover linked services for AI Foundry"""
        # This is a placeholder for AI Foundry specific linked services
        # Implementation would depend on specific AI Foundry APIs
        pass
    
    def _add_resource(self, resource_id: str, resource_type: str, 
                     connection_type: str):
        """Add a discovered resource"""
        # Extract resource details from ID
        parts = resource_id.split('/')
        
        if len(parts) >= 9:
            resource = ConnectedResource(
                resource_id=resource_id,
                resource_type=resource_type,
                name=parts[-1],
                resource_group=parts[4] if len(parts) > 4 else self.resource_group,
                connection_type=connection_type,
                access_method='unknown'
            )
            
            # Avoid duplicates
            if not any(r.resource_id == resource_id for r in self.connected_resources):
                self.connected_resources.append(resource)
    
    def _add_compute_instance(self, compute: Dict):
        """Add compute instance details"""
        properties = compute.get('properties', {})
        
        # Compute instances have associated resources
        subnet = properties.get('properties', {}).get('subnet', {})
        if subnet.get('id'):
            # Add the VNet as a connected resource
            vnet_id = '/'.join(subnet['id'].split('/')[:-2])
            self._add_resource(
                resource_id=vnet_id,
                resource_type='Microsoft.Network/virtualNetworks',
                connection_type='associated'
            )

    def _add_compute_cluster(self, compute: Dict):
        """Add compute cluster details"""
        properties = compute.get('properties', {})
        
        # Similar to compute instance
        subnet = properties.get('properties', {}).get('subnet', {})
        if subnet.get('id'):
            vnet_id = '/'.join(subnet['id'].split('/')[:-2])
            self._add_resource(
                resource_id=vnet_id,
                resource_type='Microsoft.Network/virtualNetworks',
                connection_type='associated'
            )

    def _add_kubernetes_compute(self, compute: Dict):
        """Add Kubernetes compute details"""
        properties = compute.get('properties', {})
        
        # Kubernetes attachments reference external AKS clusters
        resource_id = properties.get('resourceId')
        if resource_id:
            self._add_resource(
                resource_id=resource_id,
                resource_type='Microsoft.ContainerService/managedClusters',
                connection_type='associated'
            )
    
    def _add_azure_openai_connection(self, conn: Dict):
        """Add Azure OpenAI connection"""
        target = conn.get('target')
        if target:
            # Extract service name from endpoint
            if '://' in target:
                domain = target.split('://')[1].split('/')[0]
                service_name = domain.split('.')[0]
                
                resource_id = f"/subscriptions/{self.subscription_id or 'unknown'}/resourceGroups/*/providers/Microsoft.CognitiveServices/accounts/{service_name}"
                self._add_resource(
                    resource_id=resource_id,
                    resource_type='Microsoft.CognitiveServices/accounts',
                    connection_type='user-defined'
                )
    
    def _add_cognitive_services_connection(self, conn: Dict):
        """Add Cognitive Services connection"""
        target = conn.get('target')
        if target:
            # Similar to Azure OpenAI
            if '://' in target:
                domain = target.split('://')[1].split('/')[0]
                service_name = domain.split('.')[0]
                
                resource_id = f"/subscriptions/{self.subscription_id or 'unknown'}/resourceGroups/*/providers/Microsoft.CognitiveServices/accounts/{service_name}"
                self._add_resource(
                    resource_id=resource_id,
                    resource_type='Microsoft.CognitiveServices/accounts',
                    connection_type='user-defined'
                )
    
    def _add_custom_connection(self, conn: Dict):
        """Add custom connection"""
        # Custom connections may point to various Azure services
        # This is a placeholder for custom connection analysis
        pass
    
    def _analyze_resource(self, resource: ConnectedResource):
        """Analyze a specific resource for connectivity details"""
        analyzers = {
            'Microsoft.Storage/storageAccounts': self._analyze_storage_account,
            'Microsoft.KeyVault/vaults': self._analyze_key_vault,
            'Microsoft.ContainerRegistry/registries': self._analyze_container_registry,
            'Microsoft.CognitiveServices/accounts': self._analyze_cognitive_services
        }
        
        analyzer = analyzers.get(resource.resource_type)
        if analyzer:
            analyzer(resource)
    
    def _analyze_storage_account(self, resource: ConnectedResource):
        """Analyze storage account connectivity"""
        try:
            # Get storage account details
            cmd = ['az', 'storage', 'account', 'show',
                   '--name', resource.name,
                   '--resource-group', resource.resource_group,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                storage_info = json.loads(result.stdout)
                
                # Check public access
                resource.public_access_enabled = (
                    storage_info.get('publicNetworkAccess', 'Enabled') == 'Enabled'
                )
                
                # Check private endpoints
                private_endpoints = storage_info.get('privateEndpointConnections', [])
                for pe in private_endpoints:
                    resource.private_endpoints.append({
                        'name': pe.get('name'),
                        'state': pe.get('privateLinkServiceConnectionState', {}).get('status')
                    })
                
                # Check firewall rules
                network_acls = storage_info.get('networkAcls', {})
                resource.network_acls = network_acls
                
                # Determine access method
                if resource.private_endpoints:
                    resource.access_method = 'private-endpoint'
                elif not resource.public_access_enabled:
                    resource.access_method = 'service-endpoint'
                else:
                    resource.access_method = 'public'
                    
        except Exception as e:
            self.logger.warning(f"Failed to analyze storage account {resource.name}: {str(e)}")
    
    def _analyze_key_vault(self, resource: ConnectedResource):
        """Analyze Key Vault connectivity"""
        try:
            cmd = ['az', 'keyvault', 'show',
                   '--name', resource.name,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                kv_info = json.loads(result.stdout)
                
                # Check public access
                resource.public_access_enabled = (
                    kv_info.get('properties', {}).get('publicNetworkAccess', 'Enabled') == 'Enabled'
                )
                
                # Check private endpoints
                private_endpoints = kv_info.get('properties', {}).get('privateEndpointConnections', [])
                for pe in private_endpoints:
                    resource.private_endpoints.append({
                        'name': pe.get('name'),
                        'state': pe.get('properties', {}).get('privateLinkServiceConnectionState', {}).get('status')
                    })
                
                # Get network ACLs
                cmd_network = ['az', 'keyvault', 'network-rule', 'list',
                              '--name', resource.name,
                              '--output', 'json']
                
                if self.subscription_id:
                    cmd_network.extend(['--subscription', self.subscription_id])
                    
                result_network = subprocess.run(cmd_network, capture_output=True, text=True, timeout=30)
                if result_network.returncode == 0:
                    resource.network_acls = json.loads(result_network.stdout)
                    
                # Determine access method
                if resource.private_endpoints:
                    resource.access_method = 'private-endpoint'
                elif not resource.public_access_enabled:
                    resource.access_method = 'service-endpoint'
                else:
                    resource.access_method = 'public'
                    
        except Exception as e:
            self.logger.warning(f"Failed to analyze key vault {resource.name}: {str(e)}")
    
    def _analyze_container_registry(self, resource: ConnectedResource):
        """Analyze Container Registry connectivity"""
        try:
            cmd = ['az', 'acr', 'show',
                   '--name', resource.name,
                   '--resource-group', resource.resource_group,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                acr_info = json.loads(result.stdout)
                
                # Check public access
                resource.public_access_enabled = (
                    acr_info.get('publicNetworkAccess', 'Enabled') == 'Enabled'
                )
                
                # Check private endpoints
                private_endpoints = acr_info.get('privateEndpointConnections', [])
                for pe in private_endpoints:
                    resource.private_endpoints.append({
                        'name': pe.get('name'),
                        'state': pe.get('privateLinkServiceConnectionState', {}).get('status')
                    })
                
                # Determine access method
                if resource.private_endpoints:
                    resource.access_method = 'private-endpoint'
                elif not resource.public_access_enabled:
                    resource.access_method = 'service-endpoint'
                else:
                    resource.access_method = 'public'
                    
        except Exception as e:
            self.logger.warning(f"Failed to analyze container registry {resource.name}: {str(e)}")
    
    def _analyze_cognitive_services(self, resource: ConnectedResource):
        """Analyze Cognitive Services connectivity"""
        try:
            cmd = ['az', 'cognitiveservices', 'account', 'show',
                   '--name', resource.name,
                   '--resource-group', resource.resource_group,
                   '--output', 'json']
            
            if self.subscription_id:
                cmd.extend(['--subscription', self.subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                cs_info = json.loads(result.stdout)
                
                # Check public access
                resource.public_access_enabled = (
                    cs_info.get('properties', {}).get('publicNetworkAccess', 'Enabled') == 'Enabled'
                )
                
                # Check private endpoints
                private_endpoints = cs_info.get('properties', {}).get('privateEndpointConnections', [])
                for pe in private_endpoints:
                    resource.private_endpoints.append({
                        'name': pe.get('name'),
                        'state': pe.get('properties', {}).get('privateLinkServiceConnectionState', {}).get('status')
                    })
                
                # Determine access method
                if resource.private_endpoints:
                    resource.access_method = 'private-endpoint'
                elif not resource.public_access_enabled:
                    resource.access_method = 'service-endpoint'
                else:
                    resource.access_method = 'public'
                    
        except Exception as e:
            self.logger.warning(f"Failed to analyze cognitive services {resource.name}: {str(e)}")
    
    def _build_dependency_graph(self):
        """Build resource dependency graph"""
        # This creates a graph showing which resources depend on others
        for resource in self.connected_resources:
            self.resource_graph[resource.resource_id] = []
            
            # Add dependencies based on resource type
            if resource.resource_type == 'Microsoft.MachineLearningServices/workspaces/computes':
                # Compute depends on VNet, Storage
                storage_resources = [r.resource_id for r in self.connected_resources 
                                   if r.resource_type == 'Microsoft.Storage/storageAccounts']
                self.resource_graph[resource.resource_id].extend(storage_resources)
    
    def _format_discovery_results(self) -> Dict:
        """Format discovery results for output"""
        resources_by_type = {}
        
        for resource in self.connected_resources:
            resource_type = resource.resource_type.split('/')[-1]
            if resource_type not in resources_by_type:
                resources_by_type[resource_type] = []
                
            resources_by_type[resource_type].append({
                'name': resource.name,
                'resource_group': resource.resource_group,
                'connection_type': resource.connection_type,
                'access_method': resource.access_method,
                'public_access': resource.public_access_enabled,
                'security_score': resource.get_security_score(),
                'private_endpoints': len(resource.private_endpoints)
            })
        
        return {
            'total_resources': len(self.connected_resources),
            'resources_by_type': resources_by_type,
            'security_summary': self._generate_security_summary(),
            'dependency_graph': self.resource_graph
        }
    
    def _generate_security_summary(self) -> Dict:
        """Generate security summary for all resources"""
        total_resources = len(self.connected_resources)
        public_accessible = sum(1 for r in self.connected_resources if r.public_access_enabled)
        private_endpoint_protected = sum(1 for r in self.connected_resources if r.private_endpoints)
        
        avg_security_score = sum(r.get_security_score() for r in self.connected_resources) / total_resources if total_resources > 0 else 0
        
        return {
            'total_resources': total_resources,
            'public_accessible': public_accessible,
            'private_endpoint_protected': private_endpoint_protected,
            'average_security_score': round(avg_security_score, 1),
            'recommendations': self._generate_resource_recommendations()
        }
    
    def _generate_resource_recommendations(self) -> List[str]:
        """Generate recommendations for connected resources"""
        recommendations = []
        
        # Check for public access
        public_resources = [r for r in self.connected_resources if r.public_access_enabled]
        if public_resources:
            recommendations.append(
                f"Consider disabling public access for {len(public_resources)} resources"
            )
        
        # Check for missing private endpoints
        no_pe_resources = [r for r in self.connected_resources 
                          if not r.private_endpoints and r.connection_type == 'default']
        if no_pe_resources:
            recommendations.append(
                f"Consider adding private endpoints to {len(no_pe_resources)} default resources"
            )
        
        return recommendations 