"""
Comparison Analyzer for Interactive Mode
Generates diff reports between two workspaces focusing on connectivity settings
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .connectivity_analyzer import ConnectivityAnalyzer
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class ConnectivityDifference:
    """Represents a difference in connectivity configuration"""
    category: str
    workspace1_value: Any
    workspace2_value: Any
    difference_type: str  # 'added', 'removed', 'changed'
    severity: str  # 'high', 'medium', 'low'
    description: str

class ComparisonAnalyzer:
    """Analyzes differences between two workspace connectivity configurations"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        
    def compare_workspaces(self, workspace1_info: Dict, workspace2_info: Dict, 
                          subscription_id: str) -> Dict[str, Any]:
        """
        Compare two workspaces and generate a comprehensive diff report.
        
        Args:
            workspace1_info: First workspace info (from WorkspaceInfo)
            workspace2_info: Second workspace info (from WorkspaceInfo)
            subscription_id: Azure subscription ID
            
        Returns:
            Dict containing the comparison results
        """
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]⚖️  Workspace Comparison Analysis[/bold cyan]",
            border_style="cyan"
        ))
        
        # Analyze both workspaces
        analyzer1 = ConnectivityAnalyzer(
            workspace1_info['name'], 
            workspace1_info['resource_group'], 
            subscription_id,
            workspace1_info['hub_type']
        )
        
        analyzer2 = ConnectivityAnalyzer(
            workspace2_info['name'], 
            workspace2_info['resource_group'], 
            subscription_id,
            workspace2_info['hub_type']
        )
        
        self.console.print(f"🔍 Analyzing [bold magenta]{workspace1_info['name']}[/bold magenta]...")
        analysis1 = analyzer1.analyze()
        
        self.console.print(f"🔍 Analyzing [bold green]{workspace2_info['name']}[/bold green]...")
        analysis2 = analyzer2.analyze()
        
        # Generate comparison
        comparison = self._generate_comparison(
            workspace1_info, analysis1,
            workspace2_info, analysis2
        )
        
        # Display comparison results
        self._display_comparison_results(comparison)
        
        return comparison
    
    def _generate_comparison(self, ws1_info: Dict, analysis1: Dict, 
                           ws2_info: Dict, analysis2: Dict) -> Dict[str, Any]:
        """Generate detailed comparison between two workspace analyses"""
        differences = []
        
        # Compare basic workspace settings
        differences.extend(self._compare_basic_settings(ws1_info, analysis1, ws2_info, analysis2))
        
        # Compare network configuration
        differences.extend(self._compare_network_config(analysis1, analysis2))
        
        # Compare connected resources
        differences.extend(self._compare_connected_resources(analysis1, analysis2))
        
        # Compare outbound rules
        differences.extend(self._compare_outbound_rules(analysis1, analysis2))
        
        # Categorize differences by severity
        high_severity = [d for d in differences if d.severity == 'high']
        medium_severity = [d for d in differences if d.severity == 'medium']
        low_severity = [d for d in differences if d.severity == 'low']
        
        return {
            'workspace1': {
                'name': ws1_info['name'],
                'resource_group': ws1_info['resource_group'],
                'hub_type': ws1_info['hub_type'],
                'analysis': analysis1
            },
            'workspace2': {
                'name': ws2_info['name'],
                'resource_group': ws2_info['resource_group'],
                'hub_type': ws2_info['hub_type'],
                'analysis': analysis2
            },
            'differences': {
                'all': differences,
                'high': high_severity,
                'medium': medium_severity,
                'low': low_severity,
                'total_count': len(differences)
            },
            'summary': self._generate_summary(differences)
        }
    
    def _compare_basic_settings(self, ws1_info: Dict, analysis1: Dict, 
                              ws2_info: Dict, analysis2: Dict) -> List[ConnectivityDifference]:
        """Compare basic workspace settings"""
        differences = []
        
        # Compare hub types
        if ws1_info['hub_type'] != ws2_info['hub_type']:
            differences.append(ConnectivityDifference(
                category="Workspace Type",
                workspace1_value=ws1_info['hub_type'],
                workspace2_value=ws2_info['hub_type'],
                difference_type="changed",
                severity="medium",
                description=f"Different workspace types: {ws1_info['hub_type']} vs {ws2_info['hub_type']}"
            ))
        
        # Compare public network access
        ws1_public = analysis1.get('workspace_config', {}).get('public_network_access', 'Unknown')
        ws2_public = analysis2.get('workspace_config', {}).get('public_network_access', 'Unknown')
        
        if ws1_public != ws2_public:
            differences.append(ConnectivityDifference(
                category="Public Network Access",
                workspace1_value=ws1_public,
                workspace2_value=ws2_public,
                difference_type="changed",
                severity="high",
                description=f"Public network access differs: {ws1_public} vs {ws2_public}"
            ))
        
        return differences
    
    def _compare_network_config(self, analysis1: Dict, analysis2: Dict) -> List[ConnectivityDifference]:
        """Compare network configurations"""
        differences = []
        
        # Compare VNet configurations
        vnet1 = analysis1.get('network_config', {}).get('vnet_integration', {})
        vnet2 = analysis2.get('network_config', {}).get('vnet_integration', {})
        
        # Compare VNet enabled status
        vnet1_enabled = vnet1.get('enabled', False)
        vnet2_enabled = vnet2.get('enabled', False)
        
        if vnet1_enabled != vnet2_enabled:
            differences.append(ConnectivityDifference(
                category="VNet Integration",
                workspace1_value=vnet1_enabled,
                workspace2_value=vnet2_enabled,
                difference_type="changed",
                severity="high",
                description=f"VNet integration differs: {vnet1_enabled} vs {vnet2_enabled}"
            ))
        
        # Compare private endpoint configurations
        pe1 = analysis1.get('network_config', {}).get('private_endpoints', [])
        pe2 = analysis2.get('network_config', {}).get('private_endpoints', [])
        
        pe1_count = len(pe1)
        pe2_count = len(pe2)
        
        if pe1_count != pe2_count:
            differences.append(ConnectivityDifference(
                category="Private Endpoints",
                workspace1_value=pe1_count,
                workspace2_value=pe2_count,
                difference_type="changed",
                severity="medium",
                description=f"Private endpoint count differs: {pe1_count} vs {pe2_count}"
            ))
        
        return differences
    
    def _compare_connected_resources(self, analysis1: Dict, analysis2: Dict) -> List[ConnectivityDifference]:
        """Compare connected resources"""
        differences = []
        
        # Get connected resources
        resources1 = analysis1.get('connected_resources', [])
        resources2 = analysis2.get('connected_resources', [])
        
        # Compare by resource type
        types1 = set(r.get('resource_type', '') for r in resources1)
        types2 = set(r.get('resource_type', '') for r in resources2)
        
        # Resources only in workspace1
        only_in_1 = types1 - types2
        for resource_type in only_in_1:
            differences.append(ConnectivityDifference(
                category="Connected Resources",
                workspace1_value=resource_type,
                workspace2_value="Not present",
                difference_type="removed",
                severity="medium",
                description=f"Resource type {resource_type} only in first workspace"
            ))
        
        # Resources only in workspace2
        only_in_2 = types2 - types1
        for resource_type in only_in_2:
            differences.append(ConnectivityDifference(
                category="Connected Resources",
                workspace1_value="Not present",
                workspace2_value=resource_type,
                difference_type="added",
                severity="medium",
                description=f"Resource type {resource_type} only in second workspace"
            ))
        
        return differences
    
    def _compare_outbound_rules(self, analysis1: Dict, analysis2: Dict) -> List[ConnectivityDifference]:
        """Compare outbound rules configurations"""
        differences = []
        
        # Compare outbound rule counts
        rules1 = analysis1.get('outbound_rules', [])
        rules2 = analysis2.get('outbound_rules', [])
        
        rules1_count = len(rules1)
        rules2_count = len(rules2)
        
        if rules1_count != rules2_count:
            differences.append(ConnectivityDifference(
                category="Outbound Rules",
                workspace1_value=rules1_count,
                workspace2_value=rules2_count,
                difference_type="changed",
                severity="low",
                description=f"Outbound rule count differs: {rules1_count} vs {rules2_count}"
            ))
        
        # Compare rule types
        if rules1 and rules2:
            types1 = set(r.get('type', '') for r in rules1)
            types2 = set(r.get('type', '') for r in rules2)
            
            if types1 != types2:
                differences.append(ConnectivityDifference(
                    category="Outbound Rule Types",
                    workspace1_value=list(types1),
                    workspace2_value=list(types2),
                    difference_type="changed",
                    severity="low",
                    description="Different outbound rule types configured"
                ))
        
        return differences
    
    def _generate_summary(self, differences: List[ConnectivityDifference]) -> Dict[str, Any]:
        """Generate comparison summary"""
        return {
            'total_differences': len(differences),
            'high_severity': len([d for d in differences if d.severity == 'high']),
            'medium_severity': len([d for d in differences if d.severity == 'medium']),
            'low_severity': len([d for d in differences if d.severity == 'low']),
            'categories': list(set(d.category for d in differences)),
            'recommendation': self._get_recommendation(differences)
        }
    
    def _get_recommendation(self, differences: List[ConnectivityDifference]) -> str:
        """Get recommendation based on differences"""
        high_count = len([d for d in differences if d.severity == 'high'])
        medium_count = len([d for d in differences if d.severity == 'medium'])
        
        if high_count > 0:
            return "CRITICAL: High-severity differences found that may impact connectivity"
        elif medium_count > 3:
            return "WARNING: Multiple medium-severity differences found"
        elif len(differences) > 10:
            return "INFO: Many configuration differences found"
        elif len(differences) == 0:
            return "SUCCESS: Workspaces have similar connectivity configurations"
        else:
            return "INFO: Minor configuration differences found"
    
    def _display_comparison_results(self, comparison: Dict[str, Any]):
        """Display comparison results in a formatted table"""
        self.console.print()
        
        # Summary panel
        summary = comparison['summary']
        summary_text = Text()
        summary_text.append(f"Total Differences: {summary['total_differences']}\n", style="bold")
        summary_text.append(f"High Priority: {summary['high_severity']} | ", style="bold red")
        summary_text.append(f"Medium Priority: {summary['medium_severity']} | ", style="bold yellow")
        summary_text.append(f"Low Priority: {summary['low_severity']}\n", style="bold green")
        summary_text.append(f"\n{summary['recommendation']}", style="bold cyan")
        
        summary_panel = Panel(
            summary_text,
            title="Comparison Summary",
            border_style="cyan"
        )
        self.console.print(summary_panel)
        
        # Differences table
        if comparison['differences']['total_count'] > 0:
            self._display_differences_table(comparison['differences']['all'])
        else:
            self.console.print("\n✅ [bold green]No significant differences found![/bold green]")
    
    def _display_differences_table(self, differences: List[ConnectivityDifference]):
        """Display differences in a table format"""
        table = Table(title="Connectivity Configuration Differences", 
                     show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Workspace 1", style="green", width=25)
        table.add_column("Workspace 2", style="blue", width=25)
        table.add_column("Severity", width=10)
        table.add_column("Description", style="white", no_wrap=False)
        
        for diff in differences:
            severity_style = {
                'high': 'bold red',
                'medium': 'bold yellow',
                'low': 'bold green'
            }.get(diff.severity, 'white')
            
            table.add_row(
                diff.category,
                str(diff.workspace1_value),
                str(diff.workspace2_value),
                f"[{severity_style}]{diff.severity.upper()}[/{severity_style}]",
                diff.description
            )
        
        self.console.print(table) 