"""
Validation utilities for prerequisites and configurations
"""

import subprocess
import sys
import re
from typing import Dict, List, Optional, Tuple
import validators as url_validators
from urllib.parse import urlparse

def validate_azure_cli() -> bool:
    """
    Validate Azure CLI installation and authentication.
    
    Returns:
        True if Azure CLI is properly configured, False otherwise
    """
    try:
        # Check if Azure CLI is installed
        result = subprocess.run(['az', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False
        
        # Check if ML extension is installed
        result = subprocess.run(['az', 'extension', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False
        
        if '"name": "ml"' not in result.stdout:
            return False
        
        # Check if user is logged in
        result = subprocess.run(['az', 'account', 'show'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False
        
        return True
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False

def validate_package_manager_available(package_manager: str) -> bool:
    """
    Check if a specific package manager is available.
    
    Args:
        package_manager: Name of package manager (pip, conda, uv, etc.)
    
    Returns:
        True if available, False otherwise
    """
    try:
        result = subprocess.run([package_manager, '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False

def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    return url_validators.url(url) is True

def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL for use in Azure ML outbound rules.
    
    Args:
        url: Full URL
        
    Returns:
        Domain with wildcard prefix (e.g., "*.pypi.org") or None if invalid
    """
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
        
        domain = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # Add wildcard prefix if not already present
        if not domain.startswith('*.'):
            # For subdomains, use wildcard for the parent domain
            parts = domain.split('.')
            if len(parts) > 2:
                domain = '*.' + '.'.join(parts[-2:])
            else:
                domain = '*.' + domain
        
        return domain
        
    except Exception:
        return None

def is_private_repository(url: str) -> bool:
    """
    Determine if a URL points to a private repository.
    
    Args:
        url: Repository URL
        
    Returns:
        True if likely a private repository, False otherwise
    """
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Common private repository indicators
    private_indicators = [
        'localhost',
        '127.0.0.1',
        '10.',
        '172.',
        '192.168.',
        'internal',
        'corp',
        'company',
        'private',
        'artifactory',
        'nexus',
        'intranet'
    ]
    
    # Check if URL contains private indicators
    for indicator in private_indicators:
        if indicator in url_lower:
            return True
    
    # Check for common public repositories (if not in this list, might be private)
    public_repositories = [
        'pypi.org',
        'pythonhosted.org',
        'anaconda.org',
        'conda-forge.org',
        'github.com',
        'gitlab.com',
        'bitbucket.org'
    ]
    
    for public_repo in public_repositories:
        if public_repo in url_lower:
            return False
    
    # If we can't determine, assume it might be private for safety
    parsed = urlparse(url)
    if parsed.netloc and not any(pub in parsed.netloc.lower() for pub in public_repositories):
        return True
    
    return False

def validate_azure_workspace_name(name: str) -> bool:
    """
    Validate Azure ML workspace name format.
    
    Args:
        name: Workspace name to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not name:
        return False
    
    # Azure ML workspace name requirements:
    # - 3-33 characters
    # - Alphanumeric and hyphens only
    # - Must start and end with alphanumeric
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,31}[a-zA-Z0-9]$|^[a-zA-Z0-9]{3}$'
    return bool(re.match(pattern, name))

def validate_azure_resource_group_name(name: str) -> bool:
    """
    Validate Azure resource group name format.
    
    Args:
        name: Resource group name to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not name:
        return False
    
    # Azure resource group name requirements:
    # - 1-90 characters
    # - Alphanumeric, periods, underscores, hyphens, and parentheses
    # - Cannot end with period
    if len(name) > 90 or name.endswith('.'):
        return False
    
    pattern = r'^[a-zA-Z0-9._()-]+$'
    return bool(re.match(pattern, name))

def validate_workspace_access(workspace_name: str, resource_group: str, 
                            subscription_id: Optional[str] = None) -> bool:
    """Validate user has access to the workspace"""
    try:
        cmd = ['az', 'ml', 'workspace', 'show', 
               '--name', workspace_name, 
               '--resource-group', resource_group]
        if subscription_id:
            cmd.extend(['--subscription', subscription_id])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception:
        return False

def validate_required_permissions() -> Dict[str, bool]:
    """Check for required RBAC permissions"""
    # This will be expanded in later phases
    permissions = {
        'read_workspace': True,  # Placeholder
        'read_network': True,    # Placeholder
        'read_resources': True   # Placeholder
    }
    return permissions

def get_system_info() -> Dict[str, str]:
    """
    Get system information for troubleshooting.
    
    Returns:
        Dictionary with system information
    """
    info = {
        'platform': sys.platform,
        'python_version': sys.version,
        'python_executable': sys.executable
    }
    
    # Check available package managers
    package_managers = ['pip', 'conda', 'uv', 'poetry']
    for pm in package_managers:
        info[f'{pm}_available'] = str(validate_package_manager_available(pm))
    
    # Check Azure CLI
    info['azure_cli_available'] = str(validate_azure_cli())
    
    return info 