from typing import Dict, List, Optional, Set
import ipaddress
import re

class NetworkUtils:
    """Utility functions for network analysis"""
    
    @staticmethod
    def categorize_ip_address(ip: str) -> str:
        """Categorize an IP address (public, private, etc.)"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check specific types first (order matters)
            if ip_obj.is_loopback:
                return "loopback"
            elif ip_obj.is_multicast:
                return "multicast"
            elif ip_obj.is_link_local:
                return "link_local"
            elif ip_obj.is_reserved:
                return "reserved"
            elif ip_obj.is_private:
                return "private"
            elif ip_obj.is_global:
                return "public"
            else:
                return "other"
        except ValueError:
            return "invalid"
    
    @staticmethod
    def analyze_cidr_overlap(cidrs: List[str]) -> List[Dict]:
        """Analyze CIDR blocks for overlaps"""
        overlaps = []
        networks = []
        
        # Convert to network objects
        for cidr in cidrs:
            try:
                networks.append(ipaddress.ip_network(cidr, strict=False))
            except ValueError:
                continue
                
        # Check for overlaps
        for i in range(len(networks)):
            for j in range(i + 1, len(networks)):
                if networks[i].overlaps(networks[j]):
                    overlap_type = "overlap"
                    if networks[i].subnet_of(networks[j]):
                        overlap_type = f"{networks[i]} is subnet of {networks[j]}"
                    elif networks[j].subnet_of(networks[i]):
                        overlap_type = f"{networks[j]} is subnet of {networks[i]}"
                    
                    overlaps.append({
                        'network1': str(networks[i]),
                        'network2': str(networks[j]),
                        'type': overlap_type
                    })
                    
        return overlaps
    
    @staticmethod
    def get_network_info(cidr: str) -> Dict:
        """Get detailed information about a CIDR block"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            return {
                'network': str(network),
                'network_address': str(network.network_address),
                'broadcast_address': str(network.broadcast_address),
                'netmask': str(network.netmask),
                'prefix_length': network.prefixlen,
                'num_addresses': network.num_addresses,
                'is_private': network.is_private,
                'is_global': network.is_global,
                'is_multicast': network.is_multicast,
                'address_type': NetworkUtils.categorize_ip_address(str(network.network_address))
            }
        except ValueError as e:
            return {
                'error': f"Invalid CIDR: {str(e)}",
                'network': cidr
            }
    
    @staticmethod
    def parse_service_tag(service_tag: str) -> Dict:
        """Parse Azure service tag information"""
        # Common service tags and their descriptions
        service_tags = {
            'AzureMachineLearning': 'Azure Machine Learning service',
            'Storage': 'Azure Storage service',
            'KeyVault': 'Azure Key Vault service',
            'ContainerRegistry': 'Azure Container Registry',
            'AzureActiveDirectory': 'Azure Active Directory',
            'AzureResourceManager': 'Azure Resource Manager',
            'AzureMonitor': 'Azure Monitor service',
            'BatchNodeManagement': 'Azure Batch node management',
            'AzureCloud': 'Azure Cloud public IP addresses',
            'Internet': 'Internet addresses',
            'VirtualNetwork': 'Virtual network address space',
            'AzureLoadBalancer': 'Azure Load Balancer health probes',
            'Sql': 'Azure SQL Database',
            'AzureCosmosDB': 'Azure Cosmos DB',
            'EventHub': 'Azure Event Hubs',
            'ServiceBus': 'Azure Service Bus',
            'AzureConnectors': 'Azure Logic Apps connectors',
            'PowerQueryOnline': 'Power Query Online service',
            'MicrosoftContainerRegistry': 'Microsoft Container Registry',
            'AzureFrontDoor': 'Azure Front Door service',
            'AzureTrafficManager': 'Azure Traffic Manager'
        }
        
        # Extract base tag and region if present
        base_tag = service_tag.split('.')[0]
        region = None
        
        if '.' in service_tag:
            parts = service_tag.split('.')
            if len(parts) > 1:
                region = parts[1]
        
        return {
            'tag': service_tag,
            'base_tag': base_tag,
            'service': service_tags.get(base_tag, base_tag),
            'regional': region is not None,
            'region': region,
            'description': service_tags.get(base_tag, f"Azure service: {base_tag}")
        }
    
    @staticmethod
    def identify_common_ports(port: int) -> Dict:
        """Identify common port usage"""
        common_ports = {
            20: {'name': 'FTP Data', 'protocol': 'TCP', 'risk': 'Medium'},
            21: {'name': 'FTP Control', 'protocol': 'TCP', 'risk': 'Medium'},
            22: {'name': 'SSH', 'protocol': 'TCP', 'risk': 'Medium'},
            23: {'name': 'Telnet', 'protocol': 'TCP', 'risk': 'High'},
            25: {'name': 'SMTP', 'protocol': 'TCP', 'risk': 'Medium'},
            53: {'name': 'DNS', 'protocol': 'TCP/UDP', 'risk': 'Low'},
            80: {'name': 'HTTP', 'protocol': 'TCP', 'risk': 'Medium'},
            110: {'name': 'POP3', 'protocol': 'TCP', 'risk': 'Medium'},
            143: {'name': 'IMAP', 'protocol': 'TCP', 'risk': 'Medium'},
            443: {'name': 'HTTPS', 'protocol': 'TCP', 'risk': 'Low'},
            445: {'name': 'SMB', 'protocol': 'TCP', 'risk': 'High'},
            993: {'name': 'IMAPS', 'protocol': 'TCP', 'risk': 'Low'},
            995: {'name': 'POP3S', 'protocol': 'TCP', 'risk': 'Low'},
            1433: {'name': 'SQL Server', 'protocol': 'TCP', 'risk': 'High'},
            1521: {'name': 'Oracle DB', 'protocol': 'TCP', 'risk': 'High'},
            3306: {'name': 'MySQL', 'protocol': 'TCP', 'risk': 'High'},
            3389: {'name': 'RDP', 'protocol': 'TCP', 'risk': 'High'},
            5432: {'name': 'PostgreSQL', 'protocol': 'TCP', 'risk': 'High'},
            5831: {'name': 'Azure ML', 'protocol': 'TCP', 'risk': 'Low'},
            5985: {'name': 'WinRM HTTP', 'protocol': 'TCP', 'risk': 'Medium'},
            5986: {'name': 'WinRM HTTPS', 'protocol': 'TCP', 'risk': 'Medium'},
            8080: {'name': 'HTTP Alt', 'protocol': 'TCP', 'risk': 'Medium'},
            8443: {'name': 'HTTPS Alt', 'protocol': 'TCP', 'risk': 'Medium'},
            8787: {'name': 'RStudio', 'protocol': 'TCP', 'risk': 'Medium'},
            18881: {'name': 'Azure ML Python IntelliSense', 'protocol': 'TCP', 'risk': 'Low'}
        }
        
        port_info = common_ports.get(port, {
            'name': f'Port {port}',
            'protocol': 'Unknown',
            'risk': 'Unknown'
        })
        
        port_info['port'] = port
        return port_info
    
    @staticmethod
    def parse_port_range(port_range: str) -> List[int]:
        """Parse a port range string into a list of ports"""
        ports = []
        
        if port_range == '*' or port_range.lower() == 'any':
            return list(range(1, 65536))  # All ports
        
        try:
            # Handle single port
            if '-' not in port_range:
                ports.append(int(port_range))
            else:
                # Handle port range
                start, end = port_range.split('-', 1)
                start_port = int(start.strip())
                end_port = int(end.strip())
                ports.extend(range(start_port, end_port + 1))
        except ValueError:
            # Handle comma-separated ports
            if ',' in port_range:
                for port_str in port_range.split(','):
                    try:
                        if '-' in port_str:
                            start, end = port_str.strip().split('-', 1)
                            start_port = int(start.strip())
                            end_port = int(end.strip())
                            ports.extend(range(start_port, end_port + 1))
                        else:
                            ports.append(int(port_str.strip()))
                    except ValueError:
                        continue
        
        return sorted(list(set(ports)))
    
    @staticmethod
    def analyze_port_exposure(port_ranges: List[str]) -> Dict:
        """Analyze port exposure for security risks"""
        all_ports = set()
        high_risk_ports = set()
        medium_risk_ports = set()
        
        for port_range in port_ranges:
            ports = NetworkUtils.parse_port_range(port_range)
            all_ports.update(ports)
            
            for port in ports:
                port_info = NetworkUtils.identify_common_ports(port)
                if port_info['risk'] == 'High':
                    high_risk_ports.add(port)
                elif port_info['risk'] == 'Medium':
                    medium_risk_ports.add(port)
        
        return {
            'total_ports': len(all_ports),
            'high_risk_ports': sorted(list(high_risk_ports)),
            'medium_risk_ports': sorted(list(medium_risk_ports)),
            'risk_assessment': NetworkUtils._assess_port_risk(high_risk_ports, medium_risk_ports)
        }
    
    @staticmethod
    def _assess_port_risk(high_risk_ports: Set[int], medium_risk_ports: Set[int]) -> str:
        """Assess overall port exposure risk"""
        if high_risk_ports:
            return f"High - {len(high_risk_ports)} high-risk port(s) exposed"
        elif medium_risk_ports:
            return f"Medium - {len(medium_risk_ports)} medium-risk port(s) exposed"
        else:
            return "Low - No high-risk ports exposed"
    
    @staticmethod
    def validate_fqdn(fqdn: str) -> Dict:
        """Validate and analyze an FQDN"""
        # Basic FQDN regex pattern
        fqdn_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        )
        
        result = {
            'fqdn': fqdn,
            'is_valid': False,
            'is_wildcard': False,
            'domain_levels': 0,
            'top_level_domain': None,
            'category': 'unknown'
        }
        
        # Handle wildcard domains
        if fqdn.startswith('*.'):
            result['is_wildcard'] = True
            fqdn_to_check = fqdn[2:]  # Remove wildcard prefix
        else:
            fqdn_to_check = fqdn
        
        # Validate FQDN format
        if fqdn_pattern.match(fqdn_to_check):
            result['is_valid'] = True
            
            # Analyze domain structure
            parts = fqdn_to_check.split('.')
            result['domain_levels'] = len(parts)
            if parts:
                result['top_level_domain'] = parts[-1]
        
        # Categorize domain
        result['category'] = NetworkUtils._categorize_domain(fqdn_to_check)
        
        return result
    
    @staticmethod
    def _categorize_domain(domain: str) -> str:
        """Categorize a domain by type"""
        domain_lower = domain.lower()
        
        # Azure domains
        azure_indicators = [
            'azure', 'microsoft', 'msft', 'azureml', 'azurewebsites',
            'cloudapp', 'azurecontainer', 'azurecr', 'vault.azure'
        ]
        
        # Development/ML domains
        ml_indicators = [
            'anaconda', 'conda-forge', 'pypi', 'pythonhosted', 'jupyter',
            'github', 'gitlab', 'bitbucket', 'docker', 'tensorflow',
            'pytorch', 'huggingface'
        ]
        
        # Cloud provider domains
        cloud_indicators = [
            'amazonaws', 'googleapi', 'google.com', 'gcp', 'cloudflare'
        ]
        
        for indicator in azure_indicators:
            if indicator in domain_lower:
                return 'azure'
        
        for indicator in ml_indicators:
            if indicator in domain_lower:
                return 'ml_development'
        
        for indicator in cloud_indicators:
            if indicator in domain_lower:
                return 'cloud_provider'
        
        # Check for common CDN/package repositories
        if any(cdn in domain_lower for cdn in ['cdn', 'fastly', 'cloudfront']):
            return 'cdn'
        
        return 'general' 