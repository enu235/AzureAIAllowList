#!/usr/bin/env python3
"""
Azure ML Package URL Allowlist Tool

A tool to discover package download URLs and generate Azure ML workspace 
outbound rules for secured environments.

Now supports both Azure Machine Learning workspaces and Azure AI Foundry Hubs.

Author: Community Tool
License: MIT
"""

import click
import sys
import os
from pathlib import Path
from typing import List, Optional
import json

from src.workspace_analyzer import WorkspaceAnalyzerFactory
from src.package_discoverer import PackageDiscovererFactory
from src.output_formatter import OutputFormatterFactory
from src.utils.logger import setup_logger
from src.utils.validators import validate_azure_cli
from src.config.messages import MessageTemplates
from src.config.hub_features import HubFeatureManager
from src.connectivity.connectivity_analyzer import ConnectivityAnalyzer

# Setup logging
logger = setup_logger(__name__)

@click.command()
@click.option('--action', 
              type=click.Choice(['package-allowlist', 'analyze-connectivity'], case_sensitive=False),
              default='package-allowlist',
              help='Action to perform: package-allowlist (default) or analyze-connectivity')
@click.option('--workspace-name', '-w', required=True, 
              help='Azure ML workspace or AI Foundry hub name')
@click.option('--resource-group', '-g', required=True,
              help='Azure resource group name')
@click.option('--subscription-id', '-s', 
              help='Azure subscription ID (uses current if not specified)')
@click.option('--hub-type', 
              type=click.Choice(['ai-foundry', 'azure-ml'], case_sensitive=False),
              default='ai-foundry', 
              help='Hub type: AI Foundry hub or Azure ML workspace (default: ai-foundry)')
@click.option('--requirements-file', '-r', type=click.Path(exists=True),
              help='Path to requirements.txt file')
@click.option('--conda-env', '-c', type=click.Path(exists=True),
              help='Path to conda environment.yml file')
@click.option('--pyproject-toml', '-p', type=click.Path(exists=True),
              help='Path to pyproject.toml file')
@click.option('--pipfile', type=click.Path(exists=True),
              help='Path to Pipfile')
@click.option('--output-format', '-o', 
              type=click.Choice(['cli', 'json', 'yaml'], case_sensitive=False),
              default='cli', help='Output format (default: cli)')
@click.option('--include-transitive', is_flag=True, default=True,
              help='Include transitive dependencies (default: True)')
@click.option('--platform', type=click.Choice(['linux', 'windows', 'auto']),
              default='auto', help='Target platform (default: auto-detect)')
@click.option('--output-file', type=click.Path(),
              help='Output file path (default: stdout)')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
@click.option('--dry-run', is_flag=True,
              help='Show what would be discovered without making API calls')
# Azure AI Foundry Feature Flags
@click.option('--include-vscode', is_flag=True,
              help='Include Visual Studio Code integration FQDNs (AI Foundry)')
@click.option('--include-huggingface', is_flag=True,
              help='Include HuggingFace model access FQDNs (AI Foundry)')
@click.option('--include-prompt-flow', is_flag=True,
              help='Include Prompt Flow service FQDNs (AI Foundry)')
@click.option('--custom-fqdns', 
              help='Comma-separated list of additional custom FQDNs to include')
