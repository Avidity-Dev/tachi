# Phase 1: Project Setup Tasks (Days 1-2)

## Overview
This document provides detailed implementation instructions for Agent D to complete Phase 1 of the tachi CLI tool development.

## Task 1: Initialize Project with uv

### Steps:

1. Initialize with uv:
   ```bash
   uv init
   ```

2. Update pyproject.toml with the following content:
   ```toml
   [project]
   name = "tachi"
   version = "0.1.0"
   description = "GitHub Actions CI/CD generator for Azure Container Apps"
   authors = [{name = "Your Name", email = "your.email@example.com"}]
   requires-python = ">=3.10"
   dependencies = [
       "click>=8.1.0",
       "jinja2>=3.1.0",
       "pyyaml>=6.0",
   ]

   [project.scripts]
   tachi = "tachi.cli:cli"

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [tool.uv]
   dev-dependencies = [
       "pytest>=7.4.0",
       "pytest-cov>=4.1.0",
   ]
   ```

## Task 2: Create Project Structure

### Create the following directory structure:
```
tachi/
├── pyproject.toml (already created)
├── README.md
├── src/
│   └── tachi/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── azure_generator.py
│       ├── validator.py
│       └── templates/
│           └── azure/
│               ├── dev-deploy.yaml.j2
│               ├── stage-deploy.yaml.j2
│               ├── prod-deploy.yaml.j2
│               ├── pr-cleanup.yaml.j2
│               └── container-apps/
│                   └── app.yaml.j2
└── tests/
    ├── __init__.py
    ├── test_config.py
    ├── test_generator.py
    └── test_cli.py
```

### File contents:

1. **src/tachi/__init__.py**:
   ```python
   """tachi - GitHub Actions CI/CD generator for Azure Container Apps"""
   __version__ = "0.1.0"
   ```

2. **README.md**:
   ```markdown
   # tachi

   A simple CLI tool for generating GitHub Actions workflows for Azure Container Apps deployments.

   ## Installation

   ```bash
   uv pip install -e .
   ```

   ## Usage

   ```bash
   tachi generate --config tachi.yaml
   ```

   ## Development

   This project uses `uv` for package management. To set up the development environment:

   ```bash
   uv sync
   ```
   ```

## Task 3: Implement Minimal CLI Entry Point

### Create src/tachi/cli.py:
```python
"""CLI interface for tachi"""
from pathlib import Path
from typing import Optional

import click


@click.group()
@click.version_option()
def cli():
    """tachi - GitHub Actions CI/CD generator for Azure Container Apps"""
    pass


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file')
@click.option('--output', '-o', type=click.Path(), default='.', help='Output directory')
def generate(config: Optional[str], output: str):
    """Generate GitHub Actions workflows and configurations"""
    output_dir = Path(output)

    if config:
        click.echo(f"Loading configuration from: {config}")
        click.echo(f"Output directory: {output_dir.absolute()}")
        # TODO: Implement configuration loading and generation
        click.echo("Generation complete! (placeholder)")
    else:
        click.echo("Interactive mode not yet implemented")
        click.echo("Please provide a configuration file with --config")


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True), required=True, help='Configuration file')
def validate(config: str):
    """Validate configuration file"""
    click.echo(f"Validating configuration: {config}")
    # TODO: Implement validation
    click.echo("Validation complete! (placeholder)")


if __name__ == '__main__':
    cli()
```

### Create placeholder files:

1. **src/tachi/config.py**:
   ```python
   """Configuration dataclasses for tachi"""
   # TODO: Implement in Phase 2
   ```

2. **src/tachi/azure_generator.py**:
   ```python
   """Azure Container Apps workflow generator"""
   # TODO: Implement in Phase 3
   ```

3. **src/tachi/validator.py**:
   ```python
   """Configuration validation utilities"""
   # TODO: Implement as needed
   ```

4. **Template placeholders** (create empty files):
   - src/tachi/templates/azure/dev-deploy.yaml.j2
   - src/tachi/templates/azure/stage-deploy.yaml.j2
   - src/tachi/templates/azure/prod-deploy.yaml.j2
   - src/tachi/templates/azure/pr-cleanup.yaml.j2
   - src/tachi/templates/azure/container-apps/app.yaml.j2

## Verification Steps

After completing all tasks, verify:

1. **Install the package**:
   ```bash
   uv pip install -e .
   ```

2. **Test the CLI**:
   ```bash
   tachi --help
   tachi generate --help
   tachi validate --help
   ```

3. **Expected output for `tachi --help`**:
   ```
   Usage: tachi [OPTIONS] COMMAND [ARGS]...

     tachi - GitHub Actions CI/CD generator for Azure Container Apps

   Options:
     --version  Show the version and exit.
     --help     Show this message and exit.

   Commands:
     generate  Generate GitHub Actions workflows and configurations
     validate  Validate configuration file
   ```

## Deliverables Checklist

- [ ] Project initialized with uv
- [ ] pyproject.toml configured with dependencies
- [ ] Complete directory structure created
- [ ] CLI entry point working with two commands
- [ ] Package installable with `uv pip install -e .`
- [ ] CLI accessible via `tachi` command
- [ ] All placeholder files created

## Notes for Agent D

- Keep it simple - this is just the foundation
- Don't implement any actual functionality yet
- Focus on getting the structure right
- The CLI should work but commands can show placeholder messages
- Total code for Phase 1 should be under 100 lines

Once Phase 1 is complete, we'll move on to Phase 2 where we implement the configuration dataclasses.