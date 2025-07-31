"""Azure Container Apps workflow generator"""
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

from tachi.config import ProjectConfig


class AzureGenerator:
    """Generator for Azure Container Apps workflows and configurations"""
    
    def __init__(self, template_dir: Path):
        """Initialize generator with template directory"""
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            variable_start_string='[[',
            variable_end_string=']]',
            block_start_string='[%',
            block_end_string='%]'
        )
    
    def generate(self, config: ProjectConfig, output_dir: Path) -> None:
        """Generate all workflows and configurations"""
        # Create output directory structure
        workflows_dir = output_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        container_apps_dir = output_dir / "container-apps" / "configs"
        container_apps_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine workflows based on strategy
        workflows = self._get_workflows_for_strategy(config.strategy)
        
        # Generate each workflow
        for workflow_name in workflows:
            self._generate_workflow(config, workflow_name, workflows_dir)
        
        # Generate container app configurations
        self._generate_container_configs(config, container_apps_dir)
        
        # Generate setup instructions
        self._generate_setup_instructions(config, output_dir)
    
    def _get_workflows_for_strategy(self, strategy: str) -> List[str]:
        """Return workflow list based on deployment strategy"""
        if strategy == "basic":
            return ["dev-deploy", "stage-deploy", "prod-deploy"]
        elif strategy == "blue-green":
            return ["dev-deploy", "stage-deploy", "prod-deploy", "pr-cleanup"]
        elif strategy == "canary":
            return ["dev-deploy", "stage-deploy", "prod-deploy", "pr-cleanup"]
        else:
            return ["dev-deploy", "stage-deploy", "prod-deploy"]
    
    def _generate_workflow(self, config: ProjectConfig, workflow_name: str, output_dir: Path) -> None:
        """Generate a single workflow file from template"""
        template = self.env.get_template(f"{workflow_name}.yaml.j2")
        
        # Prepare context for template
        context = {
            "project": config,
            "azure": config.azure,
            "services": config.services
        }
        
        # Render template
        workflow_content = template.render(**context)
        
        # Write to file
        workflow_file = output_dir / f"{workflow_name}.yaml"
        workflow_file.write_text(workflow_content)
    
    def _generate_container_configs(self, config: ProjectConfig, output_dir: Path) -> None:
        """Generate container app configuration files from template"""
        template = self.env.get_template("container-apps/app.yaml.j2")
        
        for service in config.services:
            # Prepare context for each service
            context = {
                "project": config,
                "azure": config.azure,
                "service": service,
                "environment": "{{ environment }}"  # This will be replaced at deploy time
            }
            
            # Render template
            config_content = template.render(**context)
            
            # Write to file (as YAML, not JSON)
            config_file = output_dir / f"{service.name}.yaml"
            config_file.write_text(config_content)
    
    def _generate_setup_instructions(self, config: ProjectConfig, output_dir: Path) -> None:
        """Generate SETUP.md with required secrets and configuration"""
        setup_content = f"""# Setup Instructions for {config.name}

## Required GitHub Secrets

To deploy this application, you need to configure the following secrets in your GitHub repository:

### Azure Credentials
- `AZURE_CREDENTIALS`: Service principal credentials for Azure authentication
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID

### Container Registry
- `REGISTRY_LOGIN_SERVER`: {config.azure.registry}.azurecr.io
- `REGISTRY_USERNAME`: Service principal client ID
- `REGISTRY_PASSWORD`: Service principal client secret

### Azure Resources
- `AZURE_RESOURCE_GROUP`: {config.azure.resource_group}
- `AZURE_LOCATION`: {config.azure.location}

### Log Analytics (Optional)
- `LOG_ANALYTICS_WORKSPACE_ID`: {config.azure.log_analytics_workspace_id or "Not configured"}
- `LOG_ANALYTICS_WORKSPACE_KEY`: {config.azure.log_analytics_workspace_key or "Not configured"}

## Services Configuration

The following services will be deployed:

"""
        
        for service in config.services:
            setup_content += f"""
### {service.name}
- Port: {service.port}
- External: {service.external}
- CPU: {service.cpu}
- Memory: {service.memory}
- Min replicas: {service.min_replicas}
- Max replicas: {service.max_replicas}
"""
        
        setup_content += f"""
## Deployment Strategy

This project uses the **{config.strategy}** deployment strategy.

## Getting Started

1. Create the required GitHub secrets listed above
2. Push your code to trigger the deployment workflows
3. Monitor the Actions tab for deployment progress
"""
        
        setup_file = output_dir / "SETUP.md"
        setup_file.write_text(setup_content)