"""
Azure CLI Helper Utilities

Common patterns for subprocess calls and JSON parsing to reduce code duplication.
"""

import json
import subprocess
from typing import Dict, List, Optional, Any
from .logger import setup_logger

logger = setup_logger(__name__)


class AzureCliHelper:
    """Helper class for Azure CLI operations with consistent error handling"""
    
    @staticmethod
    def run_az_command(cmd: List[str], timeout: int = 60, 
                       subscription_id: Optional[str] = None) -> Optional[Dict]:
        """
        Run Azure CLI command and return parsed JSON result.
        
        Args:
            cmd: Azure CLI command as list of strings
            timeout: Command timeout in seconds
            subscription_id: Optional subscription ID to add to command
            
        Returns:
            Parsed JSON result or None if command failed/returned empty
        """
        try:
            # Add subscription if provided
            if subscription_id:
                cmd.extend(['--subscription', subscription_id])
            
            # Add JSON output if not already specified
            if '--output' not in cmd:
                cmd.extend(['--output', 'json'])
            
            logger.debug(f"Running Azure CLI command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            elif result.returncode != 0:
                logger.warning(f"Azure CLI command failed: {result.stderr}")
            
            return None
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Azure CLI command timed out after {timeout} seconds")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error running Azure CLI command: {str(e)}")
            return None
    
    @staticmethod
    def run_az_command_raw(cmd: List[str], timeout: int = 60, 
                          subscription_id: Optional[str] = None) -> Optional[str]:
        """
        Run Azure CLI command and return raw stdout.
        
        Args:
            cmd: Azure CLI command as list of strings
            timeout: Command timeout in seconds
            subscription_id: Optional subscription ID to add to command
            
        Returns:
            Raw stdout or None if command failed
        """
        try:
            # Add subscription if provided
            if subscription_id:
                cmd.extend(['--subscription', subscription_id])
            
            logger.debug(f"Running Azure CLI command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.warning(f"Azure CLI command failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.warning(f"Azure CLI command timed out after {timeout} seconds")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error running Azure CLI command: {str(e)}")
            return None
    
    @staticmethod
    def get_workspace_info(workspace_name: str, resource_group: str, 
                          subscription_id: Optional[str] = None) -> Optional[Dict]:
        """Get workspace information using Azure CLI"""
        cmd = ['az', 'ml', 'workspace', 'show',
               '--name', workspace_name,
               '--resource-group', resource_group]
        
        return AzureCliHelper.run_az_command(cmd, subscription_id=subscription_id)
    
    @staticmethod
    def get_resource_info(resource_type: str, resource_name: str, 
                         resource_group: Optional[str] = None,
                         subscription_id: Optional[str] = None) -> Optional[Dict]:
        """Get resource information using Azure CLI"""
        if resource_type == 'keyvault':
            cmd = ['az', 'keyvault', 'show', '--name', resource_name]
        elif resource_type == 'storage':
            cmd = ['az', 'storage', 'account', 'show', 
                   '--name', resource_name, '--resource-group', resource_group]
        elif resource_type == 'acr':
            cmd = ['az', 'acr', 'show', 
                   '--name', resource_name, '--resource-group', resource_group]
        else:
            logger.warning(f"Unsupported resource type: {resource_type}")
            return None
        
        return AzureCliHelper.run_az_command(cmd, subscription_id=subscription_id)
    
    @staticmethod
    def list_subscriptions() -> Optional[List[Dict]]:
        """List all available subscriptions"""
        cmd = ['az', 'account', 'list']
        result = AzureCliHelper.run_az_command(cmd)
        return result if isinstance(result, list) else None
    
    @staticmethod
    def is_logged_in() -> bool:
        """Check if user is logged into Azure CLI"""
        try:
            result = subprocess.run(
                ['az', 'account', 'show'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False 