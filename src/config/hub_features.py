"""
Hub Feature Manager

Manages feature-specific FQDN requirements for Azure ML workspaces and AI Foundry hubs.
"""

from typing import Set, Dict, List


class HubFeatureManager:
    """Manages feature-specific domains for different hub types"""
    
    def __init__(self, hub_type: str):
        self.hub_type = hub_type.lower()
        
        # Azure AI Foundry specific features
        self._ai_foundry_features = {
            'vscode': {
                '*.vscode.dev',
                'code.visualstudio.com',
                'vscode-cdn.azureedge.net',
                'az764295.vo.msecnd.net',
                'vscode.blob.core.windows.net',
                'vsmarketplacebadge.apphb.com',
                '*.vscode-cdn.net',
                'vscode.download.prss.microsoft.com'
            },
            'huggingface': {
                'huggingface.co',
                '*.huggingface.co',
                'cdn-lfs.huggingface.co',
                'cdn-lfs-us-1.huggingface.co',
                'docker.io',
                '*.docker.com',
                'registry-1.docker.io',
                'production.cloudflare.docker.com',
                'cdn-lfs.hf.co',
                'datasets-server.huggingface.co'
            },
            'prompt_flow': {
                'pypi.org',
                '*.pypi.org',
                'files.pythonhosted.org',
                '*.pythonhosted.org',
                'github.com',
                '*.github.com',
                'api.github.com',
                'raw.githubusercontent.com',
                'objects.githubusercontent.com'
            }
        }
        
        # Base domains required for each hub type
        self._base_domains = {
            'azure-ml': {
                # Basic Azure ML domains (these are usually pre-configured)
                '*.azureml.ms',
                '*.azureml.net',
                'ml.azure.com'
            },
            'ai-foundry': {
                # AI Foundry base domains
                '*.azureml.ms',
                '*.azureml.net', 
                'ml.azure.com',
                'ai.azure.com',
                '*.ai.azure.com',
                'aistudio.microsoft.com',
                '*.aistudio.microsoft.com'
            }
        }
        
        # Common domains for package management (already handled by package discoverers)
        self._package_domains = {
            '*.pypi.org',
            '*.pythonhosted.org',
            'files.pythonhosted.org',
            '*.anaconda.org',
            'conda.anaconda.org',
            '*.conda.io'
        }
    
    def get_vscode_domains(self) -> Set[str]:
        """Get Visual Studio Code integration domains"""
        if self.hub_type == 'ai-foundry':
            return self._ai_foundry_features['vscode'].copy()
        return set()
    
    def get_huggingface_domains(self) -> Set[str]:
        """Get HuggingFace model access domains"""
        if self.hub_type == 'ai-foundry':
            return self._ai_foundry_features['huggingface'].copy()
        return set()
    
    def get_prompt_flow_domains(self) -> Set[str]:
        """Get Prompt Flow service domains"""
        if self.hub_type == 'ai-foundry':
            return self._ai_foundry_features['prompt_flow'].copy()
        return set()
    
    def get_base_domains(self) -> Set[str]:
        """Get base domains for the hub type"""
        return self._base_domains.get(self.hub_type, set()).copy()
    
    def get_all_feature_domains(self, enabled_features: List[str]) -> Set[str]:
        """Get all domains for enabled features"""
        all_domains = set()
        
        if self.hub_type == 'ai-foundry':
            for feature in enabled_features:
                if feature in self._ai_foundry_features:
                    all_domains.update(self._ai_foundry_features[feature])
        
        return all_domains
    
    def get_feature_info(self) -> Dict[str, Dict[str, any]]:
        """Get information about available features for the hub type"""
        if self.hub_type == 'ai-foundry':
            return {
                'vscode': {
                    'name': 'Visual Studio Code Integration',
                    'description': 'Enable VS Code web editor integration',
                    'domains_count': len(self._ai_foundry_features['vscode']),
                    'flag': '--include-vscode'
                },
                'huggingface': {
                    'name': 'HuggingFace Model Access',
                    'description': 'Access HuggingFace models and datasets',
                    'domains_count': len(self._ai_foundry_features['huggingface']),
                    'flag': '--include-huggingface'
                },
                'prompt_flow': {
                    'name': 'Prompt Flow Services',
                    'description': 'Enable Prompt Flow orchestration features',
                    'domains_count': len(self._ai_foundry_features['prompt_flow']),
                    'flag': '--include-prompt-flow'
                }
            }
        else:
            return {}
    
    def get_recommended_features(self) -> List[str]:
        """Get recommended features to enable for the hub type"""
        if self.hub_type == 'ai-foundry':
            return ['vscode', 'huggingface']  # Most commonly used
        return []
    
    @classmethod
    def get_supported_features(cls, hub_type: str) -> List[str]:
        """Get list of supported features for a hub type"""
        if hub_type.lower() == 'ai-foundry':
            return ['vscode', 'huggingface', 'prompt_flow']
        return []
    
    def validate_features(self, requested_features: List[str]) -> tuple[List[str], List[str]]:
        """Validate requested features against supported ones
        
        Returns:
            tuple: (valid_features, invalid_features)
        """
        supported = self.get_supported_features(self.hub_type)
        valid = [f for f in requested_features if f in supported]
        invalid = [f for f in requested_features if f not in supported]
        return valid, invalid 