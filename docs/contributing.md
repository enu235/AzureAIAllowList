# Contributing Guide

**Welcome!** 🎉 Thank you for your interest in contributing to the Azure AI Foundry & ML Package Allowlist Tool.

> **🚨 AS IS DISCLAIMER**: This tool is provided "AS IS" without warranty of any kind, express or implied. By contributing, you acknowledge that all contributions are made under the same terms.

## 🎯 How You Can Help

This tool is designed to be **community-driven** and **easy to extend**. We welcome contributions in many forms:

### 🔧 **Code Contributions**
- 🌍 Additional package manager support (npm, gradle, etc.)
- 🔒 Enhanced security analysis features
- 🐛 Bug fixes and performance improvements
- 🧪 More comprehensive testing coverage
- 🌐 Internationalization support

### 📚 **Documentation**
- 📖 User guides and tutorials
- 💡 Example configurations
- 🔧 Troubleshooting guides
- 🎥 Video walkthroughs
- 🌍 Translations

### 🧪 **Testing & Quality**
- 🐛 Bug reports with reproduction steps
- 🧪 Test case contributions
- 📊 Performance analysis
- 🔍 Security audits
- 💻 Platform compatibility testing

### 🎨 **User Experience**
- 🎨 UI/UX improvements for interactive mode
- 📱 Accessibility enhancements
- 🎯 User journey optimizations
- 📋 Better error messages

---

## 🚀 Quick Start for Contributors

### 1. Fork & Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/AzureAIAllowList.git
cd AzureAIAllowList

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/AzureAIAllowList.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv contrib-env
source contrib-env/bin/activate  # On Windows: contrib-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available
```

### 3. Create Feature Branch

```bash
# Get latest changes
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-amazing-feature
```

### 4. Make Your Changes

Follow our [coding standards](#coding-standards) and ensure all tests pass.

### 5. Submit Pull Request

```bash
# Commit your changes
git add .
git commit -m "feat: add amazing feature for package discovery"

# Push to your fork
git push origin feature/your-amazing-feature

# Open PR on GitHub
```

---

## 📋 Contribution Guidelines

### 🎯 **What We're Looking For**

**High Priority Areas:**
1. **Package Manager Support** - Support for npm, gradle, Maven, NuGet, etc.
2. **Security Enhancements** - Better vulnerability detection and analysis
3. **Interactive Mode Improvements** - Enhanced user experience features
4. **Error Handling** - More graceful error recovery and user guidance
5. **Documentation** - User guides, examples, and API documentation

**Medium Priority Areas:**
1. **Performance Optimizations** - Faster analysis and discovery
2. **Platform Support** - Better Windows/Linux/macOS compatibility
3. **Testing Coverage** - Unit tests, integration tests, end-to-end tests
4. **Accessibility** - Screen reader support, keyboard navigation
5. **Internationalization** - Multi-language support

### ✅ **Before You Start**

1. **Check Existing Issues**
   - Browse [open issues](https://github.com/your-repo/issues)
   - Look for `good first issue` or `help wanted` labels
   - Comment on issues you want to work on

2. **Discuss Major Changes**
   - Open an issue for significant features
   - Get feedback before starting large work
   - Consider backward compatibility

3. **Review Existing Code**
   - Understand the current architecture
   - Follow established patterns
   - Check the [architecture documentation](connectivity-architecture.md)

---

## 🏗️ Development Setup

### Directory Structure

```
AzureAIAllowList/
├── main.py                    # Main CLI entry point
├── src/                       # Core application code
│   ├── interactive/           # Interactive mode components
│   ├── connectivity/          # Network analysis modules
│   ├── package_discoverer.py # Package discovery logic
│   ├── utils/                 # Shared utilities
│   └── config/                # Configuration management
├── docs/                      # Documentation
├── tests/                     # Test suite
├── examples/                  # Example configurations
└── requirements.txt           # Dependencies
```

### Key Components

1. **Interactive Mode** (`src/interactive/`)
   - `interactive_flow.py` - Main orchestrator
   - `auth_handler.py` - Azure authentication
   - `workspace_selector.py` - Workspace discovery
   - `analysis_selector.py` - Analysis configuration

2. **Package Discovery** (`src/package_discoverer.py`)
   - Factory pattern for package managers
   - Extensible for new package types
   - Platform-aware dependency resolution

3. **Connectivity Analysis** (`src/connectivity/`)
   - Network configuration analysis
   - Security assessment
   - Resource discovery

### Adding New Package Manager Support

**Example: Adding npm support**

1. **Create Discoverer Class**
   ```python
   class NpmDiscoverer(PackageDiscoverer):
       def discover_urls(self, package_file: str, **kwargs) -> DiscoveryResult:
           # Parse package.json
           # Resolve dependencies
           # Extract registry URLs
           pass
   ```

2. **Register in Factory**
   ```python
   # In PackageDiscovererFactory
   def create_discoverer(self, package_type: str) -> PackageDiscoverer:
       if package_type == 'npm':
           return NpmDiscoverer()
       # ... existing types
   ```

3. **Add CLI Support**
   ```python
   # In cli_params.py
   @click.option('--package-json', type=click.Path(exists=True),
                 help='Path to package.json file')
   ```

4. **Add File Detection**
   ```python
   # In analysis_selector.py
   def discover_package_files(self) -> List[Tuple[str, str]]:
       files = []
       if Path('package.json').exists():
           files.append(('npm', 'package.json'))
       # ... existing discovery
   ```

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_package_discoverer.py

# Run interactive mode tests
python -m pytest tests/test_interactive/ -v
```

