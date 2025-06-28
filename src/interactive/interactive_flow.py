"""
Main Interactive Flow Coordinator
"""

import sys
from typing import Optional, Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from .auth_handler import AuthHandler
from .subscription_selector import SubscriptionSelector
from .workspace_selector import WorkspaceSelector, WorkspaceInfo
from .analysis_selector import AnalysisSelector
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class InteractiveFlow:
    """Main coordinator for interactive mode"""
    
    def __init__(self):
        self.console = Console()
        self.auth_handler = AuthHandler(self.console)
        self.current_subscription = None
        
    def run(self) -> Optional[Dict[str, Any]]:
        """
        Run the complete interactive flow.
        
        Returns:
            Dict with analysis configuration, or None if cancelled/failed
        """
        try:
            self._display_welcome_banner()
            
            # Step 1: Authentication
            if not self._handle_authentication():
                return None
            
            # Step 2: Subscription Selection
            subscription = self._handle_subscription_selection()
            if not subscription:
                return None
            
            # Step 3: Analysis Type Selection
            analysis_type = self._handle_analysis_type_selection()
            if not analysis_type:
                return None
            
            # Step 4: Workspace Selection
            workspaces = self._handle_workspace_selection(analysis_type)
            if not workspaces:
                return None
            
            # Step 5: Package Analysis Configuration
            package_config = self._handle_package_configuration()
            
            # Step 6: Build and return configuration
            config = self._build_analysis_config(
                subscription, workspaces, analysis_type, package_config
            )
            
            self._display_analysis_summary(config)
            
            return config
            
        except KeyboardInterrupt:
            self.console.print("\n\n❌ [bold red]Interactive mode cancelled by user[/bold red]")
            return None
        except Exception as e:
            self.console.print(f"\n❌ [bold red]Interactive mode error: {str(e)}[/bold red]")
            logger.error(f"Interactive flow error: {str(e)}")
            return None
    
    def _display_welcome_banner(self):
        """Display welcome banner and disclaimer"""
        welcome_text = Text()
        welcome_text.append("🚀 Azure AI Foundry & ML Package Allowlist Tool\n", style="bold cyan")
        welcome_text.append("Interactive Mode", style="bold yellow")
        
        banner = Panel(
            welcome_text,
            title="Welcome",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(banner)
        
        # AS IS Disclaimer
        disclaimer = Text()
        disclaimer.append("⚠️  DISCLAIMER: ", style="bold yellow")
        disclaimer.append("This tool is provided 'AS IS' without warranty. ", style="white")
        disclaimer.append("Review all recommendations before implementation. ", style="white")
        disclaimer.append("Test in non-production environments first.", style="bold red")
        
        disclaimer_panel = Panel(
            disclaimer,
            title="Important Notice",
            border_style="yellow",
            padding=(0, 1)
        )
        
        self.console.print(disclaimer_panel)
    
    def _handle_authentication(self) -> bool:
        """Handle Azure CLI authentication"""
        if not self.auth_handler.check_and_ensure_login():
            self.console.print("❌ [bold red]Authentication failed. Cannot continue without Azure access.[/bold red]")
            return False
        
        if not self.auth_handler.validate_ml_extension():
            self.console.print("❌ [bold red]Azure ML extension validation failed.[/bold red]")
            return False
        
        return True
    
    def _handle_subscription_selection(self) -> Optional[Dict]:
        """Handle subscription selection"""
        subscription_selector = SubscriptionSelector(self.console)
        subscription = subscription_selector.select_subscription()
        
        if subscription:
            self.current_subscription = subscription
            return subscription
        
        self.console.print("❌ [bold red]No subscription selected. Cannot continue.[/bold red]")
        return None
    
    def _handle_analysis_type_selection(self) -> Optional[str]:
        """Handle analysis type selection"""
        analysis_selector = AnalysisSelector(self.console)
        return analysis_selector.select_analysis_type()
    
    def _handle_workspace_selection(self, analysis_type: str) -> Optional[List[WorkspaceInfo]]:
        """Handle workspace discovery and selection"""
        workspace_selector = WorkspaceSelector(
            self.current_subscription['id'], 
            self.console
        )
        
        return workspace_selector.discover_and_select_workspaces(analysis_type)
    
    def _handle_package_configuration(self) -> Optional[Dict]:
        """Handle package analysis configuration"""
        analysis_selector = AnalysisSelector(self.console)
        return analysis_selector.configure_package_analysis()
    
    def _build_analysis_config(self, subscription: Dict, workspaces: List[WorkspaceInfo], 
                              analysis_type: str, package_config: Optional[Dict]) -> Dict[str, Any]:
        """Build the final analysis configuration"""
        config = {
            'mode': 'interactive',
            'subscription': subscription,
            'analysis_type': analysis_type,
            'workspaces': workspaces,
            'package_analysis': package_config,
            'output_settings': {
                'format': 'cli',
                'include_transitive': package_config.get('include_transitive', True) if package_config else True,
                'platform': package_config.get('platform', 'auto') if package_config else 'auto',
                'verbose': True
            }
        }
        
        # Add AI features if configured
        if package_config and package_config.get('ai_features'):
            config['ai_features'] = package_config['ai_features']
        
        return config
    
    def _display_analysis_summary(self, config: Dict[str, Any]):
        """Display summary of the analysis configuration"""
        self.console.print()
        self.console.print(Panel.fit(
            "[bold green]🎯 Analysis Configuration Ready[/bold green]",
            border_style="green"
        ))
        
        # Subscription info
        subscription = config['subscription']
        self.console.print(f"📋 [bold]Subscription:[/bold] {subscription['name']}")
        self.console.print(f"   ID: {subscription['id']}")
        
        # Analysis type
        analysis_type_display = "Standard Analysis" if config['analysis_type'] == 'standard' else "Comparison Analysis"
        self.console.print(f"📊 [bold]Analysis Type:[/bold] {analysis_type_display}")
        
        # Workspaces
        workspaces = config['workspaces']
        self.console.print(f"🏢 [bold]Workspaces ({len(workspaces)}):[/bold]")
        for ws in workspaces:
            type_icon = "🔮" if ws.hub_type == "ai-foundry" else "🤖"
            self.console.print(f"   {type_icon} {ws.name} ({ws.resource_group})")
        
        # Package analysis
        package_config = config['package_analysis']
        if package_config:
            self.console.print(f"📦 [bold]Package Analysis:[/bold] Enabled")
            if package_config.get('files'):
                self.console.print(f"   Files: {len(package_config['files'])} package file(s)")
            
            ai_features = package_config.get('ai_features', {})
            enabled_features = []
            if ai_features.get('include_vscode'):
                enabled_features.append("VS Code")
            if ai_features.get('include_huggingface'):
                enabled_features.append("HuggingFace")
            if ai_features.get('include_prompt_flow'):
                enabled_features.append("Prompt Flow")
            if ai_features.get('custom_fqdns'):
                enabled_features.append("Custom FQDNs")
            
            if enabled_features:
                self.console.print(f"   AI Features: {', '.join(enabled_features)}")
        else:
            self.console.print(f"📦 [bold]Package Analysis:[/bold] [yellow]Disabled[/yellow] (connectivity only)")
        
        self.console.print()
        self.console.print("🚀 [bold green]Starting analysis...[/bold green]")
    
    @staticmethod
    def is_interactive_mode(args: List[str]) -> bool:
        """Check if the tool should run in interactive mode"""
        # Run interactive if no workspace-name provided or explicitly requested
        has_workspace = any('--workspace-name' in arg or '-w' in arg for arg in args)
        has_interactive_flag = '--interactive' in args
        
        return not has_workspace or has_interactive_flag 