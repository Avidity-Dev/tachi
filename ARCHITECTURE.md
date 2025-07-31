# Architecture Plan for 'tachi' - GitHub Actions CI/CD CLI Tool

## Tool Overview
**tachi** is a Python CLI tool using `uv` that generates GitHub Actions workflows for Azure Container Apps deployments. Built with simplicity in mind, it focuses on delivering value quickly while keeping the door open for future expansion.

## Core Principles
1. **Start simple**: Direct implementation without premature abstractions
2. **Ship fast**: 2-week implementation timeline
3. **Prove value**: Get feedback before adding complexity
4. **YAGNI**: Add abstractions only when needed

## Project Structure
```
tachi/
├── pyproject.toml
├── README.md
├── src/
│   └── tachi/
│       ├── __init__.py
│       ├── cli.py              # Click CLI interface
│       ├── config.py           # Simple dataclasses
│       ├── azure_generator.py  # Direct Azure implementation
│       ├── templates/
│       │   └── azure/
│       │       ├── dev-deploy.yaml.j2
│       │       ├── stage-deploy.yaml.j2
│       │       ├── prod-deploy.yaml.j2
│       │       ├── pr-cleanup.yaml.j2
│       │       └── container-apps/
│       │           └── app.yaml.j2
│       └── validator.py        # Configuration validation
└── tests/
    ├── test_config.py
    ├── test_generator.py
    └── test_cli.py
```

## Key Components

### 1. Configuration (`config.py`)
```python
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Service:
    """Service configuration"""
    name: str
    dockerfile: str
    port: int
    external: bool = True
    cpu: float = 0.5
    memory: str = "1.0Gi"
    min_replicas: int = 1
    max_replicas: int = 10
    context: str = "."

    def validate(self) -> List[str]:
        """Simple validation"""
        errors = []
        if self.port <= 0 or self.port > 65535:
            errors.append(f"Service {self.name}: Invalid port {self.port}")
        if self.cpu <= 0:
            errors.append(f"Service {self.name}: CPU must be > 0")
        if self.min_replicas < 0:
            errors.append(f"Service {self.name}: min_replicas must be >= 0")
        if self.max_replicas < self.min_replicas:
            errors.append(f"Service {self.name}: max_replicas must be >= min_replicas")
        return errors


@dataclass
class AzureConfig:
    """Azure-specific configuration"""
    resource_group: str
    registry: str
    location: str = "westus2"
    log_analytics_workspace_id: Optional[str] = None
    log_analytics_workspace_key: Optional[str] = None


@dataclass
class ProjectConfig:
    """Project configuration"""
    name: str
    strategy: str  # "trunk-release" or "trunk-direct"
    azure: AzureConfig
    services: List[Service]

    def validate(self) -> List[str]:
        """Validate complete configuration"""
        errors = []
        if not self.name:
            errors.append("Project name is required")
        if self.strategy not in ["trunk-release", "trunk-direct"]:
            errors.append(f"Invalid strategy: {self.strategy}")
        if not self.services:
            errors.append("At least one service is required")

        # Validate each service
        for service in self.services:
            errors.extend(service.validate())

        # Check for duplicate service names
        names = [s.name for s in self.services]
        if len(names) != len(set(names)):
            errors.append("Duplicate service names found")

        return errors
```

