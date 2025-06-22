from typing import Dict, List, Optional
import os
from .report_formatter import ReportFormatter

class SummaryReportGenerator:
    """Generates concise summary reports"""
    
    def __init__(self, analysis_results: Dict):
        self.analysis_results = analysis_results
        self.formatter = ReportFormatter()
    
    def generate_cli_summary(self) -> str:
        """Generate summary for CLI output"""
        workspace_info = self.analysis_results.get('results', {}).get('workspace', {})
        network_info = self.analysis_results.get('results', {}).get('network', {})
        resources_info = self.analysis_results.get('results', {}).get('connected_resources', {})
        summary_info = self.analysis_results.get('summary', {})
        
        output = "\n" + "=" * 80 + "\n"
        output += "📊 CONNECTIVITY ANALYSIS SUMMARY\n"
        output += "=" * 80 + "\n\n"
        
        # Workspace info
        output += f"📍 Workspace: {workspace_info.get('name', 'Unknown')}\n"
        output += f"   Type: {workspace_info.get('hub_type', 'Unknown').replace('-', ' ').title()}\n"
        output += f"   Location: {workspace_info.get('location', 'Unknown')}\n\n"
        
        # Network summary
        output += "🌐 Network Configuration:\n"
        output += f"   Type: {network_info.get('network_type', 'Unknown')}\n"
        output += f"   Public Access: {'⚠️ Enabled' if network_info.get('public_network_access') else '✅ Disabled'}\n"
        
        if network_info.get('private_endpoints', {}).get('count', 0) > 0:
            output += f"   Private Endpoints: {network_info.get('private_endpoints', {}).get('count', 0)}\n"
        
        if network_info.get('outbound_rules', {}).get('count', 0) > 0:
            output += f"   Outbound Rules: {network_info.get('outbound_rules', {}).get('count', 0)}\n"
        
        output += "\n"
        
        # Resources summary
        output += "🔗 Connected Resources:\n"
        output += f"   Total: {resources_info.get('total_resources', 0)}\n"
        
        security_summary = resources_info.get('security_summary', {})
        output += f"   Average Security Score: {self.formatter.format_security_score(int(security_summary.get('average_security_score', 0)))}\n"
        
        public_count = security_summary.get('public_accessible', 0)
        total_count = security_summary.get('total_resources', 0)
        output += f"   Public Accessible: {self.formatter.format_resource_count(public_count, total_count)}\n"
        
        pe_count = security_summary.get('private_endpoint_protected', 0)
        output += f"   Private Endpoint Protected: {self.formatter.format_resource_count(pe_count, total_count)}\n\n"
        
        # Resource breakdown by type
        resources_by_type = resources_info.get('resources_by_type', {})
        if resources_by_type:
            output += "📦 Resources by Type:\n"
            for resource_type, resources in resources_by_type.items():
                avg_score = sum(r.get('security_score', 0) for r in resources) / len(resources) if resources else 0
                output += f"   {resource_type}: {len(resources)} (avg score: {avg_score:.1f}/100)\n"
            output += "\n"
        
        # Key recommendations
        all_recommendations = []
        if 'recommendations' in network_info:
            all_recommendations.extend(network_info['recommendations'])
        if 'recommendations' in security_summary:
            all_recommendations.extend(security_summary['recommendations'])
        
        if all_recommendations:
            output += "⚡ Key Recommendations:\n"
            for rec in all_recommendations[:3]:  # Show top 3
                output += f"   • {rec}\n"
            if len(all_recommendations) > 3:
                output += f"   ... and {len(all_recommendations) - 3} more recommendations\n"
            output += "\n"
        
        # Analysis summary
        analysis_summary = summary_info.get('summary', {})
        output += "✅ Analysis Complete:\n"
        
        duration = analysis_summary.get('total_duration', 0)
        output += f"   Duration: {self.formatter.format_duration(duration)}\n"
        
        successful_steps = analysis_summary.get('successful_steps', 0)
        total_steps = analysis_summary.get('total_steps', 0)
        output += f"   Steps Completed: {successful_steps}/{total_steps}\n"
        
        if analysis_summary.get('failed_steps', 0) > 0:
            output += f"   Failed Steps: {analysis_summary.get('failed_steps', 0)}\n"
        
        if 'report_location' in self.analysis_results:
            output += f"\n📄 Full report saved to: {self.analysis_results['report_location']}\n"
            json_path = self.analysis_results['report_location'].replace('.md', '.json')
            output += f"   JSON data saved to: {json_path}\n"
        
        output += "\n" + "=" * 80 + "\n"
        
        return output
    
    def generate_security_summary(self) -> str:
        """Generate focused security summary"""
        network_info = self.analysis_results.get('results', {}).get('network', {})
        resources_info = self.analysis_results.get('results', {}).get('connected_resources', {})
        security_summary = resources_info.get('security_summary', {})
        
        output = "\n" + "🛡️  SECURITY ANALYSIS SUMMARY\n"
        output += "=" * 50 + "\n\n"
        
        # Overall security posture
        avg_score = security_summary.get('average_security_score', 0)
        output += f"Overall Security Score: {self.formatter.format_security_score(int(avg_score))}\n\n"
        
        # Network security
        output += "Network Security:\n"
        if not network_info.get('public_network_access'):
            output += "   ✅ Private network access only\n"
        else:
            output += "   ⚠️  Public network access enabled\n"
        
        isolation_mode = network_info.get('isolation_mode', 'Not configured')
        if isolation_mode == 'allow_only_approved_outbound':
            output += "   ✅ Strict outbound control enabled\n"
        elif isolation_mode == 'allow_internet_outbound':
            output += "   ⚠️  Internet outbound allowed\n"
        else:
            output += f"   ℹ️  Isolation mode: {isolation_mode}\n"
        
        output += "\n"
        
        # Resource security
        output += "Resource Security:\n"
        total_resources = security_summary.get('total_resources', 0)
        
        if total_resources > 0:
            public_accessible = security_summary.get('public_accessible', 0)
            pe_protected = security_summary.get('private_endpoint_protected', 0)
            
            if public_accessible == 0:
                output += "   ✅ No resources with public access\n"
            else:
                output += f"   ⚠️  {public_accessible} resources with public access\n"
            
            if pe_protected > 0:
                output += f"   ✅ {pe_protected} resources protected with private endpoints\n"
            else:
                output += "   ⚠️  No private endpoint protection found\n"
        else:
            output += "   ℹ️  No resources analyzed\n"
        
        output += "\n"
        
        # Top security recommendations
        recommendations = security_summary.get('recommendations', [])
        if recommendations:
            output += "Priority Actions:\n"
            for idx, rec in enumerate(recommendations[:2], 1):
                output += f"   {idx}. {rec}\n"
        
        output += "\n" + "=" * 50 + "\n"
        
        return output
    
    def generate_resource_summary(self) -> str:
        """Generate focused resource connectivity summary"""
        resources_info = self.analysis_results.get('results', {}).get('connected_resources', {})
        
        output = "\n" + "🔗 RESOURCE CONNECTIVITY SUMMARY\n"
        output += "=" * 50 + "\n\n"
        
        total_resources = resources_info.get('total_resources', 0)
        output += f"Total Connected Resources: {total_resources}\n\n"
        
        if total_resources == 0:
            output += "No connected resources found.\n"
            output += "=" * 50 + "\n"
            return output
        
        # Resources by type
        resources_by_type = resources_info.get('resources_by_type', {})
        
        if resources_by_type:
            output += "Resource Types:\n"
            for resource_type, resources in resources_by_type.items():
                output += f"   {resource_type}: {len(resources)}\n"
            output += "\n"
        
        # Access methods distribution
        access_methods = {}
        connection_types = {}
        
        for resource_type, resources in resources_by_type.items():
            for resource in resources:
                access_method = resource.get('access_method', 'unknown')
                access_methods[access_method] = access_methods.get(access_method, 0) + 1
                
                connection_type = resource.get('connection_type', 'unknown')
                connection_types[connection_type] = connection_types.get(connection_type, 0) + 1
        
        if access_methods:
            output += "Access Methods:\n"
            for method, count in access_methods.items():
                percentage = (count / total_resources) * 100
                output += f"   {self.formatter.format_connection_type(method)}: {count} ({percentage:.1f}%)\n"
            output += "\n"
        
        if connection_types:
            output += "Connection Types:\n"
            for conn_type, count in connection_types.items():
                percentage = (count / total_resources) * 100
                output += f"   {conn_type}: {count} ({percentage:.1f}%)\n"
            output += "\n"
        
        # Security insights
        security_summary = resources_info.get('security_summary', {})
        avg_score = security_summary.get('average_security_score', 0)
        
        output += f"Security Insights:\n"
        output += f"   Average Score: {self.formatter.format_security_score(int(avg_score))}\n"
        
        # Resource security distribution
        if resources_by_type:
            high_security = sum(1 for resources in resources_by_type.values() 
                              for resource in resources 
                              if resource.get('security_score', 0) >= 80)
            medium_security = sum(1 for resources in resources_by_type.values() 
                                for resource in resources 
                                if 60 <= resource.get('security_score', 0) < 80)
            low_security = sum(1 for resources in resources_by_type.values() 
                             for resource in resources 
                             if resource.get('security_score', 0) < 60)
            
            output += f"   High Security (80+): {self.formatter.format_resource_count(high_security, total_resources)}\n"
            output += f"   Medium Security (60-79): {self.formatter.format_resource_count(medium_security, total_resources)}\n"
            output += f"   Low Security (<60): {self.formatter.format_resource_count(low_security, total_resources)}\n"
        
        output += "\n" + "=" * 50 + "\n"
        
        return output 