from typing import Dict, List, Optional
import json
import subprocess

class StorageAnalyzer:
    """Detailed analysis for storage accounts"""
    
    @staticmethod
    def analyze_detailed(storage_account_name: str, resource_group: str,
                        subscription_id: Optional[str] = None) -> Dict:
        """Perform detailed storage account analysis"""
        analysis = {
            'containers': [],
            'file_shares': [],
            'queues': [],
            'tables': [],
            'encryption': {},
            'lifecycle_policies': [],
            'cors_rules': {},
            'static_website': False
        }
        
        try:
            # Get storage account keys (needed for further operations)
            cmd_keys = ['az', 'storage', 'account', 'keys', 'list',
                       '--account-name', storage_account_name,
                       '--resource-group', resource_group,
                       '--output', 'json']
            
            if subscription_id:
                cmd_keys.extend(['--subscription', subscription_id])
                
            result = subprocess.run(cmd_keys, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                keys = json.loads(result.stdout)
                account_key = keys[0]['value'] if keys else None
                
                if account_key:
                    # List containers
                    cmd_containers = ['az', 'storage', 'container', 'list',
                                    '--account-name', storage_account_name,
                                    '--account-key', account_key,
                                    '--output', 'json']
                    
                    result = subprocess.run(cmd_containers, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        containers = json.loads(result.stdout)
                        for container in containers:
                            analysis['containers'].append({
                                'name': container.get('name'),
                                'public_access': container.get('properties', {}).get('publicAccess', 'None')
                            })
                    
                    # List file shares
                    cmd_shares = ['az', 'storage', 'share', 'list',
                                '--account-name', storage_account_name,
                                '--account-key', account_key,
                                '--output', 'json']
                    
                    result = subprocess.run(cmd_shares, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        shares = json.loads(result.stdout)
                        for share in shares:
                            analysis['file_shares'].append({
                                'name': share.get('name'),
                                'quota': share.get('properties', {}).get('quota')
                            })
                    
                    # List queues
                    cmd_queues = ['az', 'storage', 'queue', 'list',
                                '--account-name', storage_account_name,
                                '--account-key', account_key,
                                '--output', 'json']
                    
                    result = subprocess.run(cmd_queues, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        analysis['queues'] = json.loads(result.stdout)
                    
                    # List tables
                    cmd_tables = ['az', 'storage', 'table', 'list',
                                '--account-name', storage_account_name,
                                '--account-key', account_key,
                                '--output', 'json']
                    
                    result = subprocess.run(cmd_tables, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        analysis['tables'] = json.loads(result.stdout)
                    
                    # Get encryption settings
                    cmd_encryption = ['az', 'storage', 'account', 'show',
                                    '--name', storage_account_name,
                                    '--resource-group', resource_group,
                                    '--output', 'json']
                    
                    if subscription_id:
                        cmd_encryption.extend(['--subscription', subscription_id])
                        
                    result = subprocess.run(cmd_encryption, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        storage_info = json.loads(result.stdout)
                        analysis['encryption'] = storage_info.get('encryption', {})
                        analysis['static_website'] = storage_info.get('primaryEndpoints', {}).get('web') is not None
                            
        except Exception as e:
            # Log but continue
            pass
            
        return analysis

class KeyVaultAnalyzer:
    """Detailed analysis for Key Vaults"""
    
    @staticmethod
    def analyze_detailed(key_vault_name: str, subscription_id: Optional[str] = None) -> Dict:
        """Perform detailed Key Vault analysis"""
        analysis = {
            'access_policies': [],
            'rbac_enabled': False,
            'soft_delete_enabled': False,
            'purge_protection_enabled': False,
            'secrets_count': 0,
            'keys_count': 0,
            'certificates_count': 0
        }
        
        try:
            # Get Key Vault details
            cmd = ['az', 'keyvault', 'show',
                   '--name', key_vault_name,
                   '--output', 'json']
            
            if subscription_id:
                cmd.extend(['--subscription', subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                kv_info = json.loads(result.stdout)
                properties = kv_info.get('properties', {})
                
                # Extract security settings
                analysis['rbac_enabled'] = properties.get('enableRbacAuthorization', False)
                analysis['soft_delete_enabled'] = properties.get('enableSoftDelete', False)
                analysis['purge_protection_enabled'] = properties.get('enablePurgeProtection', False)
                
                # Get access policies
                access_policies = properties.get('accessPolicies', [])
                for policy in access_policies:
                    analysis['access_policies'].append({
                        'object_id': policy.get('objectId'),
                        'permissions': policy.get('permissions', {})
                    })
                
                # Count secrets (requires permissions)
                try:
                    cmd_secrets = ['az', 'keyvault', 'secret', 'list',
                                 '--vault-name', key_vault_name,
                                 '--output', 'json']
                    
                    if subscription_id:
                        cmd_secrets.extend(['--subscription', subscription_id])
                        
                    result = subprocess.run(cmd_secrets, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        secrets = json.loads(result.stdout)
                        analysis['secrets_count'] = len(secrets)
                except:
                    pass  # User may not have permissions
                
                # Count keys (requires permissions)
                try:
                    cmd_keys = ['az', 'keyvault', 'key', 'list',
                              '--vault-name', key_vault_name,
                              '--output', 'json']
                    
                    if subscription_id:
                        cmd_keys.extend(['--subscription', subscription_id])
                        
                    result = subprocess.run(cmd_keys, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        keys = json.loads(result.stdout)
                        analysis['keys_count'] = len(keys)
                except:
                    pass  # User may not have permissions
                
                # Count certificates (requires permissions)
                try:
                    cmd_certs = ['az', 'keyvault', 'certificate', 'list',
                               '--vault-name', key_vault_name,
                               '--output', 'json']
                    
                    if subscription_id:
                        cmd_certs.extend(['--subscription', subscription_id])
                        
                    result = subprocess.run(cmd_certs, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        certs = json.loads(result.stdout)
                        analysis['certificates_count'] = len(certs)
                except:
                    pass  # User may not have permissions
                    
        except Exception as e:
            # Log but continue
            pass
            
        return analysis

class ContainerRegistryAnalyzer:
    """Detailed analysis for Container Registries"""
    
    @staticmethod
    def analyze_detailed(registry_name: str, resource_group: str,
                        subscription_id: Optional[str] = None) -> Dict:
        """Perform detailed Container Registry analysis"""
        analysis = {
            'sku': 'Basic',
            'admin_enabled': False,
            'public_access': True,
            'repositories': [],
            'webhooks': [],
            'replications': [],
            'retention_policy': {}
        }
        
        try:
            # Get registry details
            cmd = ['az', 'acr', 'show',
                   '--name', registry_name,
                   '--resource-group', resource_group,
                   '--output', 'json']
            
            if subscription_id:
                cmd.extend(['--subscription', subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                acr_info = json.loads(result.stdout)
                
                analysis['sku'] = acr_info.get('sku', {}).get('name', 'Basic')
                analysis['admin_enabled'] = acr_info.get('adminUserEnabled', False)
                analysis['public_access'] = (
                    acr_info.get('publicNetworkAccess', 'Enabled') == 'Enabled'
                )
                
                # List repositories
                cmd_repos = ['az', 'acr', 'repository', 'list',
                           '--name', registry_name,
                           '--output', 'json']
                
                if subscription_id:
                    cmd_repos.extend(['--subscription', subscription_id])
                    
                result = subprocess.run(cmd_repos, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    analysis['repositories'] = json.loads(result.stdout)
                
                # List webhooks
                cmd_webhooks = ['az', 'acr', 'webhook', 'list',
                              '--registry', registry_name,
                              '--output', 'json']
                
                if subscription_id:
                    cmd_webhooks.extend(['--subscription', subscription_id])
                    
                result = subprocess.run(cmd_webhooks, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    webhooks = json.loads(result.stdout)
                    for webhook in webhooks:
                        analysis['webhooks'].append({
                            'name': webhook.get('name'),
                            'status': webhook.get('status'),
                            'actions': webhook.get('actions', [])
                        })
                
                # List replications (Premium SKU only)
                if analysis['sku'] == 'Premium':
                    cmd_replications = ['az', 'acr', 'replication', 'list',
                                      '--registry', registry_name,
                                      '--output', 'json']
                    
                    if subscription_id:
                        cmd_replications.extend(['--subscription', subscription_id])
                        
                    result = subprocess.run(cmd_replications, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        replications = json.loads(result.stdout)
                        for replication in replications:
                            analysis['replications'].append({
                                'name': replication.get('name'),
                                'location': replication.get('location'),
                                'status': replication.get('provisioningState')
                            })
                
                # Get retention policy (if available)
                try:
                    cmd_retention = ['az', 'acr', 'config', 'retention', 'show',
                                   '--registry', registry_name,
                                   '--output', 'json']
                    
                    if subscription_id:
                        cmd_retention.extend(['--subscription', subscription_id])
                        
                    result = subprocess.run(cmd_retention, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        analysis['retention_policy'] = json.loads(result.stdout)
                except:
                    pass  # Retention policy may not be configured
                    
        except Exception as e:
            # Log but continue
            pass
            
        return analysis

class CognitiveServicesAnalyzer:
    """Detailed analysis for Cognitive Services"""
    
    @staticmethod
    def analyze_detailed(service_name: str, resource_group: str,
                        subscription_id: Optional[str] = None) -> Dict:
        """Perform detailed Cognitive Services analysis"""
        analysis = {
            'kind': 'Unknown',
            'sku': {},
            'custom_subdomain': False,
            'endpoints': {},
            'api_properties': {}
        }
        
        try:
            # Get Cognitive Services details
            cmd = ['az', 'cognitiveservices', 'account', 'show',
                   '--name', service_name,
                   '--resource-group', resource_group,
                   '--output', 'json']
            
            if subscription_id:
                cmd.extend(['--subscription', subscription_id])
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                cs_info = json.loads(result.stdout)
                
                analysis['kind'] = cs_info.get('kind', 'Unknown')
                analysis['sku'] = cs_info.get('sku', {})
                analysis['custom_subdomain'] = cs_info.get('properties', {}).get('customSubDomainName') is not None
                analysis['endpoints'] = cs_info.get('properties', {}).get('endpoints', {})
                analysis['api_properties'] = cs_info.get('properties', {}).get('apiProperties', {})
                    
        except Exception as e:
            # Log but continue
            pass
            
        return analysis 