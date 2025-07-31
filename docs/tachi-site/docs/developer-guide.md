---
sidebar_position: 6
---

# Developer Guide

Guide for developers who want to contribute to or extend tachi.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- uv package manager
- Git
- Docker (for testing generated configurations)

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/Avidity-Dev/tachi.git
cd tachi

# Create a virtual environment with uv
uv venv

# Install in development mode
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

## Project Structure

```
tachi/
├── src/tachi/
│   ├── __init__.py
│   ├── cli.py              # CLI commands and interface
│   ├── config.py           # Configuration dataclasses
│   ├── azure_generator.py  # Workflow generation logic
│   └── templates/azure/    # Jinja2 templates
│       ├── workflows/
│       │   ├── pr-deploy.yaml.j2
│       │   ├── pr-cleanup.yaml.j2
│       │   ├── stage-deploy.yaml.j2
│       │   └── prod-deploy.yaml.j2
│       ├── container-apps/
│       │   └── config.yaml.j2
│       └── SETUP.md.j2
├── tests/
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_generator.py
├── examples/               # Example configurations
└── pyproject.toml         # Project configuration
```

## Architecture

### Core Components

#### 1. Configuration (`config.py`)
Defines dataclasses for configuration:
- `Service`: Individual service configuration
- `AzureConfig`: Azure-specific settings
- `ProjectConfig`: Top-level project configuration

```python
@dataclass
class Service:
    name: str
    dockerfile: str = "Dockerfile"
    port: int = 8000
    external: bool = True
    cpu: float = 0.25
    memory: str = "0.5Gi"
    min_replicas: int = 1
    max_replicas: int = 10
    context: str = "."
```

#### 2. CLI (`cli.py`)
Implements Click commands:
- `generate`: Create workflows and configurations
- `validate`: Validate configuration files

```python
@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True))
def generate(config):
    """Generate GitHub Actions workflows"""
    # Implementation
```

#### 3. Generator (`azure_generator.py`)
Handles template rendering and file generation:
- Loads Jinja2 templates
- Applies configuration to templates
- Writes output files

```python
class AzureGenerator:
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            variable_start_string='[[',  # Custom delimiters
            variable_end_string=']]'
        )
```

### Template System

tachi uses Jinja2 templates with custom delimiters to avoid conflicts with GitHub Actions syntax:

- Variables: `[[ variable ]]` instead of `{{ variable }}`
- Blocks: `[% if condition %]` instead of `{% if condition %}`

Example template snippet:
```yaml
name: Deploy to [[ environment|title ]]

on:
  [% if environment == "production" and strategy == "trunk-release" %]
  push:
    tags:
      - 'v*'
  [% endif %]
```

## Adding Features

### Adding a New Command

1. Add command function in `cli.py`:
```python
@cli.command()
@click.option("--format", type=click.Choice(["json", "yaml"]))
def export(format):
    """Export configuration in different formats"""
    # Implementation
```

2. Add tests in `tests/test_cli.py`:
```python
def test_export_command(runner):
    result = runner.invoke(cli, ["export", "--format", "json"])
    assert result.exit_code == 0
```

### Adding Configuration Options

1. Update dataclass in `config.py`:
```python
@dataclass
class Service:
    # Existing fields...
    health_check_path: str = "/health"  # New field
```

2. Update validation if needed:
```python
def validate(self) -> List[str]:
    errors = []
    if not self.health_check_path.startswith("/"):
        errors.append("health_check_path must start with /")
    return errors
```

3. Update templates to use new field:
```yaml
configuration:
  ingress:
    customDomains: []
    healthCheck:
      path: [[ service.health_check_path ]]
```

### Adding a New Deployment Strategy

1. Add strategy to valid list in `config.py`:
```python
valid_strategies = ["trunk-direct", "trunk-release", "trunk-release-stage", "new-strategy"]
```

2. Update workflow selection in `azure_generator.py`:
```python
def _get_workflows_for_strategy(self, strategy: str) -> List[str]:
    workflows = {
        "trunk-direct": ["pr-deploy", "prod-deploy", "pr-cleanup"],
        "new-strategy": ["custom-workflow", "pr-deploy", "pr-cleanup"],
    }
    return workflows.get(strategy, workflows["trunk-direct"])
```

3. Create new workflow templates as needed

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=tachi

# Run specific test file
uv run pytest tests/test_config.py

# Run with verbose output
uv run pytest -v
```

### Writing Tests

Follow existing patterns for consistency:

```python
class TestNewFeature:
    def test_feature_happy_path(self):
        """Test feature with valid input"""
        # Arrange
        config = create_valid_config()
        
        # Act
        result = process_feature(config)
        
        # Assert
        assert result.success
        assert result.output == expected_output
    
    def test_feature_error_handling(self):
        """Test feature with invalid input"""
        # Test error cases
```

### Test Coverage

Aim for high test coverage:
- Unit tests for all public functions
- Integration tests for CLI commands
- Edge cases and error conditions

## Code Style

### Python Style

- Follow PEP 8
- Use type hints for function parameters
- Add docstrings to all public functions
- Use absolute imports

```python
from typing import List, Optional, Dict
from pathlib import Path

def generate_workflows(
    config: ProjectConfig,
    output_dir: Path,
    dry_run: bool = False
) -> List[Path]:
    """
    Generate workflow files from configuration.
    
    Args:
        config: Project configuration
        output_dir: Output directory path
        dry_run: Preview mode without writing files
        
    Returns:
        List of generated file paths
    """
    # Implementation
```

### Template Style

- Use clear variable names
- Add comments for complex logic
- Keep indentation consistent
- Use includes for repeated sections

```yaml
# [% if strategy == "trunk-release-stage" %]
# This workflow deploys to staging on merge to main
# [% endif %]
```

## Contributing

### Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

### Pull Request Guidelines

- Clear description of changes
- Tests for new functionality
- Documentation updates
- No breaking changes without discussion
- Follow existing code style

### Commit Messages

Use conventional commits:
- `feat: Add new deployment strategy`
- `fix: Correct CPU validation range`
- `docs: Update configuration examples`
- `test: Add tests for CLI commands`
- `refactor: Simplify template loading`

## Debugging

### Enable Debug Output

```python
# In development
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Template Rendering

```python
from tachi.azure_generator import AzureGenerator
from tachi.config import load_config

config = load_config("test.yaml")
generator = AzureGenerator(template_dir)
output = generator.render_template("workflows/pr-deploy.yaml.j2", {"config": config})
print(output)
```

### Common Issues

1. **Template Syntax Errors**
   - Check Jinja2 syntax
   - Verify custom delimiters
   - Test template in isolation

2. **Configuration Validation**
   - Add debug prints in validate()
   - Check error messages
   - Verify data types

3. **File Generation**
   - Check file permissions
   - Verify paths exist
   - Test with --dry-run first

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release PR
4. Tag release after merge
5. Build and publish to PyPI (if applicable)

## Getting Help

- Open an issue for bugs
- Start a discussion for features
- Check existing issues first
- Provide minimal reproducible examples