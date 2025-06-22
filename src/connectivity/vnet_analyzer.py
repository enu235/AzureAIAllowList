from typing import Dict, List, Optional
import json
import subprocess
import logging

class VNetAnalyzer:
    """Analyzes Virtual Network configurations"""
    
    def __init__(self, resource_group: str, subscription_id: Optional[str] = None):
        self.resource_group = resource_group
        self.subscription_id = subscription_id
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def analyze_workspace_vnet(self, workspace_info: Dict) -> Dict:
        """Analyze VNet associated with workspace"""
        vnet_info = {
            'vnets': [],
            'subnets': [],
            'network_security_groups': [],
            'route_tables': [],
            'analysis_summary': {}
        }
        
        try:
            # Extract subnet information from private endpoints
            subnet_ids = self._extract_subnet_ids(workspace_info)
            
            # Get VNet information for each subnet
            for subnet_id in subnet_ids:
                subnet_info = self._get_subnet_info(subnet_id)
                if subnet_info:
                    vnet_info['subnets'].append(subnet_info)
                    
                    # Get VNet details
                    vnet_details = self._get_vnet_details(subnet_id)
                    if vnet_details and not any(v['id'] == vnet_details['id'] for v in vnet_info['vnets']):
                        vnet_info['vnets'].append(vnet_details)
            
            # Analyze network security groups
            vnet_info['network_security_groups'] = self.analyze_network_security_groups(subnet_ids)
            
            # Analyze route tables
            vnet_info['route_tables'] = self._analyze_route_tables(subnet_ids)
            
            # Generate analysis summary
            vnet_info['analysis_summary'] = self._generate_vnet_summary(vnet_info)
            
        except Exception as e:
            self.logger.error(f"VNet analysis failed: {str(e)}")
            vnet_info['analysis_summary'] = {
                'error': f"Analysis failed: {str(e)}",
                'status': 'failed'
            }
            
        return vnet_info
    
    def _extract_subnet_ids(self, workspace_info: Dict) -> List[str]:
        """Extract subnet IDs from workspace information"""
        subnet_ids = set()
        
        # Extract from private endpoint connections
        pe_connections = workspace_info.get('private_endpoint_connections', [])
        for pe_conn in pe_connections:
            private_endpoint = pe_conn.get('private_endpoint', {})
            pe_id = private_endpoint.get('id', '')
            if pe_id:
                # Get private endpoint details to extract subnet
                pe_details = self._get_private_endpoint_details(pe_id)
                if pe_details:
                    subnet = pe_details.get('subnet', {})
                    subnet_id = subnet.get('id')
                    if subnet_id:
                        subnet_ids.add(subnet_id)
        
        return list(subnet_ids)
    
    def _get_private_endpoint_details(self, pe_id: str) -> Optional[Dict]:
        """Get private endpoint details"""
        try:
            # Extract resource group and name from the ID
            parts = pe_id.split('/')
            if len(parts) >= 9:
                pe_rg = parts[4]
                pe_name = parts[8]
                
                cmd = ['az', 'network', 'private-endpoint', 'show',
                       '--resource-group', pe_rg,
                       '--name', pe_name,
                       '--output', 'json']
                
                if self.subscription_id:
                    cmd.extend(['--subscription', self.subscription_id])
                    
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    return json.loads(result.stdout)
                    
        except Exception as e:
            self.logger.debug(f"Failed to get private endpoint details: {str(e)}")
        
        return None
    
    def _get_subnet_info(self, subnet_id: str) -> Optional[Dict]:
        """Get subnet information"""
        try:
            # Parse subnet ID to extract components
            parts = subnet_id.split('/')
            if len(parts) >= 11:
                subnet_rg = parts[4]
                vnet_name = parts[8]
                subnet_name = parts[10]
                
                cmd = ['az', 'network', 'vnet', 'subnet', 'show',
                       '--resource-group', subnet_rg,
                       '--vnet-name', vnet_name,
                       '--name', subnet_name,
                       '--output', 'json']
                
                if self.subscription_id:
                    cmd.extend(['--subscription', self.subscription_id])
                    
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    subnet_data = json.loads(result.stdout)
                    return {
                        'id': subnet_data.get('id'),
                        'name': subnet_data.get('name'),
                        'address_prefix': subnet_data.get('addressPrefix'),
                        'resource_group': subnet_rg,
                        'vnet_name': vnet_name,
                        'network_security_group': subnet_data.get('networkSecurityGroup'),
                        'route_table': subnet_data.get('routeTable'),
                        'service_endpoints': subnet_data.get('serviceEndpoints', []),
                        'private_endpoint_network_policies': subnet_data.get('privateEndpointNetworkPolicies'),
                        'private_link_service_network_policies': subnet_data.get('privateLinkServiceNetworkPolicies')
                    }
                    
        except Exception as e:
            self.logger.debug(f"Failed to get subnet info: {str(e)}")
        
        return None
    
    def _get_vnet_details(self, subnet_id: str) -> Optional[Dict]:
        """Get VNet details from subnet ID"""
        try:
            # Parse subnet ID to extract VNet components
            parts = subnet_id.split('/')
            if len(parts) >= 9:
                vnet_rg = parts[4]
                vnet_name = parts[8]
                
                cmd = ['az', 'network', 'vnet', 'show',
                       '--resource-group', vnet_rg,
                       '--name', vnet_name,
                       '--output', 'json']
                
                if self.subscription_id:
                    cmd.extend(['--subscription', self.subscription_id])
                    
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    vnet_data = json.loads(result.stdout)
                    return {
                        'id': vnet_data.get('id'),
                        'name': vnet_data.get('name'),
                        'resource_group': vnet_rg,
                        'location': vnet_data.get('location'),
                        'address_space': vnet_data.get('addressSpace', {}).get('addressPrefixes', []),
                        'dns_servers': vnet_data.get('dhcpOptions', {}).get('dnsServers', []),
                        'subnets_count': len(vnet_data.get('subnets', [])),
                        'enable_ddos_protection': vnet_data.get('enableDdosProtection', False),
                        'enable_vm_protection': vnet_data.get('enableVmProtection', False)
                    }
                    
        except Exception as e:
            self.logger.debug(f"Failed to get VNet details: {str(e)}")
        
        return None
    
    def analyze_network_security_groups(self, subnet_ids: List[str]) -> List[Dict]:
        """Analyze NSGs associated with subnets"""
        nsgs = []
        processed_nsgs = set()
        
        for subnet_id in subnet_ids:
            try:
                subnet_info = self._get_subnet_info(subnet_id)
                if subnet_info and subnet_info.get('network_security_group'):
                    nsg_id = subnet_info['network_security_group']['id']
                    
                    # Avoid processing the same NSG multiple times
                    if nsg_id not in processed_nsgs:
                        processed_nsgs.add(nsg_id)
                        nsg_details = self._get_nsg_details(nsg_id)
                        if nsg_details:
                            nsgs.append(nsg_details)
                            
            except Exception as e:
                self.logger.debug(f"Failed to analyze NSG for subnet {subnet_id}: {str(e)}")
                
        return nsgs
    
    def _get_nsg_details(self, nsg_id: str) -> Optional[Dict]:
        """Get NSG rules and configuration"""
        try:
            parts = nsg_id.split('/')
            if len(parts) >= 9:
                nsg_rg = parts[4]
                nsg_name = parts[8]
                
                cmd = ['az', 'network', 'nsg', 'show',
                       '--resource-group', nsg_rg,
                       '--name', nsg_name,
                       '--output', 'json']
                
                if self.subscription_id:
                    cmd.extend(['--subscription', self.subscription_id])
                    
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    nsg_data = json.loads(result.stdout)
                    
                    # Extract and analyze relevant rules
                    return {
                        'id': nsg_data.get('id'),
                        'name': nsg_data.get('name'),
                        'resource_group': nsg_rg,
                        'location': nsg_data.get('location'),
                        'security_rules': self._format_nsg_rules(nsg_data.get('securityRules', [])),
                        'default_security_rules': self._format_nsg_rules(nsg_data.get('defaultSecurityRules', [])),
                        'rules_summary': self._analyze_nsg_rules(nsg_data.get('securityRules', []))
                    }
                    
        except Exception as e:
            self.logger.debug(f"Failed to get NSG details: {str(e)}")
            
        return None
    
    def _format_nsg_rules(self, rules: List[Dict]) -> List[Dict]:
        """Format NSG rules for readability"""
        formatted_rules = []
        
        for rule in rules:
            formatted_rules.append({
                'name': rule.get('name'),
                'priority': rule.get('priority'),
                'direction': rule.get('direction'),
                'access': rule.get('access'),
                'protocol': rule.get('protocol'),
                'source': f"{rule.get('sourceAddressPrefix', '*')}:{rule.get('sourcePortRange', '*')}",
                'destination': f"{rule.get('destinationAddressPrefix', '*')}:{rule.get('destinationPortRange', '*')}",
                'description': rule.get('description', '')
            })
            
        return sorted(formatted_rules, key=lambda x: x.get('priority', 65535))
    
    def _analyze_nsg_rules(self, rules: List[Dict]) -> Dict:
        """Analyze NSG rules for security insights"""
        analysis = {
            'total_rules': len(rules),
            'allow_rules': 0,
            'deny_rules': 0,
            'inbound_rules': 0,
            'outbound_rules': 0,
            'high_risk_rules': [],
            'open_ports': []
        }
        
        for rule in rules:
            access = rule.get('access', '').lower()
            direction = rule.get('direction', '').lower()
            
            if access == 'allow':
                analysis['allow_rules'] += 1
            elif access == 'deny':
                analysis['deny_rules'] += 1
            
            if direction == 'inbound':
                analysis['inbound_rules'] += 1
            elif direction == 'outbound':
                analysis['outbound_rules'] += 1
                
            # Check for high-risk rules
            if (access == 'allow' and 
                rule.get('sourceAddressPrefix') in ['*', '0.0.0.0/0', 'Internet'] and
                direction == 'inbound'):
                analysis['high_risk_rules'].append({
                    'name': rule.get('name'),
                    'risk': 'Open to Internet',
                    'port': rule.get('destinationPortRange')
                })
                
                # Track open ports
                port_range = rule.get('destinationPortRange', '*')
                if port_range != '*':
                    analysis['open_ports'].append(port_range)
        
        return analysis
    
    def _analyze_route_tables(self, subnet_ids: List[str]) -> List[Dict]:
        """Analyze route tables associated with subnets"""
        route_tables = []
        processed_rts = set()
        
        for subnet_id in subnet_ids:
            try:
                subnet_info = self._get_subnet_info(subnet_id)
                if subnet_info and subnet_info.get('route_table'):
                    rt_id = subnet_info['route_table']['id']
                    
                    # Avoid processing the same route table multiple times
                    if rt_id not in processed_rts:
                        processed_rts.add(rt_id)
                        rt_details = self._get_route_table_details(rt_id)
                        if rt_details:
                            route_tables.append(rt_details)
                            
            except Exception as e:
                self.logger.debug(f"Failed to analyze route table for subnet {subnet_id}: {str(e)}")
                
        return route_tables
    
    def _get_route_table_details(self, rt_id: str) -> Optional[Dict]:
        """Get route table details"""
        try:
            parts = rt_id.split('/')
            if len(parts) >= 9:
                rt_rg = parts[4]
                rt_name = parts[8]
                
                cmd = ['az', 'network', 'route-table', 'show',
                       '--resource-group', rt_rg,
                       '--name', rt_name,
                       '--output', 'json']
                
                if self.subscription_id:
                    cmd.extend(['--subscription', self.subscription_id])
                    
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    rt_data = json.loads(result.stdout)
                    
                    return {
                        'id': rt_data.get('id'),
                        'name': rt_data.get('name'),
                        'resource_group': rt_rg,
                        'location': rt_data.get('location'),
                        'routes': self._format_routes(rt_data.get('routes', [])),
                        'disable_bgp_route_propagation': rt_data.get('disableBgpRoutePropagation', False)
                    }
                    
        except Exception as e:
            self.logger.debug(f"Failed to get route table details: {str(e)}")
            
        return None
    
    def _format_routes(self, routes: List[Dict]) -> List[Dict]:
        """Format routes for readability"""
        formatted_routes = []
        
        for route in routes:
            formatted_routes.append({
                'name': route.get('name'),
                'address_prefix': route.get('addressPrefix'),
                'next_hop_type': route.get('nextHopType'),
                'next_hop_ip_address': route.get('nextHopIpAddress'),
                'provisioning_state': route.get('provisioningState')
            })
            
        return formatted_routes
    
    def _generate_vnet_summary(self, vnet_info: Dict) -> Dict:
        """Generate VNet analysis summary"""
        summary = {
            'status': 'completed',
            'vnets_analyzed': len(vnet_info['vnets']),
            'subnets_analyzed': len(vnet_info['subnets']),
            'nsgs_analyzed': len(vnet_info['network_security_groups']),
            'route_tables_analyzed': len(vnet_info['route_tables']),
            'security_insights': self._generate_security_insights(vnet_info),
            'recommendations': self._generate_vnet_recommendations(vnet_info)
        }
        
        return summary
    
    def _generate_security_insights(self, vnet_info: Dict) -> List[str]:
        """Generate security insights from VNet analysis"""
        insights = []
        
        # Analyze NSG rules
        high_risk_count = 0
        for nsg in vnet_info.get('network_security_groups', []):
            rules_summary = nsg.get('rules_summary', {})
            high_risk_rules = rules_summary.get('high_risk_rules', [])
            high_risk_count += len(high_risk_rules)
            
            if high_risk_rules:
                insights.append(f"⚠️ NSG '{nsg['name']}' has {len(high_risk_rules)} high-risk rule(s)")
        
        if high_risk_count == 0:
            insights.append("✅ No high-risk NSG rules detected")
        
        # Analyze service endpoints
        service_endpoints_count = 0
        for subnet in vnet_info.get('subnets', []):
            service_endpoints_count += len(subnet.get('service_endpoints', []))
        
        if service_endpoints_count > 0:
            insights.append(f"ℹ️ {service_endpoints_count} service endpoint(s) configured")
        
        return insights
    
    def _generate_vnet_recommendations(self, vnet_info: Dict) -> List[str]:
        """Generate VNet recommendations"""
        recommendations = []
        
        # Check for missing NSGs
        subnets_without_nsg = [s for s in vnet_info.get('subnets', []) if not s.get('network_security_group')]
        if subnets_without_nsg:
            recommendations.append(f"Consider adding NSGs to {len(subnets_without_nsg)} subnet(s) without network security groups")
        
        # Check for overly permissive rules
        for nsg in vnet_info.get('network_security_groups', []):
            rules_summary = nsg.get('rules_summary', {})
            if rules_summary.get('high_risk_rules', []):
                recommendations.append(f"Review high-risk rules in NSG '{nsg['name']}'")
        
        # Check for custom DNS
        for vnet in vnet_info.get('vnets', []):
            if not vnet.get('dns_servers'):
                recommendations.append(f"Consider configuring custom DNS servers for VNet '{vnet['name']}'")
        
        return recommendations 