### Test Requirements

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows
4. **Mock Azure Services** - Don't hit real Azure APIs in tests

### Writing Tests

**Example Test Structure:**
```python
import pytest
from unittest.mock import Mock, patch
from src.package_discoverer import PipDiscoverer

class TestPipDiscoverer:
    @pytest.fixture
    def discoverer(self):
        return PipDiscoverer()
    
    @patch('subprocess.run')
    def test_discover_urls_success(self, mock_run, discoverer):
        # Arrange
        mock_run.return_value.stdout = "package==1.0.0"
        mock_run.return_value.returncode = 0
        
        # Act
        result = discoverer.discover_urls('requirements.txt')
        
        # Assert
        assert len(result.domains) > 0
        assert 'pypi.org' in str(result.domains)
```

---

## 📝 Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

```python
# ✅ Good
class PackageDiscoverer:
    """Base class for package discovery implementations."""
    
    def discover_urls(self, package_file: str, **kwargs) -> DiscoveryResult:
        """
        Discover package download URLs from a package file.
        
        Args:
            package_file: Path to the package file
            **kwargs: Additional options
            
        Returns:
            DiscoveryResult containing domains and metadata
        """
        pass

# ✅ Good - Type hints
def analyze_workspace(workspace_name: str, 
                     resource_group: str,
                     subscription_id: Optional[str] = None) -> AnalysisResult:
    pass

# ✅ Good - Error handling
try:
    result = azure_operation()
except AzureError as e:
    logger.error(f"Azure operation failed: {str(e)}")
    return AnalysisResult(success=False, error=str(e))
```

### Documentation Standards

**Docstring Format:**
```python
def complex_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    One-line summary of what the function does.
    
    Longer description if needed. Explain the purpose, behavior,
    and any important considerations.
    
    Args:
        param1: Description of first parameter
        param2: Description of optional parameter with default behavior
        
    Returns:
        Dictionary containing result data with keys:
        - 'success': Boolean indicating operation success
        - 'data': Any result data
        - 'error': Error message if success is False
        
    Raises:
        ValueError: When param1 is empty or invalid
        AzureError: When Azure API calls fail
        
    Example:
        >>> result = complex_function("workspace-name")
        >>> if result['success']:
        ...     print(f"Data: {result['data']}")
    """
    pass
```

### Interactive Mode Standards

**Rich UI Components:**
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# ✅ Good - Consistent styling
def display_workspaces(workspaces: List[WorkspaceInfo]):
    console = Console()
    
    table = Table(title="Discovered Workspaces")
    table.add_column("#", style="dim")
    table.add_column("Name", style="bold cyan")
    table.add_column("Type", style="bright_magenta")
    
    for i, ws in enumerate(workspaces, 1):
        icon = "🔮" if ws.hub_type == "ai-foundry" else "🤖"
        table.add_row(str(i), ws.name, f"{icon} {ws.hub_type}")
    
    console.print(table)
```

**Error Handling in Interactive Mode:**
```python
# ✅ Good - Graceful error handling
try:
    workspaces = discover_workspaces(subscription_id)
    if not workspaces:
        console.print("⚠️  No workspaces found", style="yellow")
        return handle_no_workspaces_scenario()
