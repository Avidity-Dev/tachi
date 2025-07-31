"""
Azure Container Apps workflow generator.

This module handles the generation of GitHub Actions workflows and Azure Container Apps
configuration files based on project specifications. It uses Jinja2 templates with custom
delimiters to avoid conflicts with GitHub Actions syntax.
"""
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

from tachi.config import ProjectConfig


class AzureGenerator:
    """
    Generator for Azure Container Apps workflows and configurations.
    
    Handles the generation of all deployment-related files including GitHub Actions
    workflows, container app configurations, and setup documentation based on the
    selected deployment strategy.
    
    Attributes
    ----------
    template_dir : Path
        Directory containing Jinja2 templates
    env : jinja2.Environment
        Jinja2 environment configured with custom delimiters
    """
    
    def __init__(self, template_dir: Path):
        """
        Initialize generator with template directory.
        
        Parameters
        ----------
        template_dir : Path
            Path to directory containing Jinja2 templates
        """
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
        """
        Generate all workflows and configurations.
        
        Creates the complete set of deployment files based on the project configuration,
        including GitHub Actions workflows, container app configs, and setup documentation.
        
        Parameters
        ----------
        config : ProjectConfig
            Project configuration specifying services and deployment strategy
        output_dir : Path
            Directory where generated files will be written
        """
        workflows_dir = output_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        container_apps_dir = output_dir / "container-apps" / "configs"
        container_apps_dir.mkdir(parents=True, exist_ok=True)
        
        workflows = self._get_workflows_for_strategy(config.strategy)
        
        for workflow_name in workflows:
            self._generate_workflow(config, workflow_name, workflows_dir)
        
        self._generate_container_configs(config, container_apps_dir)
        
        self._generate_setup_instructions(config, output_dir)
    
    def _get_workflows_for_strategy(self, strategy: str) -> List[str]:
        """
        Return workflow list based on deployment strategy.
        
        Parameters
        ----------
        strategy : str
            Deployment strategy name
        
        Returns
        -------
        List[str]
            List of workflow names to generate
        """
        if strategy == "trunk-direct":
            return ["pr-deploy", "prod-deploy", "pr-cleanup"]
        elif strategy == "trunk-release":
            return ["pr-deploy", "prod-deploy", "pr-cleanup"]
        elif strategy == "trunk-release-stage":
            return ["pr-deploy", "stage-deploy", "prod-deploy", "pr-cleanup"]
        else:
            return ["pr-deploy", "prod-deploy", "pr-cleanup"]
    
    def _generate_workflow(self, config: ProjectConfig, workflow_name: str, output_dir: Path) -> None:
        """
        Generate a single workflow file from template.
        
        Parameters
        ----------
        config : ProjectConfig
            Project configuration
        workflow_name : str
            Name of the workflow to generate (without extension)
        output_dir : Path
            Directory where the workflow file will be written
        """
        template = self.env.get_template(f"{workflow_name}.yaml.j2")
        
        context = {
            "project": config,
            "azure": config.azure,
            "services": config.services
        }
        
        workflow_content = template.render(**context)
        
        workflow_file = output_dir / f"{workflow_name}.yaml"
        workflow_file.write_text(workflow_content)
    
    def _generate_container_configs(self, config: ProjectConfig, output_dir: Path) -> None:
        """
        Generate container app configuration files from template.
        
        Creates a separate configuration file for each service defined in the project.
        
        Parameters
        ----------
        config : ProjectConfig
            Project configuration containing service definitions
        output_dir : Path
            Directory where configuration files will be written
        """
        template = self.env.get_template("container-apps/app.yaml.j2")
        
        for service in config.services:
            context = {
                "project": config,
                "azure": config.azure,
                "service": service,
                "environment": "{{ environment }}"
            }
            
            config_content = template.render(**context)
            
            config_file = output_dir / f"{service.name}.yaml"
            config_file.write_text(config_content)
    
    def _generate_setup_instructions(self, config: ProjectConfig, output_dir: Path) -> None:
        """
        Generate SETUP.md with required secrets and configuration.
        
        Creates a setup guide documenting required GitHub secrets, Azure resources,
        and deployment steps.
        
        Parameters
        ----------
        config : ProjectConfig
            Project configuration
        output_dir : Path
            Directory where SETUP.md will be written
        """
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