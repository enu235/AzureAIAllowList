"""
Analysis Selector for Interactive Mode
"""

import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import questionary

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class AnalysisSelector:
    """Handles analysis type selection and configuration"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        
    def select_analysis_type(self) -> Optional[str]:
        """
        Select the type of analysis to perform.
        
        Returns:
            'standard' for standard analysis, 'compare' for comparison, None if cancelled
        """
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]📊 Analysis Type Selection[/bold cyan]",
            border_style="cyan"
        ))
        
        choices = [
            {
                'name': '📋 Standard Analysis - Analyze one or more workspaces',
                'value': 'standard'
            },
            {
                'name': '⚖️  Compare Analysis - Compare two workspaces side-by-side',
                'value': 'compare'
            }
        ]
        
        try:
            selected = questionary.select(
                "What type of analysis would you like to perform?",
                choices=choices,
                style=questionary.Style([
                    ('question', 'bold'),
                    ('answer', 'fg:#ff9d00 bold'),
                    ('pointer', 'fg:#ff9d00 bold'),
                    ('highlighted', 'fg:#ff9d00 bold'),
                ])
            ).ask()
            
            if selected:
                analysis_type = "Standard" if selected == 'standard' else "Comparison"
                self.console.print(f"✅ Selected: [bold green]{analysis_type} Analysis[/bold green]")
                return selected
            else:
                return None
                
        except KeyboardInterrupt:
            self.console.print("\n❌ Selection cancelled")
            return None
    
    def configure_package_analysis(self) -> Optional[Dict]:
        """
        Configure package analysis settings.
        
        Returns:
            Dict with package analysis configuration, or None if not requested
        """
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]📦 Package Analysis Configuration[/bold cyan]",
            border_style="cyan"
        ))
        
        # Ask if user wants package analysis
        try:
            enable_package_analysis = questionary.confirm(
                "Would you like to include package analysis (allowlist generation)?",
                default=False
            ).ask()
            
            if not enable_package_analysis:
                self.console.print("ℹ️  Package analysis [bold yellow]disabled[/bold yellow] - connectivity analysis only")
                return None
            
            self.console.print("✅ Package analysis [bold green]enabled[/bold green]")
            
            # Configure package analysis settings
            package_config = self._configure_package_settings()
            return package_config
            
        except KeyboardInterrupt:
            self.console.print("\n❌ Configuration cancelled")
            return None
    
    def _configure_package_settings(self) -> Dict:
        """Configure specific package analysis settings"""
        config = {
            'enabled': True,
            'files': [],
            'include_transitive': True,
            'platform': 'auto'
        }
        
        # Discover package files in current directory
        discovered_files = self._discover_package_files()
        
        if discovered_files:
            self.console.print("\n🔍 [bold green]Discovered package files in current directory:[/bold green]")
            for file_type, file_path in discovered_files:
                self.console.print(f"   📄 {file_path} ({file_type})")
            
            # Ask if user wants to use discovered files
            use_discovered = questionary.confirm(
                "Use the discovered package files above?",
                default=True
            ).ask()
            
            if use_discovered:
                config['files'] = discovered_files
            else:
                config['files'] = self._manual_file_selection()
        else:
            self.console.print("\n📂 No package files found in current directory")
            config['files'] = self._manual_file_selection()
        
        # Configure additional settings
        config['include_transitive'] = questionary.confirm(
            "Include transitive dependencies?",
            default=True
        ).ask()
        
        platform_choices = [
            {'name': '🔄 Auto-detect platform', 'value': 'auto'},
            {'name': '🐧 Linux', 'value': 'linux'},
            {'name': '🪟 Windows', 'value': 'windows'}
        ]
        
        config['platform'] = questionary.select(
            "Target platform:",
            choices=platform_choices
        ).ask()
        
        return config
    
    def _discover_package_files(self) -> List[Tuple[str, str]]:
        """Discover package files in current directory"""
        discovered = []
        current_dir = Path.cwd()
        
        # Common package file patterns
        patterns = {
            'requirements.txt': 'pip',
            'environment.yml': 'conda', 
            'environment.yaml': 'conda',
            'pyproject.toml': 'pyproject',
            'Pipfile': 'pipfile'
        }
        
        for pattern, file_type in patterns.items():
            files = list(current_dir.glob(pattern))
            for file in files:
                discovered.append((file_type, str(file)))
        
        return discovered
    
    def _manual_file_selection(self) -> List[Tuple[str, str]]:
        """Manual package file selection"""
        files = []
        
        self.console.print("\n📁 [bold yellow]Manual file selection:[/bold yellow]")
        
        add_more = True
        while add_more:
            file_path = questionary.path(
                "Enter path to package file (or press Enter to skip):",
                only_directories=False
            ).ask()
            
            if file_path and os.path.exists(file_path):
                # Detect file type
                file_type = self._detect_file_type(file_path)
                files.append((file_type, file_path))
                self.console.print(f"✅ Added: {file_path} ({file_type})")
                
                add_more = questionary.confirm("Add another package file?", default=False).ask()
            else:
                add_more = False
        
        return files
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect package file type from filename"""
        file_name = os.path.basename(file_path).lower()
        
        if file_name == 'requirements.txt':
            return 'pip'
        elif file_name in ['environment.yml', 'environment.yaml']:
            return 'conda'
        elif file_name == 'pyproject.toml':
            return 'pyproject'
        elif file_name == 'pipfile':
            return 'pipfile'
        else:
            # Ask user to specify
            choices = [
                {'name': 'pip (requirements.txt format)', 'value': 'pip'},
                {'name': 'conda (environment.yml format)', 'value': 'conda'},
                {'name': 'pyproject.toml (Poetry/uv format)', 'value': 'pyproject'},
                {'name': 'Pipfile (Pipenv format)', 'value': 'pipfile'}
            ]
            
            return questionary.select(
                f"What type of package file is '{file_path}'?",
                choices=choices
            ).ask() or 'pip'
    
    def _configure_ai_features(self) -> Dict:
        """Configure Azure AI Foundry specific features"""
        ai_features = {}
        
        self.console.print("\n🔮 [bold magenta]Azure AI Foundry Features:[/bold magenta]")
        
        ai_features['include_vscode'] = questionary.confirm(
            "Include Visual Studio Code integration FQDNs?",
            default=False
        ).ask()
        
        ai_features['include_huggingface'] = questionary.confirm(
            "Include HuggingFace model access FQDNs?",
            default=False
        ).ask()
        
        ai_features['include_prompt_flow'] = questionary.confirm(
            "Include Prompt Flow service FQDNs?",
            default=False
        ).ask()
        
        # Custom FQDNs
        add_custom = questionary.confirm(
            "Add custom FQDNs (internal services, etc.)?",
            default=False
        ).ask()
        
        if add_custom:
            custom_fqdns_input = questionary.text(
                "Enter custom FQDNs (comma-separated):",
                validate=lambda x: True if x.strip() else "Please enter at least one FQDN"
            ).ask()
            
            if custom_fqdns_input:
                ai_features['custom_fqdns'] = custom_fqdns_input.strip()
        
        return ai_features

    def configure_ai_features(self) -> Optional[Dict]:
        """
        Configure AI features independently of package analysis.
        
        Returns:
            Dict with AI features configuration, or None if not requested
        """
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]🔮 AI Features Configuration[/bold cyan]",
            border_style="cyan"
        ))
        
        # Ask if user wants AI features
        try:
            enable_ai_features = questionary.confirm(
                "Would you like to include AI Foundry features (VSCode, HuggingFace, Prompt Flow)?",
                default=False
            ).ask()
            
            if not enable_ai_features:
                self.console.print("ℹ️  AI features [bold yellow]disabled[/bold yellow]")
                return None
            
            self.console.print("✅ AI features [bold green]enabled[/bold green]")
            
            # Configure AI features settings
            ai_config = self._configure_ai_features()
            return ai_config
            
        except KeyboardInterrupt:
            self.console.print("\n❌ Configuration cancelled")
            return None 