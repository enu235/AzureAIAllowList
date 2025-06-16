"""
Package URL discoverers for different package managers
"""

import subprocess
import re
import tempfile
import os
import yaml
import toml
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from .utils.logger import setup_logger
from .utils.validators import extract_domain_from_url, is_private_repository, validate_package_manager_available

logger = setup_logger(__name__)

@dataclass
class PackageDiscoveryResult:
    """Result of package URL discovery."""
    domains: Set[str]
    private_repositories: List[str]
    platform_warnings: List[str]
    packages_processed: int
    urls_discovered: List[str]

class BasePackageDiscoverer(ABC):
    """Base class for package discoverers."""
    
    def __init__(self):
        self.temp_dir = None
        
    @abstractmethod
    def discover_urls(self, file_path: str, include_transitive: bool = True, 
                     platform: str = 'auto', dry_run: bool = False) -> PackageDiscoveryResult:
        """Discover package download URLs."""
        pass
    
    @abstractmethod
    def get_package_manager_name(self) -> str:
        """Get the package manager name."""
        pass
    
    def _create_temp_environment(self) -> str:
        """Create a temporary environment for safe package discovery."""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix='azureml_package_discovery_')
            logger.debug(f"Created temporary directory: {self.temp_dir}")
        return self.temp_dir
    
    def _cleanup_temp_environment(self):
        """Clean up temporary environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
    
    def _extract_urls_from_output(self, output: str) -> List[str]:
        """Extract URLs from package manager verbose output."""
        urls = []
        
        # Common URL patterns in package manager output
        url_patterns = [
            r'https?://[^\s<>"\']+',  # Basic HTTP/HTTPS URLs
            r'Downloading\s+from\s+([^\s]+)',  # Common download pattern
            r'Looking in links:\s*([^\n]+)',  # pip looking in links
            r'Found link\s+([^\s]+)',  # pip found link
            r'Collecting.*from\s+([^\s)]+)',  # pip collecting from
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match.startswith(('http://', 'https://')):
                    urls.append(match.strip())
        
        return urls
    
    def _process_urls_to_domains(self, urls: List[str]) -> Tuple[Set[str], List[str]]:
        """Process URLs to extract domains and detect private repositories."""
        domains = set()
        private_repos = []
        
        for url in urls:
            # Check if private repository
            if is_private_repository(url):
                private_repos.append(url)
                continue
            
            # Extract domain
            domain = extract_domain_from_url(url)
            if domain:
                domains.add(domain)
        
        return domains, private_repos

class PipPackageDiscoverer(BasePackageDiscoverer):
    """Discoverer for pip packages."""
    
    def get_package_manager_name(self) -> str:
        return "pip"
    
    def discover_urls(self, file_path: str, include_transitive: bool = True,
                     platform: str = 'auto', dry_run: bool = False) -> PackageDiscoveryResult:
        """Discover URLs from requirements.txt using pip."""
        
        if not validate_package_manager_available('pip'):
            raise RuntimeError("pip is not available")
        
        logger.info("Discovering package URLs using pip...")
        
        # Read requirements file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract package names (ignore comments, options, URLs)
        packages = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                # Extract package name before any version specifiers
                pkg_name = re.split(r'[<>=!]', line)[0].strip()
                if pkg_name:
                    packages.append(pkg_name)
        
        if dry_run:
            # In dry-run mode, return common domains for the discovered packages
            return self._get_dry_run_result(packages)
        
        # Create temporary environment
        temp_dir = self._create_temp_environment()
        
        try:
            all_urls = []
            platform_warnings = []
            
            # Use pip download with verbose output to get URLs without actually installing
            for package in packages:
                try:
                    cmd = [
                        'pip', 'download', package,
                        '--dest', temp_dir,
                        '--no-deps' if not include_transitive else '--deps',
                        '--verbose', '--verbose',  # Double verbose for maximum output
                        '--dry-run' if hasattr(subprocess, 'DEVNULL') else '--no-deps'
                    ]
                    
                    logger.debug(f"Running: {' '.join(cmd)}")
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=120,
                        cwd=temp_dir
                    )
                    
                    # Extract URLs from both stdout and stderr
                    output = result.stdout + result.stderr
                    urls = self._extract_urls_from_output(output)
                    all_urls.extend(urls)
                    
                    # Check for platform warnings
                    if 'platform' in output.lower() and platform != 'auto':
                        platform_warnings.append(f"Platform-specific dependencies detected for {package}")
                    
                except subprocess.TimeoutExpired:
                    logger.warning(f"Timeout processing package: {package}")
                except Exception as e:
                    logger.warning(f"Error processing package {package}: {e}")
            
            # Process URLs to domains
            domains, private_repos = self._process_urls_to_domains(all_urls)
            
            # Add common pip domains if not discovered
            common_domains = {'*.pypi.org', '*.pythonhosted.org'}
            domains.update(common_domains)
            
            return PackageDiscoveryResult(
                domains=domains,
                private_repositories=private_repos,
                platform_warnings=platform_warnings,
                packages_processed=len(packages),
                urls_discovered=all_urls
            )
            
        finally:
            self._cleanup_temp_environment()
    
    def _get_dry_run_result(self, packages: List[str]) -> PackageDiscoveryResult:
        """Get dry-run result with common domains."""
        return PackageDiscoveryResult(
            domains={'*.pypi.org', '*.pythonhosted.org'},
            private_repositories=[],
            platform_warnings=[],
            packages_processed=len(packages),
            urls_discovered=[]
        )

class CondaPackageDiscoverer(BasePackageDiscoverer):
    """Discoverer for conda packages."""
    
    def get_package_manager_name(self) -> str:
        return "conda"
    
    def discover_urls(self, file_path: str, include_transitive: bool = True,
                     platform: str = 'auto', dry_run: bool = False) -> PackageDiscoveryResult:
        """Discover URLs from environment.yml using conda."""
        
        if not validate_package_manager_available('conda'):
            raise RuntimeError("conda is not available")
        
        logger.info("Discovering package URLs using conda...")
        
        # Parse environment.yml
        with open(file_path, 'r') as f:
            env_config = yaml.safe_load(f)
        
        dependencies = env_config.get('dependencies', [])
        channels = env_config.get('channels', ['defaults'])
        
        # Extract package names
        packages = []
        pip_packages = []
        
        for dep in dependencies:
            if isinstance(dep, str):
                # Extract package name before version specifiers
                pkg_name = re.split(r'[<>=!]', dep)[0].strip()
                if pkg_name:
                    packages.append(pkg_name)
            elif isinstance(dep, dict) and 'pip' in dep:
                pip_packages.extend(dep['pip'])
        
        if dry_run:
            return self._get_dry_run_result(packages, channels, pip_packages)
        
        try:
            all_urls = []
            platform_warnings = []
            
            # Process conda packages
            for package in packages:
                try:
                    cmd = [
                        'conda', 'search', package,
                        '--info', '--verbose'
                    ]
                    
                    # Add channels
                    for channel in channels:
                        cmd.extend(['-c', channel])
                    
                    logger.debug(f"Running: {' '.join(cmd)}")
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    output = result.stdout + result.stderr
                    urls = self._extract_urls_from_output(output)
                    all_urls.extend(urls)
                    
                except Exception as e:
                    logger.warning(f"Error processing conda package {package}: {e}")
            
            # Process pip packages within conda environment
            if pip_packages:
                pip_discoverer = PipPackageDiscoverer()
                # Create temporary requirements.txt for pip packages
                temp_req_file = os.path.join(self._create_temp_environment(), 'requirements.txt')
                with open(temp_req_file, 'w') as f:
                    f.write('\n'.join(pip_packages))
                
                pip_result = pip_discoverer.discover_urls(temp_req_file, include_transitive, platform, dry_run)
                all_urls.extend(pip_result.urls_discovered)
                platform_warnings.extend(pip_result.platform_warnings)
            
            # Process URLs to domains
            domains, private_repos = self._process_urls_to_domains(all_urls)
            
            # Add common conda domains
            common_domains = {'*.anaconda.org', '*.conda.io', '*.anaconda.com'}
            domains.update(common_domains)
            
            return PackageDiscoveryResult(
                domains=domains,
                private_repositories=private_repos,
                platform_warnings=platform_warnings,
                packages_processed=len(packages) + len(pip_packages),
                urls_discovered=all_urls
            )
            
        finally:
            self._cleanup_temp_environment()
    
    def _get_dry_run_result(self, packages: List[str], channels: List[str], 
                           pip_packages: List[str]) -> PackageDiscoveryResult:
        """Get dry-run result with common domains."""
        domains = {'*.anaconda.org', '*.conda.io', '*.anaconda.com'}
        
        # Add pip domains if pip packages are present
        if pip_packages:
            domains.update({'*.pypi.org', '*.pythonhosted.org'})
        
        return PackageDiscoveryResult(
            domains=domains,
            private_repositories=[],
            platform_warnings=[],
            packages_processed=len(packages) + len(pip_packages),
            urls_discovered=[]
        )

class PyProjectTomlDiscoverer(BasePackageDiscoverer):
    """Discoverer for pyproject.toml files (Poetry, uv, etc.)."""
    
    def get_package_manager_name(self) -> str:
        return "pyproject"
    
    def discover_urls(self, file_path: str, include_transitive: bool = True,
                     platform: str = 'auto', dry_run: bool = False) -> PackageDiscoveryResult:
        """Discover URLs from pyproject.toml."""
        
        logger.info("Discovering package URLs from pyproject.toml...")
        
        # Parse pyproject.toml
        with open(file_path, 'r') as f:
            config = toml.load(f)
        
        packages = []
        
        # Extract dependencies from different sections
        if 'tool' in config:
            # Poetry format
            if 'poetry' in config['tool'] and 'dependencies' in config['tool']['poetry']:
                deps = config['tool']['poetry']['dependencies']
                packages.extend([pkg for pkg in deps.keys() if pkg != 'python'])
            
            # uv format
            if 'uv' in config['tool'] and 'dependencies' in config['tool']['uv']:
                packages.extend(config['tool']['uv']['dependencies'])
        
        # PEP 621 format
        if 'project' in config and 'dependencies' in config['project']:
            for dep in config['project']['dependencies']:
                pkg_name = re.split(r'[<>=!]', dep)[0].strip()
                if pkg_name:
                    packages.append(pkg_name)
        
        if dry_run:
            return self._get_dry_run_result(packages)
        
        # Check available package managers and use the appropriate one
        if validate_package_manager_available('uv'):
            return self._discover_with_uv(packages, include_transitive, platform)
        elif validate_package_manager_available('poetry'):
            return self._discover_with_poetry(packages, include_transitive, platform)
        else:
            # Fall back to pip
            return self._discover_with_pip_fallback(packages, include_transitive, platform)
    
    def _discover_with_uv(self, packages: List[str], include_transitive: bool, 
                         platform: str) -> PackageDiscoveryResult:
        """Discover URLs using uv."""
        logger.debug("Using uv for package discovery")
        
        temp_dir = self._create_temp_environment()
        all_urls = []
        
        try:
            for package in packages:
                cmd = ['uv', 'pip', 'download', package, '--dest', temp_dir, '-v']
                if not include_transitive:
                    cmd.append('--no-deps')
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                output = result.stdout + result.stderr
                urls = self._extract_urls_from_output(output)
                all_urls.extend(urls)
        
        except Exception as e:
            logger.warning(f"Error using uv: {e}")
            return self._discover_with_pip_fallback(packages, include_transitive, platform)
        
        finally:
            self._cleanup_temp_environment()
        
        domains, private_repos = self._process_urls_to_domains(all_urls)
        domains.update({'*.pypi.org', '*.pythonhosted.org'})
        
        return PackageDiscoveryResult(
            domains=domains,
            private_repositories=private_repos,
            platform_warnings=[],
            packages_processed=len(packages),
            urls_discovered=all_urls
        )
    
    def _discover_with_poetry(self, packages: List[str], include_transitive: bool, 
                             platform: str) -> PackageDiscoveryResult:
        """Discover URLs using poetry."""
        logger.debug("Using poetry for package discovery")
        
        # Poetry discovery is more complex, fall back to pip for now
        return self._discover_with_pip_fallback(packages, include_transitive, platform)
    
    def _discover_with_pip_fallback(self, packages: List[str], include_transitive: bool, 
                                   platform: str) -> PackageDiscoveryResult:
        """Fall back to pip discovery."""
        logger.debug("Falling back to pip for package discovery")
        
        # Create temporary requirements.txt
        temp_dir = self._create_temp_environment()
        temp_req_file = os.path.join(temp_dir, 'requirements.txt')
        
        with open(temp_req_file, 'w') as f:
            f.write('\n'.join(packages))
        
        pip_discoverer = PipPackageDiscoverer()
        return pip_discoverer.discover_urls(temp_req_file, include_transitive, platform, False)
    
    def _get_dry_run_result(self, packages: List[str]) -> PackageDiscoveryResult:
        """Get dry-run result with common domains."""
        return PackageDiscoveryResult(
            domains={'*.pypi.org', '*.pythonhosted.org'},
            private_repositories=[],
            platform_warnings=[],
            packages_processed=len(packages),
            urls_discovered=[]
        )

class PipfileDiscoverer(BasePackageDiscoverer):
    """Discoverer for Pipfile (Pipenv)."""
    
    def get_package_manager_name(self) -> str:
        return "pipfile"
    
    def discover_urls(self, file_path: str, include_transitive: bool = True,
                     platform: str = 'auto', dry_run: bool = False) -> PackageDiscoveryResult:
        """Discover URLs from Pipfile."""
        
        logger.info("Discovering package URLs from Pipfile...")
        
        # Parse Pipfile
        with open(file_path, 'r') as f:
            config = toml.load(f)
        
        packages = []
        
        # Extract packages from [packages] and [dev-packages] sections
        if 'packages' in config:
            packages.extend(config['packages'].keys())
        
        if 'dev-packages' in config:
            packages.extend(config['dev-packages'].keys())
        
        if dry_run:
            return self._get_dry_run_result(packages)
        
        # Use pip fallback (pipenv is essentially a wrapper around pip)
        temp_dir = self._create_temp_environment()
        temp_req_file = os.path.join(temp_dir, 'requirements.txt')
        
        with open(temp_req_file, 'w') as f:
            f.write('\n'.join(packages))
        
        pip_discoverer = PipPackageDiscoverer()
        return pip_discoverer.discover_urls(temp_req_file, include_transitive, platform, False)
    
    def _get_dry_run_result(self, packages: List[str]) -> PackageDiscoveryResult:
        """Get dry-run result with common domains."""
        return PackageDiscoveryResult(
            domains={'*.pypi.org', '*.pythonhosted.org'},
            private_repositories=[],
            platform_warnings=[],
            packages_processed=len(packages),
            urls_discovered=[]
        )

class PackageDiscovererFactory:
    """Factory to create appropriate package discoverer."""
    
    @staticmethod
    def create_discoverer(package_type: str) -> BasePackageDiscoverer:
        """
        Create the appropriate discoverer for the package type.
        
        Args:
            package_type: Type of package file (pip, conda, pyproject, pipfile)
            
        Returns:
            Appropriate package discoverer instance
        """
        if package_type == 'pip':
            return PipPackageDiscoverer()
        elif package_type == 'conda':
            return CondaPackageDiscoverer()
        elif package_type == 'pyproject':
            return PyProjectTomlDiscoverer()
        elif package_type == 'pipfile':
            return PipfileDiscoverer()
        else:
            raise ValueError(f"Unsupported package type: {package_type}")
    
    @staticmethod
    def get_supported_types() -> List[str]:
        """Get list of supported package types."""
        return ['pip', 'conda', 'pyproject', 'pipfile'] 