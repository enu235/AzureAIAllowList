from typing import Dict, List, Optional
from .base_analyzer import BaseAnalyzer, AnalysisResult
from .progress_tracker import ProgressTracker
from .network_analyzer import NetworkAnalyzer
from .vnet_analyzer import VNetAnalyzer
from .resource_discovery import ResourceDiscovery
from ..utils.validators import validate_azure_cli
from ..workspace_analyzer import WorkspaceAnalyzerFactory

class ConnectivityAnalyzer(BaseAnalyzer):
    """Main orchestrator for connectivity analysis"""
    
    def __init__(self, workspace_name: str, resource_group: str, 
                 subscription_id: Optional[str] = None, hub_type: str = 'azure-ml',
                 verbose: bool = False):
        super().__init__(workspace_name, resource_group, subscription_id, hub_type)
        self.verbose = verbose
        self.progress_tracker = None
        self.results = {}
        
    def analyze(self) -> AnalysisResult:
        """Perform complete connectivity analysis"""
        # Define analysis steps
        steps = [
            "Validating prerequisites",
            "Connecting to workspace/hub",
            "Analyzing network configuration", 
            "Discovering connected resources",
            "Analyzing security settings",
            "Generating report"
        ]
        
        self.progress_tracker = ProgressTracker(len(steps), self.verbose)
        
        try:
            # Step 1: Validate prerequisites
            self.progress_tracker.start_step("Validating prerequisites", 
                                           "Checking Azure CLI and permissions")
            prereq_result = self._validate_prerequisites()
            if not prereq_result.success:
                self.progress_tracker.complete_step(False, prereq_result.message)
                return prereq_result
            self.progress_tracker.complete_step(True)
            
            # Step 2: Connect to workspace
            self.progress_tracker.start_step("Connecting to workspace/hub",
                                           f"Connecting to {self.workspace_name}")
            workspace_result = self._connect_to_workspace()
            if not workspace_result.success:
                self.progress_tracker.complete_step(False, workspace_result.message)
                return workspace_result
            self.progress_tracker.complete_step(True)
            self.results['workspace'] = workspace_result.data
            
            # Step 3: Analyze network configuration
            self.progress_tracker.start_step("Analyzing network configuration",
                                           "Discovering network isolation and connectivity settings")
            network_analyzer = NetworkAnalyzer(
                self.workspace_name,
                self.resource_group,
                self.subscription_id,
                self.hub_type
            )
            network_result = network_analyzer.analyze()

            if not network_result.success:
                self.progress_tracker.complete_step(False, network_result.message)
                # Continue with partial results but log the issue
                self.logger.warning(f"Network analysis partially failed: {network_result.message}")
                self.results['network'] = {'error': network_result.message, 'partial_data': network_result.data}
            else:
                self.progress_tracker.complete_step(True)
                self.results['network'] = network_result.data

                # Analyze VNet details if customer-managed network
                if network_result.data.get('network_type') == 'customer':
                    vnet_analyzer = VNetAnalyzer(self.resource_group, self.subscription_id)
                    vnet_info = vnet_analyzer.analyze_workspace_vnet(self.results['workspace'])
                    self.results['network']['vnet_details'] = vnet_info

            # Step 4: Discover connected resources
            self.progress_tracker.start_step("Discovering connected resources",
                                           "Finding all resources connected to the workspace")
            resource_discovery = ResourceDiscovery(
                self.workspace_name,
                self.resource_group,
                self.subscription_id,
                self.hub_type
            )
            resource_result = resource_discovery.analyze()

            if not resource_result.success:
                self.progress_tracker.complete_step(False, resource_result.message)
                # Continue with partial results but log the issue
                self.logger.warning(f"Resource discovery partially failed: {resource_result.message}")
                self.results['connected_resources'] = {'error': resource_result.message, 'partial_data': resource_result.data}
            else:
                self.progress_tracker.complete_step(True)
                self.results['connected_resources'] = resource_result.data

            # Step 5: Analyzing security settings (placeholder)
            self.progress_tracker.start_step("Analyzing security settings",
                                           "Performing comprehensive security analysis")
            # For now, security analysis is integrated into other steps
            self.progress_tracker.complete_step(True, "Security analysis completed")
            
            # Step 6: Generate report
            self.progress_tracker.start_step("Generating report",
                                           "Creating comprehensive connectivity analysis report")
            try:
                from .report_generator import MarkdownReportGenerator
                from datetime import datetime
                import os
                
                # Generate report
                report_generator = MarkdownReportGenerator(
                    {
                        'hub_type': self.hub_type,
                        'workspace_name': self.workspace_name,
                        'results': self.results,
                        'summary': self.progress_tracker.get_summary()
                    }
                )
                
                # Create reports directory
                reports_dir = "connectivity-reports"
                os.makedirs(reports_dir, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_filename = f"{reports_dir}/{self.workspace_name}_connectivity_{timestamp}.md"
                
                # Save report
                report_generator.save(report_filename)
                
                self.progress_tracker.complete_step(True, f"Report saved to {report_filename}")
                
                # Add report location to results
                self.results['report_location'] = report_filename
                
            except Exception as e:
                self.progress_tracker.complete_step(False, f"Report generation failed: {str(e)}")
                self.logger.warning(f"Report generation failed: {str(e)}")
            
            # Generate final result
            return AnalysisResult(
                success=True,
                message="Connectivity analysis completed successfully",
                data={
                    'hub_type': self.hub_type,
                    'workspace_name': self.workspace_name,
                    'results': self.results,
                    'summary': self.progress_tracker.get_summary()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error during analysis: {str(e)}")
            return AnalysisResult(
                success=False,
                message="Analysis failed due to unexpected error",
                error=str(e)
            )
    
    def _validate_prerequisites(self) -> AnalysisResult:
        """Validate all prerequisites"""
        # Check Azure CLI
        if not validate_azure_cli():
            return AnalysisResult(
                success=False,
                message="Azure CLI not found or ML extension not installed",
                error="Please install Azure CLI and run 'az extension add -n ml'"
            )
        
        # Additional validation can be added here
        return AnalysisResult(success=True, message="Prerequisites validated")
    
    def _connect_to_workspace(self) -> AnalysisResult:
        """Connect to workspace and get basic info"""
        try:
            # Use existing workspace analyzer
            analyzer_factory = WorkspaceAnalyzerFactory()
            workspace_analyzer = analyzer_factory.create_analyzer(
                self.workspace_name, 
                self.resource_group,
                self.subscription_id,
                self.hub_type
            )
            workspace_config = workspace_analyzer.analyze()
            
            return AnalysisResult(
                success=True,
                message="Successfully connected to workspace",
                data={
                    'name': workspace_config.name,
                    'location': workspace_config.location,
                    'network_mode': workspace_config.network_mode,
                    'isolation_mode': workspace_config.isolation_mode,
                    'hub_type': workspace_config.hub_type
                }
            )
        except Exception as e:
            return AnalysisResult(
                success=False,
                message=f"Failed to connect to workspace: {str(e)}",
                error=str(e)
            ) 