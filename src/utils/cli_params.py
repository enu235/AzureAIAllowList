"""
CLI Parameter Groups

Organized parameter groups for click options to reduce clutter in main function.
"""

import click
from typing import Any, Callable


def core_options(func: Callable) -> Callable:
    """Core application options"""
    func = click.option('--action', 
                       type=click.Choice(['package-allowlist', 'analyze-connectivity'], case_sensitive=False),
                       default='package-allowlist',
                       help='Action to perform: package-allowlist (default) or analyze-connectivity')(func)
    
    func = click.option('--interactive', is_flag=True, default=False,
                       help='Run in interactive mode (auto-enabled if no workspace specified)')(func)
    
    func = click.option('--verbose', '-v', is_flag=True,
                       help='Enable verbose logging')(func)
    
    func = click.option('--dry-run', is_flag=True,
                       help='Show what would be discovered without making API calls')(func)
    
    return func


def workspace_options(func: Callable) -> Callable:
    """Workspace and Azure resource options"""
    func = click.option('--workspace-name', '-w', 
                       help='Azure ML workspace or AI Foundry hub name (required for non-interactive mode)')(func)
    
    func = click.option('--resource-group', '-g',
                       help='Azure resource group name (required for non-interactive mode)')(func)
    
    func = click.option('--subscription-id', '-s', 
                       help='Azure subscription ID (uses current if not specified)')(func)
    
    func = click.option('--hub-type', 
                       type=click.Choice(['ai-foundry', 'azure-ml'], case_sensitive=False),
                       default='ai-foundry', 
                       help='Hub type: AI Foundry hub or Azure ML workspace (default: ai-foundry)')(func)
    
    return func


def package_file_options(func: Callable) -> Callable:
    """Package file input options"""
    func = click.option('--requirements-file', '-r', type=click.Path(exists=True),
                       help='Path to requirements.txt file')(func)
    
    func = click.option('--conda-env', '-c', type=click.Path(exists=True),
                       help='Path to conda environment.yml file')(func)
    
    func = click.option('--pyproject-toml', '-p', type=click.Path(exists=True),
                       help='Path to pyproject.toml file')(func)
    
    func = click.option('--pipfile', type=click.Path(exists=True),
                       help='Path to Pipfile')(func)
    
    return func


def output_options(func: Callable) -> Callable:
    """Output format and file options"""
    func = click.option('--output-format', '-o', 
                       type=click.Choice(['cli', 'json', 'yaml', 'powershell'], case_sensitive=False),
                       default='cli', help='Output format: cli (bash), json, yaml, powershell (default: cli)')(func)
    
    func = click.option('--output-file', type=click.Path(),
                       help='Output file path (default: stdout)')(func)
    
    return func


def package_discovery_options(func: Callable) -> Callable:
    """Package discovery behavior options"""
    func = click.option('--include-transitive', is_flag=True, default=True,
                       help='Include transitive dependencies (default: True)')(func)
    
    func = click.option('--platform', type=click.Choice(['linux', 'windows', 'auto']),
                       default='auto', help='Target platform (default: auto-detect)')(func)
    
    return func


def ai_foundry_options(func: Callable) -> Callable:
    """Azure AI Foundry specific feature options"""
    func = click.option('--include-vscode', is_flag=True,
                       help='Include Visual Studio Code integration FQDNs (AI Foundry)')(func)
    
    func = click.option('--include-huggingface', is_flag=True,
                       help='Include HuggingFace model access FQDNs (AI Foundry)')(func)
    
    func = click.option('--include-prompt-flow', is_flag=True,
                       help='Include Prompt Flow service FQDNs (AI Foundry)')(func)
    
    func = click.option('--custom-fqdns', 
                       help='Comma-separated list of additional custom FQDNs to include')(func)
    
    return func


def all_options(func: Callable) -> Callable:
    """Apply all option groups to a function"""
    func = core_options(func)
    func = workspace_options(func)
    func = package_file_options(func)
    func = output_options(func)
    func = package_discovery_options(func)
    func = ai_foundry_options(func)
    return func


class CliConfig:
    """Container for CLI configuration parameters"""
    
    def __init__(self, **kwargs):
        # Core options
        self.action = kwargs.get('action', 'package-allowlist')
        self.interactive = kwargs.get('interactive', False)
        self.verbose = kwargs.get('verbose', False)
        self.dry_run = kwargs.get('dry_run', False)
        
        # Workspace options
        self.workspace_name = kwargs.get('workspace_name')
        self.resource_group = kwargs.get('resource_group')
        self.subscription_id = kwargs.get('subscription_id')
        self.hub_type = kwargs.get('hub_type', 'ai-foundry')
        
        # Package file options
        self.requirements_file = kwargs.get('requirements_file')
        self.conda_env = kwargs.get('conda_env')
        self.pyproject_toml = kwargs.get('pyproject_toml')
        self.pipfile = kwargs.get('pipfile')
        
        # Output options
        self.output_format = kwargs.get('output_format', 'cli')
        self.output_file = kwargs.get('output_file')
        
        # Package discovery options
        self.include_transitive = kwargs.get('include_transitive', True)
        self.platform = kwargs.get('platform', 'auto')
        
        # AI Foundry options
        self.include_vscode = kwargs.get('include_vscode', False)
        self.include_huggingface = kwargs.get('include_huggingface', False)
        self.include_prompt_flow = kwargs.get('include_prompt_flow', False)
        self.custom_fqdns = kwargs.get('custom_fqdns')
    
    def should_run_interactive(self) -> bool:
        """Determine if interactive mode should be used"""
        return self.interactive or (not self.workspace_name or not self.resource_group)
    
    def get_input_files(self) -> list:
        """Get list of input package files"""
        input_files = []
        if self.requirements_file:
            input_files.append(('pip', self.requirements_file))
        if self.conda_env:
            input_files.append(('conda', self.conda_env))
        if self.pyproject_toml:
            input_files.append(('pyproject', self.pyproject_toml))
        if self.pipfile:
            input_files.append(('pipfile', self.pipfile))
        return input_files
    
    def get_enabled_features(self) -> list:
        """Get list of enabled AI Foundry features"""
        features = []
        if self.include_vscode:
            features.append("Visual Studio Code")
        if self.include_huggingface:
            features.append("HuggingFace")
        if self.include_prompt_flow:
            features.append("Prompt Flow")
        if self.custom_fqdns:
            features.append("Custom FQDNs")
        return features 