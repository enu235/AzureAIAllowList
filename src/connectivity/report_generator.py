from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import os
from abc import ABC, abstractmethod

@dataclass
class ReportSection:
    """Represents a section of the report"""
    title: str
    content: str
    level: int = 2  # Heading level
    subsections: List['ReportSection'] = None
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []

class BaseReportGenerator(ABC):
    """Base class for report generators"""
    
    def __init__(self, analysis_results: Dict[str, Any]):
        self.analysis_results = analysis_results
        self.report_sections: List[ReportSection] = []
        self.metadata = {
            'generated_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
    
    @abstractmethod
    def generate(self) -> str:
        """Generate the report"""
        pass
    
    @abstractmethod
    def save(self, filepath: str):
        """Save the report to file"""
        pass

class MarkdownReportGenerator(BaseReportGenerator):
    """Generates Markdown reports with Mermaid diagrams"""
    
    def generate(self) -> str:
        """Generate complete Markdown report"""
        self._build_report_structure()
        return self._render_markdown()
    
    def _build_report_structure(self):
        """Build the report structure"""
        # Executive Summary
        self.report_sections.append(self._generate_executive_summary())
        
        # Network Configuration
        self.report_sections.append(self._generate_network_section())
        
        # Connected Resources
        self.report_sections.append(self._generate_resources_section())
        
        # Security Analysis
        self.report_sections.append(self._generate_security_section())
        
        # Connectivity Diagram
        self.report_sections.append(self._generate_connectivity_diagram())
        
        # Recommendations
        self.report_sections.append(self._generate_recommendations())
        
        # Detailed Findings
        self.report_sections.append(self._generate_detailed_findings())
    
    def _generate_executive_summary(self) -> ReportSection:
        """Generate executive summary section"""
        workspace_info = self.analysis_results.get('results', {}).get('workspace', {})
        network_info = self.analysis_results.get('results', {}).get('network', {})
        resources_info = self.analysis_results.get('results', {}).get('connected_resources', {})
        
        content = f"""
## 📋 Executive Summary

**Workspace:** {workspace_info.get('name', 'Unknown')}  
**Type:** {workspace_info.get('hub_type', 'Unknown').replace('-', ' ').title()}  
**Location:** {workspace_info.get('location', 'Unknown')}  
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Key Findings

- **Network Type:** {network_info.get('network_type', 'Unknown').replace('_', ' ').title()}
- **Isolation Mode:** {network_info.get('isolation_mode', 'Not configured')}
- **Public Network Access:** {'⚠️ Enabled' if network_info.get('public_network_access') else '✅ Disabled'}
- **Total Connected Resources:** {resources_info.get('total_resources', 0)}
- **Average Security Score:** {resources_info.get('security_summary', {}).get('average_security_score', 0)}/100

### Quick Status

{self._generate_status_badges(network_info, resources_info)}
"""
        return ReportSection("Executive Summary", content, level=2)
    
    def _generate_status_badges(self, network_info: Dict, resources_info: Dict) -> str:
        """Generate status badges for quick overview"""
        badges = []
        
        # Network security badge
        if not network_info.get('public_network_access'):
            badges.append("🛡️ **Private Network**")
        else:
            badges.append("⚠️ **Public Access Enabled**")
        
        # Private endpoints
        pe_count = network_info.get('private_endpoints', {}).get('count', 0)
        if pe_count > 0:
            badges.append(f"🔒 **{pe_count} Private Endpoints**")
        
        # Resources security
        security_summary = resources_info.get('security_summary', {})
        if security_summary.get('average_security_score', 0) >= 80:
            badges.append("✅ **High Security**")
        elif security_summary.get('average_security_score', 0) >= 60:
            badges.append("⚠️ **Medium Security**")
        else:
            badges.append("❌ **Low Security**")
            
        return " | ".join(badges)
    
    def _generate_network_section(self) -> ReportSection:
        """Generate network configuration section"""
        network_info = self.analysis_results.get('results', {}).get('network', {})
        
        content = f"""
### Network Configuration

**Configuration Type:** {network_info.get('network_type', 'Unknown')}

"""
        
        if network_info.get('network_type') == 'managed':
            content += self._generate_managed_network_details(network_info)
        elif network_info.get('network_type') == 'customer':
            content += self._generate_customer_network_details(network_info)
        
        # Add outbound rules summary
        outbound_rules = network_info.get('outbound_rules', {})
        if outbound_rules.get('count', 0) > 0:
            content += self._generate_outbound_rules_summary(outbound_rules)
        
        return ReportSection("Network Configuration", content, level=2)
    
    def _generate_managed_network_details(self, network_info: Dict) -> str:
        """Generate details for managed network"""
        return f"""
#### Managed Virtual Network Details

- **Isolation Mode:** {network_info.get('isolation_mode', 'Not configured')}
- **Public Network Access:** {network_info.get('public_network_access')}

##### Network Isolation Settings

| Setting | Value |
|---------|-------|
| Allow Internet Outbound | {network_info.get('isolation_mode') == 'allow_internet_outbound'} |
| Allow Only Approved Outbound | {network_info.get('isolation_mode') == 'allow_only_approved_outbound'} |
| Disabled | {network_info.get('isolation_mode') == 'disabled'} |
"""
    
    def _generate_customer_network_details(self, network_info: Dict) -> str:
        """Generate details for customer-managed network"""
        vnet_details = network_info.get('vnet_details', {})
        
        return f"""
#### Customer-Managed Virtual Network Details

- **VNet Configuration:** Customer-managed networking
- **Network Security Groups:** {len(vnet_details.get('network_security_groups', []))}
- **Route Tables:** {len(vnet_details.get('route_tables', []))}
- **Security Level:** {vnet_details.get('security_level', 'Unknown')}

##### Network Security Summary

{self._generate_vnet_security_table(vnet_details)}
"""
    
    def _generate_vnet_security_table(self, vnet_details: Dict) -> str:
        """Generate VNet security details table"""
        nsgs = vnet_details.get('network_security_groups', [])
        
        if not nsgs:
            return "No Network Security Groups found."
        
        table = "| NSG Name | Allow Rules | Deny Rules | Risk Level |\n"
        table += "|----------|-------------|------------|------------|\n"
        
        for nsg in nsgs:
            table += f"| {nsg.get('name', 'Unknown')} | "
            table += f"{nsg.get('allow_rules_count', 0)} | "
            table += f"{nsg.get('deny_rules_count', 0)} | "
            table += f"{nsg.get('risk_level', 'Unknown')} |\n"
        
        return table
    
    def _generate_outbound_rules_summary(self, outbound_rules: Dict) -> str:
        """Generate outbound rules summary"""
        rules = outbound_rules.get('rules', {})
        
        content = """
#### Outbound Rules Summary

| Type | Count | Status |
|------|-------|--------|
"""
        
        for rule_type, rule_list in rules.items():
            if isinstance(rule_list, list) and rule_list:
                content += f"| {rule_type.replace('_', ' ').title()} | {len(rule_list)} | Active |\n"
        
        return content
    
    def _generate_connectivity_diagram(self) -> ReportSection:
        """Generate Mermaid connectivity diagram"""
        diagram = self._build_mermaid_diagram()
        
        content = f"""
### Network Connectivity Diagram

```mermaid
{diagram}
```

This diagram shows the network connectivity between your workspace and connected resources.
"""
        return ReportSection("Connectivity Visualization", content, level=2)
    
    def _build_mermaid_diagram(self) -> str:
        """Build Mermaid diagram for connectivity"""
        workspace_info = self.analysis_results.get('results', {}).get('workspace', {})
        network_info = self.analysis_results.get('results', {}).get('network', {})
        resources_info = self.analysis_results.get('results', {}).get('connected_resources', {})
        
        diagram = """graph TB
    subgraph "Azure Subscription"
        subgraph "Resource Group"
"""
        
        # Add workspace node
        workspace_name = workspace_info.get('name', 'Workspace')
        hub_type = workspace_info.get('hub_type', 'ml')
        
        if hub_type == 'azure-ai-foundry':
            diagram += f'            Hub["{workspace_name}<br/>(AI Foundry Hub)"]\n'
        else:
            diagram += f'            WS["{workspace_name}<br/>(ML Workspace)"]\n'
        
        # Add network configuration
        if network_info.get('network_type') == 'managed':
            diagram += '            ManagedVNet["Managed VNet<br/>(Microsoft-managed)"]\n'
            if hub_type == 'azure-ai-foundry':
                diagram += '            Hub --> ManagedVNet\n'
            else:
                diagram += '            WS --> ManagedVNet\n'
        elif network_info.get('network_type') == 'customer':
            diagram += '            CustomerVNet["Customer VNet<br/>(Customer-managed)"]\n'
            if hub_type == 'azure-ai-foundry':
                diagram += '            Hub --> CustomerVNet\n'
            else:
                diagram += '            WS --> CustomerVNet\n'
        
        # Add resources
        resources_by_type = resources_info.get('resources_by_type', {})
        
        for resource_type, resources in resources_by_type.items():
            for idx, resource in enumerate(resources):
                node_id = f"{resource_type}{idx}"
                resource_name = resource.get('name', 'Unknown')
                
                # Style based on access method
                if resource.get('access_method') == 'private-endpoint':
                    diagram += f'            {node_id}["{resource_name}<br/>({resource_type})<br/>🔒 Private Endpoint"]\n'
                elif resource.get('public_access'):
                    diagram += f'            {node_id}["{resource_name}<br/>({resource_type})<br/>⚠️ Public Access"]\n'
                else:
                    diagram += f'            {node_id}["{resource_name}<br/>({resource_type})"]\n'
                
                # Add connections
                if hub_type == 'azure-ai-foundry':
                    if resource.get('connection_type') == 'default':
                        diagram += f'            Hub -.-> {node_id}\n'
                    else:
                        diagram += f'            Hub --> {node_id}\n'
                else:
                    if resource.get('connection_type') == 'default':
                        diagram += f'            WS -.-> {node_id}\n'
                    else:
                        diagram += f'            WS --> {node_id}\n'
        
        diagram += """        end
    end
    
    classDef secure fill:#90EE90,stroke:#006400,stroke-width:2px
    classDef warning fill:#FFE4B5,stroke:#FF8C00,stroke-width:2px
    classDef default fill:#E6E6FA,stroke:#4B0082,stroke-width:1px"""
        
        return diagram
    
    def _generate_resources_section(self) -> ReportSection:
        """Generate connected resources section"""
        resources_info = self.analysis_results.get('results', {}).get('connected_resources', {})
        
        content = """
### Connected Resources Overview

"""
        
        # Resources by type table
        resources_by_type = resources_info.get('resources_by_type', {})
        
        if resources_by_type:
            content += "| Resource Type | Count | Avg Security Score |\n"
            content += "|---------------|-------|-------------------|\n"
            
            for resource_type, resources in resources_by_type.items():
                avg_score = sum(r.get('security_score', 0) for r in resources) / len(resources) if resources else 0
                content += f"| {resource_type} | {len(resources)} | {avg_score:.1f}/100 |\n"
        
        # Detailed resource tables
        for resource_type, resources in resources_by_type.items():
            content += f"\n#### {resource_type}\n\n"
            content += self._generate_resource_table(resources)
        
        return ReportSection("Connected Resources", content, level=2)
    
    def _generate_resource_table(self, resources: List[Dict]) -> str:
        """Generate table for specific resource type"""
        if not resources:
            return "No resources found.\n"
        
        table = "| Name | Resource Group | Access Method | Public Access | Security Score |\n"
        table += "|------|----------------|---------------|---------------|----------------|\n"
        
        for resource in resources:
            public_access = "⚠️ Yes" if resource.get('public_access') else "✅ No"
            table += f"| {resource.get('name')} | {resource.get('resource_group')} | "
            table += f"{resource.get('access_method')} | {public_access} | "
            table += f"{resource.get('security_score')}/100 |\n"
        
        return table
    
    def _generate_security_section(self) -> ReportSection:
        """Generate security analysis section"""
        network_info = self.analysis_results.get('results', {}).get('network', {})
        resources_info = self.analysis_results.get('results', {}).get('connected_resources', {})
        security_summary = resources_info.get('security_summary', {})
        
        content = f"""
### Security Analysis

#### Overall Security Posture

- **Network Security Level:** {self._calculate_network_security_level(network_info)}
- **Resource Security Score:** {security_summary.get('average_security_score', 0)}/100
- **Resources with Public Access:** {security_summary.get('public_accessible', 0)}/{security_summary.get('total_resources', 0)}
- **Resources with Private Endpoints:** {security_summary.get('private_endpoint_protected', 0)}/{security_summary.get('total_resources', 0)}

#### Security Findings

"""
        
        # Add key security findings
        findings = self._generate_security_findings(network_info, resources_info)
        for finding in findings:
            content += f"- {finding}\n"
        
        return ReportSection("Security Analysis", content, level=2)
    
    def _calculate_network_security_level(self, network_info: Dict) -> str:
        """Calculate overall network security level"""
        if not network_info.get('public_network_access'):
            if network_info.get('isolation_mode') == 'allow_only_approved_outbound':
                return "🛡️ **High** - Private access with strict outbound control"
            else:
                return "🔒 **Medium-High** - Private access only"
        else:
            return "⚠️ **Low** - Public network access enabled"
    
    def _generate_security_findings(self, network_info: Dict, resources_info: Dict) -> List[str]:
        """Generate security findings"""
        findings = []
        
        # Network findings
        if network_info.get('public_network_access'):
            findings.append("⚠️ **Public network access is enabled** - Consider disabling for enhanced security")
        
        # Resource findings
        security_summary = resources_info.get('security_summary', {})
        if security_summary.get('public_accessible', 0) > 0:
            findings.append(f"⚠️ **{security_summary.get('public_accessible')} resources have public access enabled**")
        
        # Positive findings
        if security_summary.get('private_endpoint_protected', 0) > 0:
            findings.append(f"✅ **{security_summary.get('private_endpoint_protected')} resources are protected with private endpoints**")
        
        return findings
    
    def _generate_recommendations(self) -> ReportSection:
        """Generate recommendations section"""
        all_recommendations = []
        
        # Collect recommendations from different sections
        network_info = self.analysis_results.get('results', {}).get('network', {})
        if 'recommendations' in network_info:
            all_recommendations.extend(network_info['recommendations'])
        
        resources_info = self.analysis_results.get('results', {}).get('connected_resources', {})
        security_summary = resources_info.get('security_summary', {})
        if 'recommendations' in security_summary:
            all_recommendations.extend(security_summary['recommendations'])
        
        content = """
### Recommendations

Based on the analysis, here are our recommendations to improve your security posture:

"""
        
        if all_recommendations:
            for idx, rec in enumerate(all_recommendations, 1):
                content += f"{idx}. {rec}\n"
        else:
            content += "✅ No critical security recommendations at this time.\n"
        
        # Add best practices
        content += """
#### Best Practices

1. **Use Private Endpoints**: Configure private endpoints for all critical resources
2. **Disable Public Access**: Turn off public network access where possible
3. **Implement Network Isolation**: Use managed VNet with approved outbound rules
4. **Regular Security Reviews**: Periodically review and update network configurations
5. **Monitor Access Logs**: Enable diagnostic logging for all resources
"""
        
        return ReportSection("Recommendations", content, level=2)
    
    def _generate_detailed_findings(self) -> ReportSection:
        """Generate detailed findings section"""
        content = """
### Detailed Analysis Results

<details>
<summary>Click to expand detailed JSON results</summary>

```json
"""
        
        # Pretty print the analysis results
        content += json.dumps(self.analysis_results, indent=2, default=str)
        
        content += """
```

</details>
"""
        
        return ReportSection("Detailed Findings", content, level=2)
    
    def _render_markdown(self) -> str:
        """Render all sections to Markdown"""
        workspace_info = self.analysis_results.get('results', {}).get('workspace', {})
        hub_type = workspace_info.get('hub_type', 'ML').replace('-', ' ').title()
        
        output = f"# Azure {hub_type} Connectivity Analysis Report\n\n"
        
        for section in self.report_sections:
            output += self._render_section(section)
        
        # Add footer
        output += f"\n---\n\n*Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*\n"
        
        return output
    
    def _render_section(self, section: ReportSection) -> str:
        """Render a single section"""
        output = section.content + "\n"
        
        for subsection in section.subsections:
            output += self._render_section(subsection)
        
        return output
    
    def save(self, filepath: str):
        """Save report to file"""
        report_content = self.generate()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Also save JSON version
        json_filepath = filepath.replace('.md', '.json')
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, default=str) 