except PermissionError:
    console.print("❌ Access denied", style="red")
    return suggest_permission_solutions()
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    console.print(f"❌ Unexpected error: {str(e)}", style="red")
    return False
```

---

## 🔍 Code Review Process

### What We Look For

1. **Functionality** ✅
   - Does the code work as intended?
   - Are edge cases handled?
   - Is error handling comprehensive?

2. **Code Quality** ✅
   - Follows coding standards
   - Proper type hints
   - Clear variable names
   - Reasonable function length

3. **Testing** ✅
   - Adequate test coverage
   - Tests cover edge cases
   - Tests are readable and maintainable

4. **Documentation** ✅
   - Clear docstrings
   - Updated user documentation
   - Inline comments for complex logic

5. **Backward Compatibility** ✅
   - Existing functionality preserved
   - Migration path for breaking changes
   - Deprecation warnings when appropriate

### Review Timeline

- **Small fixes** (< 50 lines): 1-2 business days
- **Medium features** (50-200 lines): 3-5 business days  
- **Large features** (200+ lines): 1-2 weeks

---

## 🏷️ Issue Management

### Issue Types

We use these labels for organization:

- 🐛 **bug** - Something isn't working correctly
- ✨ **enhancement** - New feature or improvement
- 📚 **documentation** - Documentation improvements
- 🧪 **testing** - Testing-related issues
- 🆘 **help wanted** - Extra attention needed
- 🥇 **good first issue** - Good for newcomers
- 🔒 **security** - Security-related issues
- 🚀 **performance** - Performance improvements

### Issue Templates

**Bug Report:**
```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Run `python main.py`
2. Select option X
3. See error

## Expected Behavior
What should happen

## Actual Behavior  
What actually happens

## Environment
- OS: 
- Python version:
- Azure CLI version:
- Tool version:

## Additional Context
Logs, screenshots, etc.
```

**Feature Request:**
```markdown
## Feature Description
Clear description of the new feature

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How do you envision this working?

## Alternatives Considered
Other approaches you've considered

## Additional Context
Mockups, examples, etc.
```

---

## 🎉 Recognition

### Contributors

We recognize contributors in several ways:

1. **README Credits** - Listed in the main README
2. **Release Notes** - Mentioned in version releases  
3. **GitHub Recognition** - GitHub contributor stats
4. **Special Thanks** - Call-outs for significant contributions

### Contribution Types

All contributions are valuable:

- 💻 **Code** - Feature development, bug fixes
- 📚 **Documentation** - Guides, examples, translations
- 🧪 **Testing** - Test development, QA testing
- 🐛 **Bug Reports** - Detailed issue reporting
- 💡 **Ideas** - Feature suggestions, improvements
- 🎨 **Design** - UI/UX improvements
- 🌍 **Community** - Helping other users, discussions

---

## 📞 Getting Help

### Where to Ask Questions

1. **GitHub Discussions** 💬
   - General questions about usage
   - Feature discussions
   - Community help

2. **GitHub Issues** 🐛
   - Bug reports
   - Feature requests
   - Technical problems

3. **Code Reviews** 🔍
   - Questions about implementation
   - Design decisions
   - Best practices

### Response Times

- **Community discussions**: Usually within 1-2 days
- **Bug reports**: Within 1 week
- **Feature requests**: Within 2 weeks
- **Pull requests**: Within 1 week

---

## 📄 License & Legal

### Contribution License

By contributing to this project, you agree that your contributions will be licensed under the same **MIT License** that covers the project.

### Contributor Agreement

- ✅ Your contributions are your own original work
- ✅ You have the right to submit the contributions
- ✅ Your contributions are provided under the MIT License
- ✅ You understand the "AS IS" nature of the project

---

## 🙏 Thank You!

Every contribution makes this tool better for the entire Azure ML and AI Foundry community. Whether you're:

- 🐛 Fixing a typo
- ✨ Adding a major feature  
- 📚 Improving documentation
- 🧪 Writing tests
- 💡 Suggesting improvements

**Your effort is appreciated!** 🎉

---

> **💡 TIP**: Start small! Look for `good first issue` labels and familiarize yourself with the codebase before tackling larger features.

> **🚨 REMINDER**: This tool is provided "AS IS" without warranty. All contributions are made under the same terms. 