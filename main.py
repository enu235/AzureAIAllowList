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
import traceback
from pathlib import Path
from typing import List, Optional
import json

from src.workspace_analyzer import WorkspaceAnalyzerFactory
from src.package_discoverer import PackageDiscovererFactory
from src.output_formatter import OutputFormatterFactory, OutputFormatter
from src.utils.logger import setup_logger
from src.utils.validators import validate_azure_cli
from src.utils.cli_params import all_options, CliConfig
from src.config.messages import MessageTemplates
from src.config.hub_features import HubFeatureManager
from src.connectivity.connectivity_analyzer import ConnectivityAnalyzer
from src.connectivity.comparison_analyzer import ComparisonAnalyzer
from src.interactive.interactive_flow import InteractiveFlow

# Setup logging
logger = setup_logger(__name__)

def run_interactive_mode(verbose: bool = False) -> None:
    """Run the tool in interactive mode"""
    try:
        # Initialize interactive flow
        interactive_flow = InteractiveFlow()
        
        # Run interactive configuration
        config = interactive_flow.run()
        if not config:
            return  # User cancelled or error occurred
        
        # Execute analysis based on configuration
        subscription_id = config['subscription']['id']
        analysis_type = config['analysis_type']
        workspaces = config['workspaces']
        package_config = config['package_analysis']
        ai_features_config = config['ai_features']  # Extract AI features separately
        
        if analysis_type == 'compare':
            # Run comparison analysis
            run_comparison_analysis(workspaces, subscription_id, package_config, ai_features_config)
        else:
            # Run standard analysis
            run_standard_analysis(workspaces, subscription_id, package_config, ai_features_config, config)
            
    except Exception as e:
        logger.error(f"Interactive mode error: {str(e)}")
        click.echo(f"❌ [bold red]Interactive mode failed: {str(e)}[/bold red]", err=True)
        sys.exit(1)

def run_comparison_analysis(workspaces: List, subscription_id: str, package_config: Optional[dict], ai_features_config: Optional[dict]) -> None:
    """Run comparison analysis between two workspaces"""
    if len(workspaces) != 2:
        click.echo("❌ Comparison mode requires exactly 2 workspaces", err=True)
        return
    
    # Convert WorkspaceInfo objects to dicts for the analyzer
    ws1_info = {
        'name': workspaces[0].name,
        'resource_group': workspaces[0].resource_group,
        'hub_type': workspaces[0].hub_type
    }
    ws2_info = {
        'name': workspaces[1].name,
        'resource_group': workspaces[1].resource_group,
        'hub_type': workspaces[1].hub_type
    }
    
    # Run comparison
    comparison_analyzer = ComparisonAnalyzer()
    comparison_result = comparison_analyzer.compare_workspaces(ws1_info, ws2_info, subscription_id)
    
    # Generate package comparison if requested
    if package_config and package_config.get('files'):
        click.echo("\n📦 Running package analysis for both workspaces...")
        
        # Run package analysis for both workspaces
        for i, workspace in enumerate(workspaces, 1):
            click.echo(f"\n🔍 Package analysis for workspace {i}: {workspace.name}")
            run_package_analysis_for_workspace(workspace, subscription_id, package_config, ai_features_config)

def run_standard_analysis(workspaces: List, subscription_id: str, package_config: Optional[dict], ai_features_config: Optional[dict], config: dict) -> None:
    """Run standard analysis for one or more workspaces"""
    results = []
    
    for workspace in workspaces:
        click.echo(f"\n🔍 Analyzing: {workspace.name} ({workspace.hub_type})")
        
        # Run connectivity analysis
        analyzer = ConnectivityAnalyzer(
            workspace_name=workspace.name,
            resource_group=workspace.resource_group,
            subscription_id=subscription_id,
            hub_type=workspace.hub_type,
            verbose=True
        )
        
        result = analyzer.analyze()
        if result.success:
            results.append({
                'workspace': workspace,
                'connectivity': result.data
            })
            click.echo(f"✅ Connectivity analysis completed for {workspace.name}")
        else:
            click.echo(f"❌ Connectivity analysis failed for {workspace.name}: {result.message}")
        
        # Run package analysis if requested
        if package_config and package_config.get('files'):
            click.echo(f"\n📦 Running package analysis for {workspace.name}...")
            run_package_analysis_for_workspace(workspace, subscription_id, package_config, ai_features_config)
    
    # Generate combined summary if multiple workspaces
    if len(results) > 1:
        click.echo(f"\n📊 Combined Analysis Summary ({len(results)} workspaces)")
        for result in results:
            ws = result['workspace']
            click.echo(f"   • {ws.name} ({ws.hub_type}) - {ws.resource_group}")

