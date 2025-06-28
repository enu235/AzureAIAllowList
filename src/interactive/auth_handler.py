"""
Azure CLI Authentication Handler for Interactive Mode
"""

import subprocess
import json
import sys
from typing import Optional, Dict
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class AuthHandler:
    """Handles Azure CLI authentication for interactive mode"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        
    def check_and_ensure_login(self) -> bool:
        """
        Check if user is logged in to Azure CLI, prompt for login if not.
        
        Returns:
            True if authentication successful, False otherwise
        """
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]🔐 Azure CLI Authentication Check[/bold cyan]",
            border_style="cyan"
        ))
        
        if self._is_logged_in():
            current_user = self._get_current_user()
            self.console.print(f"✅ Already logged in as: [bold green]{current_user}[/bold green]")
            return True
        
        self.console.print("❌ Not logged in to Azure CLI")
        self.console.print("🔄 Initiating Azure login process...")
        
        return self._perform_login()
    
    def _is_logged_in(self) -> bool:
        """Check if user is currently logged in to Azure CLI"""
        try:
            result = subprocess.run(
                ['az', 'account', 'show'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _get_current_user(self) -> str:
        """Get current Azure CLI user information"""
        try:
            result = subprocess.run(
                ['az', 'account', 'show', '--query', 'user.name', '-o', 'tsv'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "Unknown User"
    
    def _perform_login(self) -> bool:
        """Perform Azure CLI login"""
        try:
            self.console.print("🌐 Opening browser for Azure authentication...")
            self.console.print("💡 Please complete the login process in your browser")
            
            # Run az login in interactive mode
            result = subprocess.run(['az', 'login'], timeout=300)
            
            if result.returncode == 0:
                self.console.print("✅ [bold green]Login successful![/bold green]")
                
                # Verify login worked
                if self._is_logged_in():
                    current_user = self._get_current_user()
                    self.console.print(f"👤 Logged in as: [bold green]{current_user}[/bold green]")
                    return True
                
            self.console.print("❌ [bold red]Login failed or was cancelled[/bold red]")
            return False
            
        except subprocess.TimeoutExpired:
            self.console.print("❌ [bold red]Login timed out (5 minutes)[/bold red]")
            return False
        except KeyboardInterrupt:
            self.console.print("\n❌ [bold red]Login cancelled by user[/bold red]")
            return False
        except Exception as e:
            self.console.print(f"❌ [bold red]Login error: {str(e)}[/bold red]")
            return False
    
    def validate_ml_extension(self) -> bool:
        """Validate that the ML extension is installed"""
        try:
            result = subprocess.run(
                ['az', 'extension', 'list', '--query', '[?name==`ml`].name', '-o', 'tsv'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and 'ml' in result.stdout:
                return True
                
            self.console.print("❌ Azure ML extension not found")
            self.console.print("🔧 Installing Azure ML extension...")
            
            install_result = subprocess.run(
                ['az', 'extension', 'add', '-n', 'ml'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if install_result.returncode == 0:
                self.console.print("✅ [bold green]Azure ML extension installed successfully[/bold green]")
                return True
            else:
                self.console.print(f"❌ [bold red]Failed to install ML extension: {install_result.stderr}[/bold red]")
                return False
                
        except Exception as e:
            self.console.print(f"❌ [bold red]Error checking ML extension: {str(e)}[/bold red]")
            return False 