### 2. Azure Generator (`azure_generator.py`)
```python
from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, FileSystemLoader

from tachi.config import ProjectConfig


class AzureGenerator:
    """Generates Azure Container Apps workflows and configs"""

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(self, config: ProjectConfig, output_dir: Path) -> None:
        """Generate all workflows and configurations"""
        # Create output directories
        workflow_dir = output_dir / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)

        container_apps_dir = output_dir / "container-apps" / "configs"
        for env in ["dev", "staging", "production"]:
            (container_apps_dir / env).mkdir(parents=True, exist_ok=True)

        # Generate workflows based on strategy
        workflows = self._get_workflows_for_strategy(config.strategy)

        for workflow_name in workflows:
            self._generate_workflow(workflow_name, config, workflow_dir)

        # Always generate PR cleanup workflow
        self._generate_workflow("pr-cleanup", config, workflow_dir)

        # Generate container app configs
        self._generate_container_configs(config, container_apps_dir)

        # Generate setup instructions
        self._generate_setup_instructions(config, output_dir)

    def _get_workflows_for_strategy(self, strategy: str) -> List[str]:
        """Get workflow list based on deployment strategy"""
        if strategy == "trunk-release":
            return ["dev-deploy", "stage-deploy", "prod-deploy"]
        else:  # trunk-direct
            return ["dev-deploy", "prod-deploy"]

    def _generate_workflow(self, name: str, config: ProjectConfig, output_dir: Path) -> None:
        """Generate a single workflow file"""
        template = self.env.get_template(f"azure/{name}.yaml.j2")
        content = template.render(
            project=config,
            azure=config.azure,
            services=config.services
        )

        output_path = output_dir / f"{name}.yaml"
        output_path.write_text(content)

    def _generate_container_configs(self, config: ProjectConfig, output_dir: Path) -> None:
        """Generate Container Apps configuration files"""
        template = self.env.get_template("azure/container-apps/app.yaml.j2")

        environments = ["dev", "staging", "production"] if config.strategy == "trunk-release" else ["dev", "production"]

        for env in environments:
            for service in config.services:
                content = template.render(
                    service=service,
                    environment=env,
                    registry=config.azure.registry
                )

                output_path = output_dir / env / f"{service.name}.yaml"
                output_path.write_text(content)

    def _generate_setup_instructions(self, config: ProjectConfig, output_dir: Path) -> None:
        """Generate SETUP.md with required secrets and instructions"""
        secrets = self._get_required_secrets(config)

        content = f"""# Setup Instructions for {config.name}

## Required GitHub Secrets

Add these secrets to your GitHub repository:

"""
        for secret in secrets:
            content += f"- **{secret['name']}**: {secret['description']}\n"

        content += """
## Azure Resources

Ensure these resources exist:
"""
        content += f"- Resource Group: `{config.azure.resource_group}`\n"
        content += f"- Container Registry: `{config.azure.registry}`\n"
        content += f"- Container App Environment (will be created automatically)\n"

        setup_path = output_dir / "SETUP.md"
        setup_path.write_text(content)

    def _get_required_secrets(self, config: ProjectConfig) -> List[Dict[str, str]]:
        """Get list of required GitHub secrets"""
        return [
            {"name": "AZURE_CREDENTIALS", "description": "Azure service principal credentials"},
            {"name": "AZURE_CLIENT_ID", "description": "Azure service principal client ID"},
            {"name": "AZURE_CLIENT_SECRET", "description": "Azure service principal client secret"},
            {"name": "AZURE_TENANT_ID", "description": "Azure tenant ID"},
            {"name": "DB_PASSWORD", "description": "Database password (if using database service)"},
            {"name": "LOG_ANALYTICS_WORKSPACE_ID", "description": "Log Analytics workspace ID"},
            {"name": "LOG_ANALYTICS_WORKSPACE_KEY", "description": "Log Analytics workspace key"}
        ]
```

