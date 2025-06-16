"""
Message templates for standardized user communications
"""

class MessageTemplates:
    """Centralized message templates for consistent user communication."""
    
    @staticmethod
    def get_disclaimer() -> str:
        """Return the main disclaimer message."""
        return """
🚨 DISCLAIMER: 
This tool is provided "AS IS" without warranty of any kind. 
You use this tool and implement its recommendations at your own risk.
Always review and test configurations in a non-production environment first.
        """.strip()
    
    @staticmethod
    def get_final_disclaimer() -> str:
        """Return the final disclaimer message."""
        return """
⚠️  IMPORTANT REMINDERS:
• Review all generated configurations before applying
• Test in non-production environments first  
• This tool provides guidance only - you are responsible for implementation
• Some packages may have platform-specific requirements
• Monitor your workspace after applying changes
        """
    
    @staticmethod
    def get_private_repo_guidance() -> str:
        """Return guidance for handling private repositories."""
        return """
🔒 PRIVATE REPOSITORY HANDLING:

Private repositories detected cannot be directly added to Azure ML outbound rules.
Consider these alternatives:

1. AZURE STORAGE APPROACH:
   • Upload private packages to Azure Blob Storage
   • Configure your workspace storage account for package access
   • Use pip install from blob storage URLs
   
   Example:
   pip install https://yourstorageaccount.blob.core.windows.net/packages/yourpackage.whl

2. AZURE CONTAINER REGISTRY:
   • Build custom Docker images with pre-installed packages
   • Push to Azure Container Registry (ACR)
   • Reference in your ML environments
   
3. AZURE ARTIFACTS:
   • Use Azure DevOps Artifacts as a private Python feed
   • Configure authentication and access policies
   • Add artifacts.dev.azure.com to allowed domains

4. PRIVATE ENDPOINTS:
   • If your private repo supports it, create private endpoints
   • Add private endpoint outbound rules to workspace

For detailed guidance, see: docs/private-repositories.md
        """
    
    @staticmethod
    def get_platform_warning(platform_from: str, platform_to: str) -> str:
        """Return platform compatibility warning."""
        return f"⚠️ Platform mismatch: Package discovered on {platform_from}, targeting {platform_to}. Some packages may have platform-specific dependencies."
    
    @staticmethod
    def get_windows_linux_considerations() -> str:
        """Return Windows/Linux platform considerations."""
        return """
🖥️ PLATFORM CONSIDERATIONS:

WINDOWS vs LINUX PACKAGES:
• Some packages have different dependencies on Windows vs Linux
• Binary packages (wheels) are often platform-specific
• Consider your Azure ML compute target platform when reviewing domains

RECOMMENDATIONS:
• If using Linux compute: Focus on Linux-compatible packages
• If using Windows compute: Ensure Windows wheel availability
• Cross-platform packages: Usually work on both platforms
• Source distributions: May require compilation tools

COMMON PLATFORM-SPECIFIC DOMAINS:
• *.pythonhosted.org - Universal (both platforms)
• *.anaconda.org - Cross-platform conda packages
• Some packages may use different mirrors for different platforms
        """
    
    @staticmethod
    def get_transitive_dependency_info() -> str:
        """Return information about transitive dependencies."""
        return """
🔗 TRANSITIVE DEPENDENCIES:

This tool discovers both direct and transitive (indirect) dependencies.
Transitive dependencies are packages required by your direct dependencies.

WHY THIS MATTERS:
• Your requirements.txt may list 10 packages
• But those packages might depend on 50+ additional packages
• Each dependency may come from different domains
• All domains need to be allowed for successful package installation

EXAMPLE:
requests → urllib3, certifi, charset-normalizer, idna
pandas → numpy, python-dateutil, pytz

The tool captures all these dependency relationships automatically.
        """
    
    @staticmethod
    def get_azure_cli_validation_error() -> str:
        """Return Azure CLI validation error message."""
        return """
❌ AZURE CLI SETUP REQUIRED:

Before using this tool, ensure Azure CLI is properly configured:

1. INSTALL AZURE CLI:
   # Ubuntu/Debian
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # Windows (PowerShell)
   Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
   
   # macOS
   brew install azure-cli

2. INSTALL ML EXTENSION:
   az extension add --name ml

3. LOGIN TO AZURE:
   az login
   
4. SET SUBSCRIPTION (if you have multiple):
   az account set --subscription "your-subscription-id"

5. VERIFY ACCESS:
   az ml workspace list --resource-group "your-resource-group"
        """
    
    @staticmethod
    def get_no_changes_needed() -> str:
        """Return message when no new domains are discovered."""
        return """
✅ NO CHANGES NEEDED:

All discovered package domains are already configured in your workspace outbound rules.
Your current configuration appears to be complete for the provided package requirements.

RECOMMENDATIONS:
• Verify your package installation works in the workspace
• Test with a small compute instance first
• Monitor for any missing dependencies during actual usage
        """
    
    @staticmethod
    def get_dry_run_notice() -> str:
        """Return dry run mode notice."""
        return """
🔍 DRY RUN MODE:

Running in dry-run mode - no Azure API calls will be made.
This mode is useful for:
• Testing package discovery without Azure authentication
• Understanding what domains would be discovered
• Validating input files before running full analysis

Note: Workspace analysis is skipped in dry-run mode.
        """ 