def run_package_analysis_for_workspace(workspace, subscription_id: str, package_config: dict, ai_features_config: Optional[dict]) -> None:
    """Run package analysis for a single workspace"""
    try:
        # Collect package files
        input_files = package_config.get('files', [])
        if not input_files:
            click.echo("⚠️  No package files configured")
            return
        
        # Discover package URLs
        all_domains = set()
        private_repos = []
        
        discoverer_factory = PackageDiscovererFactory()
        
        for file_type, file_path in input_files:
            discoverer = discoverer_factory.create_discoverer(file_type)
            
            result = discoverer.discover_urls(
                file_path, 
                include_transitive=package_config.get('include_transitive', True),
                platform=package_config.get('platform', 'auto'),
                dry_run=False
            )
            
            domains = result.domains
            private = result.private_repositories
            
            all_domains.update(domains)
            private_repos.extend(private)
        
        # Apply AI Foundry features if applicable
        if workspace.hub_type == 'ai-foundry':
            feature_manager = HubFeatureManager()
            
            # Handle AI features - could be None, from interactive mode, or from CLI flags
            if ai_features_config:
                ai_domains = feature_manager.get_feature_domains(
                    include_vscode=ai_features_config.get('include_vscode', False),
                    include_huggingface=ai_features_config.get('include_huggingface', False),
                    include_prompt_flow=ai_features_config.get('include_prompt_flow', False),
                    custom_fqdns=ai_features_config.get('custom_fqdns', '')
                )
                all_domains.update(ai_domains)
        
        # Generate output
        formatter_factory = OutputFormatterFactory()
        formatter = formatter_factory.create_formatter(
            'cli', 
            workspace.name, 
            workspace.resource_group, 
            subscription_id,
            workspace.hub_type
        )
        
        output_content = formatter.format_domains(list(all_domains))
        
        # Display results
        click.echo(f"\n📋 Package Analysis Results for {workspace.name}:")
        click.echo("="*80)
        click.echo(output_content)
        click.echo("="*80)
        click.echo(f"📊 Summary: {len(all_domains)} unique domains discovered")
        
    except Exception as e:
        click.echo(f"❌ Package analysis failed for {workspace.name}: {str(e)}")
        logger.error(f"Package analysis error for {workspace.name}: {str(e)}")