### 3. CLI (`cli.py`)
```python
from pathlib import Path
from typing import Optional

import click
import yaml

from tachi.config import ProjectConfig, Service, AzureConfig
from tachi.azure_generator import AzureGenerator
from tachi.validator import validate_azure_resources


@click.group()
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
        # Load from YAML file
        config_path = Path(config)
        with open(config_path) as f:
            data = yaml.safe_load(f)

        project_config = _parse_config(data)
    else:
        # Interactive mode
        project_config = _interactive_config()

    # Validate configuration
    errors = project_config.validate()
    if errors:
        click.echo("Configuration errors:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        raise click.Exit(1)

    # Generate files
    template_dir = Path(__file__).parent / "templates"
    generator = AzureGenerator(template_dir)
    generator.generate(project_config, output_dir)

    click.echo(f"✅ Generated CI/CD configuration in {output_dir}")
    click.echo(f"📝 See SETUP.md for next steps")


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True), required=True, help='Configuration file')
def validate(config: str):
    """Validate configuration file"""
    config_path = Path(config)
    with open(config_path) as f:
        data = yaml.safe_load(f)

    project_config = _parse_config(data)
    errors = project_config.validate()

    if errors:
        click.echo("❌ Configuration errors:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        raise click.Exit(1)
    else:
        click.echo("✅ Configuration is valid")


def _parse_config(data: dict) -> ProjectConfig:
    """Parse YAML data into ProjectConfig"""
    azure_data = data.get('azure', {})
    azure_config = AzureConfig(
        resource_group=azure_data['resource_group'],
        registry=azure_data['registry'],
        location=azure_data.get('location', 'westus2')
    )

    services = []
    for service_data in data.get('services', []):
        service = Service(
            name=service_data['name'],
            dockerfile=service_data['dockerfile'],
            port=service_data['port'],
            external=service_data.get('external', True),
            cpu=service_data.get('cpu', 0.5),
            memory=service_data.get('memory', '1.0Gi'),
            min_replicas=service_data.get('min_replicas', 1),
            max_replicas=service_data.get('max_replicas', 10),
            context=service_data.get('context', '.')
        )
        services.append(service)

    return ProjectConfig(
        name=data['name'],
        strategy=data.get('strategy', 'trunk-release'),
        azure=azure_config,
        services=services
    )


def _interactive_config() -> ProjectConfig:
    """Interactive configuration wizard"""
    click.echo("Welcome to tachi! Let's set up your CI/CD pipeline.")

    name = click.prompt("Project name")
    strategy = click.prompt(
        "Deployment strategy",
        type=click.Choice(['trunk-release', 'trunk-direct']),
        default='trunk-release'
    )

    # Azure configuration
    click.echo("\nAzure Configuration:")
    resource_group = click.prompt("Resource group")
    registry = click.prompt("Container registry")
    location = click.prompt("Location", default="westus2")

    azure_config = AzureConfig(
        resource_group=resource_group,
        registry=registry,
        location=location
    )

    # Services
    services = []
    click.echo("\nLet's configure your services:")

    while True:
        if services:
            if not click.confirm("Add another service?"):
                break

        service_name = click.prompt("Service name")
        dockerfile = click.prompt("Dockerfile path", default=f"./{service_name}/Dockerfile")
        port = click.prompt("Port", type=int, default=8000)
        external = click.confirm("External access?", default=True)

        service = Service(
            name=service_name,
            dockerfile=dockerfile,
            port=port,
            external=external
        )
        services.append(service)

    return ProjectConfig(
        name=name,
        strategy=strategy,
        azure=azure_config,
        services=services
    )


if __name__ == '__main__':
    cli()
```

## Configuration File (`tachi.yaml`)
```yaml
name: my-app
strategy: trunk-release  # or trunk-direct

azure:
  resource_group: rg-my-app
  registry: myregistry.azurecr.io
  location: westus2

services:
  - name: frontend
    dockerfile: ./frontend/Dockerfile
    port: 3000
    external: true
    cpu: 0.5
    memory: 1.0Gi

  - name: api
    dockerfile: ./api/Dockerfile
    port: 8000
    external: false
    cpu: 1.0
    memory: 2.0Gi

  - name: postgres
    dockerfile: ./postgres/Dockerfile
    port: 5432
    external: false
    cpu: 0.5
    memory: 1.0Gi
    min_replicas: 1
    max_replicas: 1
```

## Implementation Timeline

### Week 1: Core Functionality
1. **Day 1-2**: Project setup, basic CLI structure
2. **Day 3-4**: Configuration parsing and validation
3. **Day 5**: Azure generator implementation

### Week 2: Templates & Polish
1. **Day 1-2**: Create Jinja2 templates from ca-1099-risk-assessment
2. **Day 3**: Testing and error handling
3. **Day 4**: Documentation and examples
4. **Day 5**: Internal deployment and feedback

## Future Additions (When Needed)

### When to Add Abstractions
- **Provider interface**: When adding second cloud provider (GCP/AWS)
- **Strategy pattern**: When patterns emerge from 3+ strategies
- **Template inheritance**: When template duplication becomes painful
- **Event system**: When users need hooks for customization
- **Dependency injection**: When unit testing becomes difficult

### Potential Future Structure
Only implement when actually needed:
```
providers/
├── base.py         # Only when 2nd provider added
├── azure.py
└── gcp.py          # When GCP support needed

strategies/
├── base.py         # Only when 3rd strategy added
├── trunk_release.py
├── trunk_direct.py
└── gitflow.py      # When requested
```

## Key Decisions

1. **Direct implementation**: No unnecessary abstractions
2. **Single provider focus**: Azure Container Apps only initially
3. **Simple validation**: Inline validation in dataclasses
4. **Flat structure**: Everything in main package directory
5. **Template simplicity**: Direct Jinja2 templates without inheritance

## Benefits of This Approach

1. **Fast delivery**: 2 weeks vs 5+ weeks
2. **Easy to understand**: ~500 lines of code total
3. **Quick onboarding**: New developers productive in hours
4. **Proven patterns**: Extract abstractions from real usage
5. **User feedback**: Ship early, iterate based on needs

This simplified architecture focuses on delivering value quickly while maintaining code quality. Abstractions can be added later when patterns emerge from actual usage.