def main(action: str, workspace_name: str, resource_group: str, subscription_id: Optional[str],
         hub_type: str, requirements_file: Optional[str], conda_env: Optional[str],
         pyproject_toml: Optional[str], pipfile: Optional[str],
         output_format: str, include_transitive: bool, platform: str,
         output_file: Optional[str], verbose: bool, dry_run: bool,
         include_vscode: bool, include_huggingface: bool, include_prompt_flow: bool,
         custom_fqdns: Optional[str]):
    """
    Azure AI Foundry & Machine Learning Package Allowlist Tool
    
    Discovers package download URLs and generates Azure AI Foundry hub/Azure ML workspace 
    outbound rules for secured environments.
    
    Supports both Azure AI Foundry Hubs and Azure Machine Learning workspaces.
    
    🚨 DISCLAIMER: This tool is provided "AS IS" without warranty of any kind, express or implied. 
    You use this tool and implement its recommendations at your own risk. Always review and test 
    configurations in non-production environments before applying to production systems.
    """
    
    if verbose:
        logger.setLevel('DEBUG')
    
    try:
        # Route based on action
        if action == 'analyze-connectivity':
            # Validate minimum required parameters for connectivity analysis
            if not workspace_name or not resource_group:
                click.echo("❌ Workspace name and resource group are required for connectivity analysis.", err=True)
                sys.exit(1)
            
            # Create and run connectivity analyzer
            click.echo(f"🔍 Starting connectivity analysis for {hub_type} workspace: {workspace_name}")
            click.echo()
            
            analyzer = ConnectivityAnalyzer(
                workspace_name=workspace_name,
                resource_group=resource_group,
                subscription_id=subscription_id,
                hub_type=hub_type.lower(),
                verbose=verbose
            )
            
            result = analyzer.analyze()
            
            if result.success:
                # Display comprehensive summary using Phase 4 reporting
                from src.output_formatter import OutputFormatter
                formatter = OutputFormatter(verbose=verbose)
                summary = formatter.format_connectivity_summary(result.data)
                click.echo(summary)
                
                click.echo(f"\n✅ {result.message}")
                
                # Report location
                if 'report_location' in result.data:
                    click.echo(f"\n📄 Detailed report saved to: {result.data['report_location']}")
                    click.echo(f"   JSON data saved to: {result.data['report_location'].replace('.md', '.json')}")
            else:
                click.echo(f"\n❌ {result.message}", err=True)
                if result.error:
                    click.echo(f"Error: {result.error}", err=True)
                sys.exit(1)
            
            return
        
        # Execute existing package allowlist functionality
        # Validate Azure CLI setup
        if not dry_run and not validate_azure_cli():
            click.echo("❌ Azure CLI validation failed. Please run 'az login' and install the ML extension.", err=True)
            sys.exit(1)
        
        # Collect input files
        input_files = []
        if requirements_file:
            input_files.append(('pip', requirements_file))
        if conda_env:
            input_files.append(('conda', conda_env))
        if pyproject_toml:
            input_files.append(('pyproject', pyproject_toml))
        if pipfile:
            input_files.append(('pipfile', pipfile))
        
        if not input_files:
            click.echo("❌ No input files specified. Please provide at least one package file.", err=True)
            sys.exit(1)
        
        # Display disclaimer and hub type info
        click.echo(MessageTemplates.get_disclaimer())
        click.echo()
        
        # Display hub type information
        hub_type_lower = hub_type.lower()
        if hub_type_lower == 'ai-foundry':
            click.echo("🔮 Targeting Azure AI Foundry Hub")
            click.echo("   Enhanced with AI-specific features and integrations")
        else:
            click.echo("🤖 Targeting Azure Machine Learning Workspace")
            click.echo("   Classic ML workspace configuration")
        click.echo()
        
        # Analyze workspace (if not dry-run)
        workspace_analyzer = None
        if not dry_run:
            click.echo("🔍 Analyzing workspace/hub configuration...")
            analyzer_factory = WorkspaceAnalyzerFactory()
            workspace_analyzer = analyzer_factory.create_analyzer(
                workspace_name, resource_group, subscription_id, hub_type_lower
            )
            workspace_config = workspace_analyzer.analyze()
            
            # Display workspace info
            click.echo(f"📊 Workspace/Hub: {workspace_config.name}")
            click.echo(f"📊 Network Mode: {workspace_config.network_mode}")
            click.echo(f"📊 Isolation Mode: {workspace_config.isolation_mode or 'Not applicable'}")
            click.echo()
        
        # Discover package URLs
        click.echo("🔍 Discovering package download URLs...")
        all_domains = set()
        private_repos = []
        platform_warnings = []
        
        for package_type, file_path in input_files:
            click.echo(f"  📦 Processing {package_type} file: {file_path}")
            
            discoverer = PackageDiscovererFactory.create_discoverer(package_type)
            
            try:
                result = discoverer.discover_urls(
                    file_path, 
                    include_transitive=include_transitive,
                    platform=platform,
                    dry_run=dry_run
                )
                
                all_domains.update(result.domains)
                private_repos.extend(result.private_repositories)
                platform_warnings.extend(result.platform_warnings)
                
                click.echo(f"    ✅ Found {len(result.domains)} unique domains")
                
            except Exception as e:
                click.echo(f"    ❌ Error processing {file_path}: {str(e)}", err=True)
                continue
        
        # Add hub-specific feature domains
        feature_manager = HubFeatureManager(hub_type_lower)
        
        # Process feature flags
        if include_vscode:
            vscode_domains = feature_manager.get_vscode_domains()
            all_domains.update(vscode_domains)
            click.echo(f"  🔧 Added {len(vscode_domains)} Visual Studio Code domains")
        
        if include_huggingface:
            hf_domains = feature_manager.get_huggingface_domains()
            all_domains.update(hf_domains)
            click.echo(f"  🤗 Added {len(hf_domains)} HuggingFace domains")
        
        if include_prompt_flow:
            pf_domains = feature_manager.get_prompt_flow_domains()
            all_domains.update(pf_domains)
            click.echo(f"  🌊 Added {len(pf_domains)} Prompt Flow domains")
        
        # Add custom FQDNs if provided
        if custom_fqdns:
            custom_domains = [domain.strip() for domain in custom_fqdns.split(',')]
            all_domains.update(custom_domains)
            click.echo(f"  ⚙️  Added {len(custom_domains)} custom domains")
        
        # Add hub-specific base domains
        base_domains = feature_manager.get_base_domains()
        all_domains.update(base_domains)
        
        # Display warnings
        if platform_warnings:
            click.echo("\n⚠️  Platform Considerations:")
            for warning in set(platform_warnings):
                click.echo(f"    {warning}")
        
        if private_repos:
            click.echo("\n🔒 Private Repository Detected:")
            for repo in set(private_repos):
                click.echo(f"    {repo}")
            click.echo(MessageTemplates.get_private_repo_guidance())
        
        # Generate output
        click.echo(f"\n📝 Generating {output_format.upper()} output...")
        
        formatter_factory = OutputFormatterFactory()
        formatter = formatter_factory.create_formatter(
            output_format, 
            workspace_name, 
            resource_group, 
            subscription_id,
            hub_type_lower
        )
        
        output_content = formatter.format_domains(list(all_domains))
        
        # Output results
        if output_file:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w') as f:
                f.write(output_content)
            click.echo(f"✅ Output written to: {output_file}")
        else:
            click.echo("\n" + "="*80)
            click.echo("🎯 GENERATED CONFIGURATION:")
            click.echo("="*80)
            click.echo(output_content)
            click.echo("="*80)
        
        # Display summary
        click.echo(f"\n📊 Summary:")
        click.echo(f"   • {len(all_domains)} unique domains discovered")
        click.echo(f"   • {len(private_repos)} private repositories detected")
        click.echo(f"   • {len(input_files)} input files processed")
        click.echo(f"   • Hub type: {hub_type}")
        
        # Display feature summary
        enabled_features = []
        if include_vscode:
            enabled_features.append("Visual Studio Code")
        if include_huggingface:
            enabled_features.append("HuggingFace")
        if include_prompt_flow:
            enabled_features.append("Prompt Flow")
        if custom_fqdns:
            enabled_features.append("Custom FQDNs")
        
        if enabled_features:
            click.echo(f"   • Features enabled: {', '.join(enabled_features)}")
        
        # Display final disclaimer
        click.echo(MessageTemplates.get_final_disclaimer())
        
    except KeyboardInterrupt:
        click.echo("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 