@click.command()
@all_options
def main(**kwargs):
    """
    Azure AI Foundry & Machine Learning Package Allowlist Tool
    
    Discovers package download URLs and generates Azure AI Foundry hub/Azure ML workspace 
    outbound rules for secured environments.
    
    Supports both Azure AI Foundry Hubs and Azure Machine Learning workspaces.
    
    🚨 DISCLAIMER: This tool is provided "AS IS" without warranty of any kind, express or implied. 
    You use this tool and implement its recommendations at your own risk. Always review and test 
    configurations in non-production environments before applying to production systems.
    """
    
    # Create configuration object from CLI parameters
    config = CliConfig(**kwargs)
    
    if config.verbose:
        logger.setLevel('DEBUG')
    
    # Determine if we should run in interactive mode
    should_run_interactive = config.should_run_interactive()
    
    # Run interactive mode if requested or required
    if should_run_interactive:
        return run_interactive_mode(config.verbose)
    
    # Validate required parameters for non-interactive mode
    if not config.workspace_name or not config.resource_group:
        click.echo("❌ Workspace name and resource group are required for non-interactive mode.", err=True)
        click.echo("💡 Run without parameters or use --interactive for guided setup.", err=True)
        sys.exit(1)
    
    try:
        # Route based on action
        if config.action == 'analyze-connectivity':
            # Validate minimum required parameters for connectivity analysis
            if not config.workspace_name or not config.resource_group:
                click.echo("❌ Workspace name and resource group are required for connectivity analysis.", err=True)
                sys.exit(1)
            
            # Create and run connectivity analyzer
            click.echo(f"🔍 Starting connectivity analysis for {config.hub_type} workspace: {config.workspace_name}")
            click.echo()
            
            analyzer = ConnectivityAnalyzer(
                workspace_name=config.workspace_name,
                resource_group=config.resource_group,
                subscription_id=config.subscription_id,
                hub_type=config.hub_type.lower(),
                verbose=config.verbose
            )
            
            result = analyzer.analyze()
            
            if result.success:
                # Display comprehensive summary using Phase 4 reporting
                formatter = OutputFormatter(verbose=config.verbose)
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
        if not config.dry_run and not validate_azure_cli():
            click.echo("❌ Azure CLI validation failed. Please run 'az login' and install the ML extension.", err=True)
            sys.exit(1)
        
        # Collect input files using the new utility method
        input_files = config.get_input_files()
        
        if not input_files:
            click.echo("❌ No input files specified. Please provide at least one package file.", err=True)
            sys.exit(1)
        
        # Display disclaimer and hub type info
        click.echo(MessageTemplates.get_disclaimer())
        click.echo()
        
        # Display hub type information
        hub_type_lower = config.hub_type.lower()
        if hub_type_lower == 'ai-foundry':
            click.echo("🔮 Targeting Azure AI Foundry Hub")
            click.echo("   Enhanced with AI-specific features and integrations")
        else:
            click.echo("🤖 Targeting Azure Machine Learning Workspace")
            click.echo("   Classic ML workspace configuration")
        click.echo()
        
        # Analyze workspace (if not dry-run)
        workspace_analyzer = None
        if not config.dry_run:
            click.echo("🔍 Analyzing workspace/hub configuration...")
            analyzer_factory = WorkspaceAnalyzerFactory()
            workspace_analyzer = analyzer_factory.create_analyzer(
                config.workspace_name, config.resource_group, config.subscription_id, hub_type_lower
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
                    include_transitive=config.include_transitive,
                    platform=config.platform,
                    dry_run=config.dry_run
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
        if config.include_vscode:
            vscode_domains = feature_manager.get_vscode_domains()
            all_domains.update(vscode_domains)
            click.echo(f"  🔧 Added {len(vscode_domains)} Visual Studio Code domains")
        
        if config.include_huggingface:
            hf_domains = feature_manager.get_huggingface_domains()
            all_domains.update(hf_domains)
            click.echo(f"  🤗 Added {len(hf_domains)} HuggingFace domains")
        
        if config.include_prompt_flow:
            pf_domains = feature_manager.get_prompt_flow_domains()
            all_domains.update(pf_domains)
            click.echo(f"  🌊 Added {len(pf_domains)} Prompt Flow domains")
        
        # Add custom FQDNs if provided
        if config.custom_fqdns:
            custom_domains = [domain.strip() for domain in config.custom_fqdns.split(',')]
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
        click.echo(f"\n📝 Generating {config.output_format.upper()} output...")
        
        formatter_factory = OutputFormatterFactory()
        formatter = formatter_factory.create_formatter(
            config.output_format, 
            config.workspace_name, 
            config.resource_group, 
            config.subscription_id,
            hub_type_lower
        )
        
        output_content = formatter.format_domains(list(all_domains))
        
        # Output results
        if config.output_file:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(config.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            with open(config.output_file, 'w') as f:
                f.write(output_content)
            click.echo(f"✅ Output written to: {config.output_file}")
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
        click.echo(f"   • Hub type: {config.hub_type}")
        
        # Display feature summary using the new utility method
        enabled_features = config.get_enabled_features()
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
        if config.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 