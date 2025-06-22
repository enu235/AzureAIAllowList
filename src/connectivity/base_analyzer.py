from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

@dataclass
class AnalysisResult:
    """Base class for analysis results"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class BaseAnalyzer(ABC):
    """Base class for all connectivity analyzers"""
    
    def __init__(self, workspace_name: str, resource_group: str, 
                 subscription_id: Optional[str] = None, hub_type: str = 'azure-ml'):
        self.workspace_name = workspace_name
        self.resource_group = resource_group
        self.subscription_id = subscription_id
        self.hub_type = hub_type
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def analyze(self) -> AnalysisResult:
        """Perform the analysis"""
        pass
    
    def validate_prerequisites(self) -> AnalysisResult:
        """Validate prerequisites for analysis"""
        # Check Azure CLI, permissions, etc.
        from ..utils.validators import validate_azure_cli
        
        if not validate_azure_cli():
            return AnalysisResult(
                success=False,
                message="Azure CLI validation failed",
                error="Please install Azure CLI and run 'az login' and 'az extension add -n ml'"
            )
        
        return AnalysisResult(
            success=True,
            message="Prerequisites validated successfully"
        ) 