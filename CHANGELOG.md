# Changelog

All notable changes to the Azure AI Foundry & Machine Learning Package Allowlist Tool will be documented in this file.

> **⚠️ DISCLAIMER**: This changelog is provided "AS IS" without warranty of any kind. Users should thoroughly test all changes in non-production environments before applying to production systems.

## [0.5.0] - 2025-06-15 (Prerelease)

### 🚀 **Major Enhancements**

#### Azure AI Foundry Focus
- **Enhanced Azure AI Foundry Support**: Optimized default configuration for AI Foundry hubs
- **AI Foundry as Default**: Changed default `--hub-type` from `azure-ml` to `ai-foundry`
- **Advanced AI Features**: Comprehensive support for VS Code, HuggingFace, and Prompt Flow integrations
- **Intelligent Feature Detection**: Automatic recommendation of AI-specific features based on dependencies

#### Architecture Improvements
- **Modular Design**: Completely rewritten with modular architecture for better maintainability  
- **Enhanced Discovery Engine**: Improved package source detection and mapping
- **Better Error Handling**: More informative error messages and recovery mechanisms
- **Performance Optimizations**: Faster dependency resolution and reduced API calls

### ✨ **New Features**

#### AI Foundry Hub Features
- `--include-vscode`: Enable Visual Studio Code web integration
- `--include-huggingface`: Direct HuggingFace model hub access  
- `--include-prompt-flow`: Advanced AI workflow orchestration support
- `--custom-fqdns`: Flexible custom domain integration for enterprise scenarios

#### Enhanced Package Manager Support
- **Poetry Support**: Full `pyproject.toml` support with custom PyPI sources
- **Pipenv Support**: Complete `Pipfile` processing with source URL extraction
- **Multi-format Processing**: Simultaneous processing of multiple package manager files
- **Improved Conda Support**: Enhanced conda channel detection and mapping

#### Docker & Container Support
- **Updated Container Names**: Renamed to `azure-ai-foundry-package-tool` for clarity
- **Improved Docker Examples**: AI Foundry-focused container examples
- **Cross-platform Support**: Better ARM64/x86_64 compatibility

### 📊 **Documentation & Usability**

#### Comprehensive Documentation
- **New Package Discovery Guide**: Complete documentation of discovery methods and flows
- **Enhanced Troubleshooting Guide**: Detailed solutions for common issues
- **Azure ML Compatibility Guide**: Dedicated section ensuring Azure ML customers feel welcome
- **Mermaid Diagrams**: Visual workflow and architecture diagrams throughout

#### Better User Experience
- **Enhanced CLI Help**: More descriptive command-line options and examples
- **Improved Output**: Better formatted CLI commands and configuration files
- **Example Scripts**: Comprehensive example usage patterns and best practices
- **Verbose Logging**: Enhanced debugging capabilities with `--verbose` flag

### 🔒 **Azure ML Workspace Support **

#### Backward Compatibility
- **Complete Feature Parity**: All existing Azure ML functionality
- **Workspace Support**: Full compatibility with existing Azure ML workspaces
- **Migration Path**: Easy upgrade path to AI Foundry when ready
- **No Breaking Changes**: Existing scripts and automation continue to work

#### Azure ML Specific Features
- **Customer-Managed VNet**: Enhanced support for customer-managed virtual networks
- **Managed VNet**: Complete support for Azure ML managed virtual networks
- **All Network Modes**: Support for all Azure ML isolation modes
- **Enterprise Integration**: Continued support for existing enterprise workflows

### 🛠️ **Technical Improvements**

#### Core Engine
- **Transitive Dependency Resolution**: Improved algorithm for dependency tree analysis
- **Private Repository Detection**: Enhanced detection and guidance for private package sources
- **Platform-Specific Handling**: Better cross-platform package compatibility
- **Rate Limiting**: Built-in API rate limiting and retry mechanisms

#### Output Formats
- **CLI Commands**: Azure CLI command generation (default)
- **JSON Configuration**: Structured configuration for automation
- **YAML Configuration**: Human-readable configuration format
- **Enhanced Formatting**: Better readability and organization

### 🔧 **Configuration Changes**

#### Default Behavior Updates
- **Default Hub Type**: Changed from `azure-ml` to `ai-foundry`
- **Enhanced Feature Flags**: More granular control over AI features
- **Improved Validation**: Better input validation and error reporting
- **Smart Defaults**: Intelligent default configurations based on detected environment

#### Breaking Changes
- **None**: This release maintains full backward compatibility
- **Docker Service Names**: Container names updated (docker-compose users may need to update)
- **Default Hub Type**: May affect scripts that relied on `azure-ml` default (easily fixed with explicit `--hub-type`)

### 📋 **Quality & Testing**

#### Enhanced Reliability
- **Comprehensive Testing**: Extensive testing across both AI Foundry and Azure ML scenarios
- **Error Recovery**: Better handling of API failures and network issues  
- **Input Validation**: More robust validation of input files and parameters
- **Edge Case Handling**: Improved handling of complex dependency scenarios

#### Security & Compliance
- **Enhanced Disclaimers**: Strengthened "AS IS" disclaimers throughout documentation
- **Security Guidance**: Improved private repository handling and security recommendations
- **Compliance Documentation**: Clear guidance for regulated environments

### 🚧 **Known Issues & Limitations**

- **API Rate Limits**: PyPI and Conda API rate limits may affect large dependency trees (use `--dry-run` for testing)
- **Private Repository Access**: Some private repositories require manual configuration (guidance provided)
- **Cross-Platform Packages**: Some packages have platform-specific dependencies (warnings generated)

### 📈 **Migration Guide**

#### For New Users
- Start with Azure AI Foundry hub type for enhanced AI features
- Use provided example scripts and documentation
- Enable AI features as needed (`--include-vscode`, `--include-huggingface`)

#### For Existing Azure ML Users
- **No action required**: Existing configurations continue to work
- Consider adding `--hub-type azure-ml` to scripts for explicit configuration
- Explore AI Foundry features when ready to upgrade

#### For Docker Users
- Update `docker-compose.yml` service names if customized
- New container names: `azure-ai-foundry-package-tool*`
- All functionality remains the same

### 🎯 **Future Roadmap**

- Enhanced AI model catalog integration
- Additional package manager support (uv, PDM)
- Automated rule validation and testing
- Integration with Azure DevOps and GitHub Actions
- Enhanced private repository migration tools

---

## Contributing

We welcome contributions! This is a community-driven tool designed to help Azure AI Foundry and Azure ML customers succeed with network security configurations.

## Support

This tool is provided as-is by the community. For Azure platform-specific issues, please contact Microsoft Azure Support.

---

> **⚠️ REMINDER**: All versions of this tool are provided "AS IS" without warranty. Always thoroughly test configurations in non-production environments before applying to production systems. 
