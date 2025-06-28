"""
Workspace Selector for Interactive Mode
"""

import subprocess
import json
from typing import List, Dict, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import questionary

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class WorkspaceInfo:
    """Container for workspace information"""
    def __init__(self, name: str, resource_group: str, hub_type: str, location: str, resource_id: str):
        self.name = name
        self.resource_group = resource_group
        self.hub_type = hub_type  # 'ai-foundry' or 'azure-ml'
        self.location = location
        self.resource_id = resource_id
    
    def display_name(self) -> str:
        """Get display name with type indicator"""
        type_icon = "🔮" if self.hub_type == "ai-foundry" else "🤖"
        type_label = "AI Foundry" if self.hub_type == "ai-foundry" else "Azure ML"
        return f"{type_icon} {self.name} ({type_label}) - {self.location}"

class WorkspaceSelector:
    """Handles workspace discovery and selection"""
    
    def __init__(self, subscription_id: str, console: Optional[Console] = None):
        self.subscription_id = subscription_id
        self.console = console or Console()
        
    def discover_and_select_workspaces(self, analysis_mode: str) -> Optional[List[WorkspaceInfo]]:
        """
        Discover workspaces and allow user to select them.
        
        Args:
            analysis_mode: 'standard' for 1+ workspaces, 'compare' for exactly 2
            
        Returns:
            List of selected WorkspaceInfo objects, or None if cancelled/failed
        """
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]🔍 Azure Workspace Discovery[/bold cyan]",
            border_style="cyan"
        ))
        
        # Discover workspaces
        workspaces = self._discover_workspaces()
        if not workspaces:
            self.console.print("❌ [bold red]No Azure AI Foundry hubs or ML workspaces found[/bold red]")
            return None
        
        # Display workspaces in a table
        self._display_workspaces_table(workspaces)
        
        # Handle selection based on mode
        if analysis_mode == 'compare':
            return self._select_two_workspaces(workspaces)
        else:
            return self._select_multiple_workspaces(workspaces)
    
    def _discover_workspaces(self) -> List[WorkspaceInfo]:
        """Discover all Azure AI Foundry hubs and ML workspaces"""
        workspaces = []
        
        # Discover Azure ML workspaces
        ml_workspaces = self._discover_ml_workspaces()
        workspaces.extend(ml_workspaces)
        
        # Discover Azure AI Foundry hubs
        ai_foundry_hubs = self._discover_ai_foundry_hubs()
        workspaces.extend(ai_foundry_hubs)
        
        # Sort by name for consistent display
        workspaces.sort(key=lambda w: w.name.lower())
        
        return workspaces
    
    def _discover_ml_workspaces(self) -> List[WorkspaceInfo]:
        """Discover Azure ML workspaces"""
        try:
            result = subprocess.run(
                ['az', 'ml', 'workspace', 'list', '--subscription', self.subscription_id, '--output', 'json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                workspaces_data = json.loads(result.stdout)
                workspaces = []
                
                for ws in workspaces_data:
                    workspace = WorkspaceInfo(
                        name=ws['name'],
                        resource_group=ws['resource_group'],
                        hub_type='azure-ml',
                        location=ws['location'],
                        resource_id=ws['id']
                    )
                    workspaces.append(workspace)
                
                return workspaces
            else:
                logger.warning(f"Failed to discover ML workspaces: {result.stderr}")
                return []
                
        except Exception as e:
            logger.warning(f"Error discovering ML workspaces: {str(e)}")
            return []
    
    def _discover_ai_foundry_hubs(self) -> List[WorkspaceInfo]:
        """Discover Azure AI Foundry hubs"""
        try:
            # AI Foundry hubs are actually ML workspaces with kind='Hub'
            result = subprocess.run(
                ['az', 'resource', 'list', 
                 '--resource-type', 'Microsoft.MachineLearningServices/workspaces',
                 '--subscription', self.subscription_id,
                 '--query', '[?kind==`Hub`]',
                 '--output', 'json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                hubs_data = json.loads(result.stdout)
                hubs = []
                
                for hub in hubs_data:
                    # Extract resource group from resource ID
                    resource_parts = hub['id'].split('/')
                    resource_group = resource_parts[4] if len(resource_parts) > 4 else 'unknown'
                    
                    workspace = WorkspaceInfo(
                        name=hub['name'],
                        resource_group=resource_group,
                        hub_type='ai-foundry',
                        location=hub['location'],
                        resource_id=hub['id']
                    )
                    hubs.append(workspace)
                
                return hubs
            else:
                logger.warning(f"Failed to discover AI Foundry hubs: {result.stderr}")
                return []
                
        except Exception as e:
            logger.warning(f"Error discovering AI Foundry hubs: {str(e)}")
            return []
    
    def _display_workspaces_table(self, workspaces: List[WorkspaceInfo]):
        """Display workspaces in a formatted table with color coding"""
        table = Table(title="Discovered Azure AI Foundry Hubs & ML Workspaces", 
                     show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Name", style="white", no_wrap=False)
        table.add_column("Type", style="yellow", width=12)
        table.add_column("Resource Group", style="cyan", width=20)
        table.add_column("Location", style="blue", width=15)
        
        for i, ws in enumerate(workspaces, 1):
            # Color code by type
            type_style = "bold magenta" if ws.hub_type == "ai-foundry" else "bold green"
            type_icon = "🔮" if ws.hub_type == "ai-foundry" else "🤖"
            type_display = f"{type_icon} AI Foundry" if ws.hub_type == "ai-foundry" else f"{type_icon} Azure ML"
            
            table.add_row(
                str(i),
                ws.name,
                f"[{type_style}]{type_display}[/{type_style}]",
                ws.resource_group,
                ws.location
            )
        
        self.console.print(table)
        self.console.print()
        
        # Display legend
        legend = Text()
        legend.append("🔮 ", style="bold magenta")
        legend.append("Azure AI Foundry Hub", style="magenta")
        legend.append("  |  ")
        legend.append("🤖 ", style="bold green")
        legend.append("Azure ML Workspace", style="green")
        
        self.console.print(Panel(legend, title="Legend", border_style="dim"))
        self.console.print()
    
    def _select_two_workspaces(self, workspaces: List[WorkspaceInfo]) -> Optional[List[WorkspaceInfo]]:
        """Select exactly two workspaces for comparison"""
        if len(workspaces) < 2:
            self.console.print("❌ [bold red]At least 2 workspaces are required for comparison[/bold red]")
            return None
        
        self.console.print("[bold yellow]📊 Comparison Mode: Select exactly 2 workspaces to compare[/bold yellow]")
        
        # Create choices
        choices = []
        for i, ws in enumerate(workspaces, 1):
            choices.append({
                'name': f"{i}. {ws.display_name()}",
                'value': ws
            })
        
        try:
            # Select first workspace
            first = questionary.select(
                "Select the FIRST workspace to compare:",
                choices=choices
            ).ask()
            
            if not first:
                return None
            
            # Create choices for second workspace (exclude the first)
            remaining_choices = [choice for choice in choices if choice['value'] != first]
            
            second = questionary.select(
                "Select the SECOND workspace to compare:",
                choices=remaining_choices
            ).ask()
            
            if not second:
                return None
            
            self.console.print(f"✅ Selected for comparison:")
            self.console.print(f"   1️⃣ [bold green]{first.display_name()}[/bold green]")
            self.console.print(f"   2️⃣ [bold green]{second.display_name()}[/bold green]")
            
            return [first, second]
            
        except KeyboardInterrupt:
            self.console.print("\n❌ Selection cancelled")
            return None
    
    def _select_multiple_workspaces(self, workspaces: List[WorkspaceInfo]) -> Optional[List[WorkspaceInfo]]:
        """Select one or more workspaces for standard analysis"""
        self.console.print("[bold yellow]📋 Standard Analysis: Select one or more workspaces[/bold yellow]")
        
        # Create choices
        choices = []
        for i, ws in enumerate(workspaces, 1):
            choices.append({
                'name': f"{i}. {ws.display_name()}",
                'value': ws
            })
        
        # Add "All workspaces" option if more than one
        if len(workspaces) > 1:
            choices.append({
                'name': f"🌟 ALL WORKSPACES ({len(workspaces)} total)",
                'value': 'all'
            })
        
        try:
            selected = questionary.checkbox(
                "Select workspace(s) to analyze:",
                choices=choices
            ).ask()
            
            if not selected:
                self.console.print("❌ No workspaces selected")
                return None
            
            # Handle "all" selection
            if 'all' in selected:
                selected_workspaces = workspaces
                self.console.print(f"✅ Selected [bold green]ALL {len(workspaces)} workspaces[/bold green] for analysis")
            else:
                selected_workspaces = selected
                self.console.print(f"✅ Selected [bold green]{len(selected_workspaces)} workspace(s)[/bold green] for analysis:")
                for ws in selected_workspaces:
                    self.console.print(f"   • {ws.display_name()}")
            
            return selected_workspaces
            
        except KeyboardInterrupt:
            self.console.print("\n❌ Selection cancelled")
            return None 