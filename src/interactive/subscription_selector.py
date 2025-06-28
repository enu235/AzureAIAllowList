"""
Subscription Selector for Interactive Mode
"""

import subprocess
import json
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import questionary

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class SubscriptionSelector:
    """Handles Azure subscription selection"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        
    def select_subscription(self) -> Optional[Dict]:
        """
        List available subscriptions and allow user to select one.
        
        Returns:
            Selected subscription info dict, or None if cancelled/failed
        """
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]📋 Azure Subscription Selection[/bold cyan]",
            border_style="cyan"
        ))
        
        # Get available subscriptions
        subscriptions = self._get_subscriptions()
        if not subscriptions:
            self.console.print("❌ [bold red]No subscriptions found or accessible[/bold red]")
            return None
        
        # Display subscriptions in a table
        self._display_subscriptions_table(subscriptions)
        
        # Create selection choices
        choices = []
        for i, sub in enumerate(subscriptions, 1):
            display_name = f"{i}. {sub['name']} ({sub['id'][:8]}...)"
            if sub.get('isDefault', False):
                display_name += " [CURRENT]"
            choices.append({
                'name': display_name,
                'value': sub
            })
        
        try:
            # Use questionary for interactive selection
            selected = questionary.select(
                "Select a subscription:",
                choices=choices,
                style=questionary.Style([
                    ('question', 'bold'),
                    ('answer', 'fg:#ff9d00 bold'),
                    ('pointer', 'fg:#ff9d00 bold'),
                    ('highlighted', 'fg:#ff9d00 bold'),
                ])
            ).ask()
            
            if selected:
                self.console.print(f"✅ Selected: [bold green]{selected['name']}[/bold green]")
                
                # Set as active subscription
                if self._set_active_subscription(selected['id']):
                    return selected
                else:
                    self.console.print("❌ Failed to set active subscription")
                    return None
            else:
                self.console.print("❌ No subscription selected")
                return None
                
        except KeyboardInterrupt:
            self.console.print("\n❌ Selection cancelled")
            return None
    
    def _get_subscriptions(self) -> List[Dict]:
        """Get list of available Azure subscriptions"""
        try:
            result = subprocess.run(
                ['az', 'account', 'list', '--output', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                subscriptions = json.loads(result.stdout)
                # Filter enabled subscriptions
                return [sub for sub in subscriptions if sub.get('state') == 'Enabled']
            else:
                logger.error(f"Failed to get subscriptions: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting subscriptions: {str(e)}")
            return []
    
    def _display_subscriptions_table(self, subscriptions: List[Dict]):
        """Display subscriptions in a formatted table"""
        table = Table(title="Available Azure Subscriptions", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Subscription Name", style="cyan", no_wrap=False)
        table.add_column("Subscription ID", style="green", width=40)
        table.add_column("Status", style="yellow")
        
        for i, sub in enumerate(subscriptions, 1):
            status = "CURRENT" if sub.get('isDefault', False) else "Available"
            status_style = "bold green" if sub.get('isDefault', False) else "white"
            
            table.add_row(
                str(i),
                sub['name'],
                sub['id'],
                f"[{status_style}]{status}[/{status_style}]"
            )
        
        self.console.print(table)
        self.console.print()
    
    def _set_active_subscription(self, subscription_id: str) -> bool:
        """Set the specified subscription as active"""
        try:
            result = subprocess.run(
                ['az', 'account', 'set', '--subscription', subscription_id],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                self.console.print(f"🔄 Set active subscription: [bold blue]{subscription_id}[/bold blue]")
                return True
            else:
                logger.error(f"Failed to set subscription: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting subscription: {str(e)}")
            return False 