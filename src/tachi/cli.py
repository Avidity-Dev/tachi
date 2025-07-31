"""CLI interface for tachi"""

from pathlib import Path
from typing import Optional
import sys

import click
import yaml

from tachi.config import load_config, ProjectConfig, Service, AzureConfig
from tachi.azure_generator import AzureGenerator


@click.group()
@click.version_option()
@click.help_option("-h", "--help")
def cli():
    """tachi - GitHub Actions CI/CD generator for Azure Container Apps
    
    Generate production-ready GitHub Actions workflows and Azure Container Apps
    configurations from a simple YAML configuration file.
    
    Example usage:
        tachi generate --config myapp.yaml --output ./generated
        tachi validate --config myapp.yaml
    """
    pass


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file (YAML)")
@click.option("--output", "-o", type=click.Path(), default=".", help="Output directory for generated files")
@click.option("--dry-run", is_flag=True, help="Preview what would be generated without creating files")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files without prompting")
def generate(config: Optional[str], output: str, dry_run: bool, force: bool):
    """Generate GitHub Actions workflows and Azure Container Apps configurations.
    
    This command generates:
    - GitHub Actions workflows for dev, staging, and production deployments
    - Azure Container Apps configuration files
    - Setup documentation with required secrets
    
    Example:
        tachi generate --config myapp.yaml --output ./generated
    """
    output_dir = Path(output)

    if config:
        with click.progressbar(length=5, label='Generating files') as bar:
            # Load configuration
            bar.update(1, 'Loading configuration')
            click.echo(f"\n📄 Loading configuration from: {config}")
            try:
                project_config = load_config(config)
            except Exception as e:
                click.echo(f"\n❌ Error loading configuration: {e}", err=True)
                raise SystemExit(1)
            
            # Validate configuration
            bar.update(1, 'Validating')
            errors = project_config.validate()
            if errors:
                click.echo("\n❌ Configuration validation failed:", err=True)
                for error in errors:
                    click.echo(f"   • {error}", err=True)
                raise SystemExit(1)
            
            # Display configuration summary
            click.echo(f"\n✅ Configuration valid!")
            click.echo(f"   📦 Project: {click.style(project_config.name, bold=True)}")
            click.echo(f"   🚀 Strategy: {click.style(project_config.strategy, fg='cyan')}")
            click.echo(f"   🔧 Services: {click.style(str(len(project_config.services)), fg='green')} " + 
                      f"({', '.join(s.name for s in project_config.services)})")
            click.echo(f"   📂 Output: {click.style(str(output_dir.absolute()), fg='yellow')}")
            
            if dry_run:
                click.echo(f"\n🔍 DRY RUN MODE - No files will be created")
                bar.update(3)
                click.echo("\nWould generate:")
                click.echo("  📁 .github/workflows/")
                workflows = []
                if project_config.strategy == "trunk-direct":
                    workflows = ["pr-deploy.yaml", "prod-deploy.yaml", "pr-cleanup.yaml"]
                elif project_config.strategy == "trunk-release":
                    workflows = ["pr-deploy.yaml", "prod-deploy.yaml", "pr-cleanup.yaml"]
                elif project_config.strategy == "trunk-release-stage":
                    workflows = ["pr-deploy.yaml", "stage-deploy.yaml", "prod-deploy.yaml", "pr-cleanup.yaml"]
                
                for workflow in workflows:
                    click.echo(f"     • {workflow}")
                click.echo("  📁 container-apps/configs/")
                for service in project_config.services:
                    click.echo(f"     • {service.name}.yaml")
                click.echo("  📄 SETUP.md")
                return
            
            # Check for existing files
            bar.update(1, 'Checking output directory')
            if output_dir.exists() and any(output_dir.iterdir()) and not force:
                if not click.confirm(f"\n⚠️  Output directory is not empty. Overwrite existing files?"):
                    click.echo("Aborted.")
                    raise SystemExit(0)
            
            # Generate files
            bar.update(1, 'Generating workflows')
            template_dir = Path(__file__).parent / "templates" / "azure"
            generator = AzureGenerator(template_dir)
            
            try:
                generator.generate(project_config, output_dir)
            except Exception as e:
                click.echo(f"\n❌ Error during generation: {e}", err=True)
                raise SystemExit(1)
            
            bar.update(1, 'Complete')
        
        # Success message
        click.echo(f"\n✅ Generation complete!")
        click.echo(f"\n📁 Files created in: {click.style(str(output_dir.absolute()), fg='green', bold=True)}")
        click.echo("\n   Generated:")
        click.echo("   • GitHub Actions workflows in .github/workflows/")
        click.echo("   • Container Apps configs in container-apps/configs/")
        click.echo("   • Setup instructions in SETUP.md")
        click.echo(f"\n💡 Next steps:")
        click.echo("   1. Review the generated SETUP.md for required GitHub secrets")
        click.echo("   2. Configure the secrets in your GitHub repository")
        click.echo("   3. Push the generated files to trigger deployments")
        
    else:
        # Interactive mode
        click.echo("🚀 Welcome to tachi interactive mode!\n")
        
        # Project name
        project_name = click.prompt("Project name", type=str)
        
        # Deployment strategy
        strategy = click.prompt(
            "Deployment strategy",
            type=click.Choice(["trunk-direct", "trunk-release", "trunk-release-stage"]),
            default="trunk-release",
            show_choices=True
        )
        
        # Azure configuration
        click.echo("\n📍 Azure Configuration:")
        resource_group = click.prompt("  Resource group", type=str)
        registry = click.prompt("  Container registry name", type=str)
        location = click.prompt("  Location", default="eastus", type=str)
        
        # Services
        services = []
        click.echo("\n🔧 Service Configuration:")
        while True:
            if services and not click.confirm("\nAdd another service?"):
                break
                
            service_name = click.prompt("  Service name", type=str)
            dockerfile = click.prompt("  Dockerfile path", default="Dockerfile", type=str)
            port = click.prompt("  Port", default=8080, type=int)
            external = click.confirm("  External access?", default=True)
            cpu = click.prompt("  CPU cores", default=0.25, type=float)
            memory = click.prompt("  Memory", default="0.5Gi", type=str)
            
            service = Service(
                name=service_name,
                dockerfile=dockerfile,
                port=port,
                external=external,
                cpu=cpu,
                memory=memory
            )
            services.append(service)
        
        # Create configuration
        azure_config = AzureConfig(
            resource_group=resource_group,
            registry=registry,
            location=location
        )
        
        project_config = ProjectConfig(
            name=project_name,
            strategy=strategy,
            azure=azure_config,
            services=services
        )
        
        # Save configuration
        config_file = f"{project_name}.yaml"
        if click.confirm(f"\n💾 Save configuration to {config_file}?"):
            config_dict = {
                "name": project_name,
                "strategy": strategy,
                "azure": {
                    "resource_group": resource_group,
                    "registry": registry,
                    "location": location
                },
                "services": [
                    {
                        "name": s.name,
                        "dockerfile": s.dockerfile,
                        "port": s.port,
                        "external": s.external,
                        "cpu": s.cpu,
                        "memory": s.memory
                    } for s in services
                ]
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            
            click.echo(f"✅ Configuration saved to {config_file}")
        
        # Generate files
        if click.confirm("\n🚀 Generate files now?"):
            template_dir = Path(__file__).parent / "templates" / "azure"
            generator = AzureGenerator(template_dir)
            generator.generate(project_config, output_dir)
            
            click.echo(f"\n✅ Files generated in: {output_dir.absolute()}")
            click.echo("\n💡 Next steps:")
            click.echo("   1. Review the generated SETUP.md")
            click.echo("   2. Configure GitHub secrets")
            click.echo("   3. Push files to your repository")


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Configuration file to validate",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed configuration information",
)
def validate(config: str, verbose: bool):
    """Validate a tachi configuration file.
    
    This command checks:
    - YAML syntax validity
    - Required fields presence
    - Service configuration constraints
    - Deployment strategy validity
    
    Example:
        tachi validate --config myapp.yaml --verbose
    """
    click.echo(f"🔍 Validating configuration: {click.style(config, fg='cyan')}\n")
    
    # Load configuration
    try:
        with open(config, 'r') as f:
            raw_config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        click.echo(f"❌ Invalid YAML syntax:", err=True)
        click.echo(f"   {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error reading file: {e}", err=True)
        raise SystemExit(1)
    
    # Parse configuration
    try:
        project_config = load_config(config)
    except Exception as e:
        click.echo(f"❌ Error parsing configuration: {e}", err=True)
        raise SystemExit(1)
    
    # Validate configuration
    errors = project_config.validate()
    
    if errors:
        click.echo("❌ Configuration validation failed:\n", err=True)
        for i, error in enumerate(errors, 1):
            click.echo(f"   {i}. {error}", err=True)
        click.echo(f"\n💡 Fix the above {len(errors)} issue(s) and try again.")
        raise SystemExit(1)
    
    # Success - show summary
    click.echo("✅ Configuration is valid!\n")
    
    # Basic information
    click.echo(f"📋 {click.style('Configuration Summary', bold=True)}")
    click.echo(f"   Project:     {click.style(project_config.name, fg='green')}")
    click.echo(f"   Strategy:    {click.style(project_config.strategy, fg='cyan')}")
    click.echo(f"   Services:    {click.style(str(len(project_config.services)), fg='yellow')}")
    
    # Azure configuration
    click.echo(f"\n☁️  {click.style('Azure Configuration', bold=True)}")
    click.echo(f"   Resource Group:  {project_config.azure.resource_group}")
    click.echo(f"   Registry:        {project_config.azure.registry}")
    click.echo(f"   Location:        {project_config.azure.location}")
    if project_config.azure.log_analytics_workspace_id:
        click.echo(f"   Log Analytics:   Configured ✓")
    else:
        click.echo(f"   Log Analytics:   Not configured")
    
    # Services summary
    click.echo(f"\n🔧 {click.style('Services', bold=True)}")
    for service in project_config.services:
        click.echo(f"\n   {click.style(service.name, fg='yellow', bold=True)}")
        click.echo(f"     Port:       {service.port}")
        click.echo(f"     External:   {'Yes' if service.external else 'No'}")
        click.echo(f"     Resources:  {service.cpu} CPU, {service.memory} Memory")
        click.echo(f"     Scaling:    {service.min_replicas}-{service.max_replicas} replicas")
        if verbose:
            click.echo(f"     Dockerfile: {service.dockerfile}")
            click.echo(f"     Context:    {service.context}")
    
    # Strategy-specific information
    click.echo(f"\n📦 {click.style('Deployment Strategy', bold=True)}")
    if project_config.strategy == "trunk-direct":
        click.echo("   Trunk Direct - Merge to main deploys directly to production")
        click.echo("   • Dynamic PR environments for testing")
        click.echo("   • Direct to production on merge")
        click.echo("   • Best for low-risk or internal applications")
    elif project_config.strategy == "trunk-release":
        click.echo("   Trunk Release - Tag releases deploy to production")
        click.echo("   • Dynamic PR environments for testing")
        click.echo("   • No automatic deployment on merge to main")
        click.echo("   • Production deployments via git tags (v*)")
        click.echo("   • Good for controlled releases without staging")
    elif project_config.strategy == "trunk-release-stage":
        click.echo("   Trunk Release + Staging - Full deployment pipeline")
        click.echo("   • Dynamic PR environments for testing")
        click.echo("   • Automatic staging deployment on merge to main")
        click.echo("   • Production deployments via git tags (v*)")
        click.echo("   • Best for applications requiring staging validation")
    
    # Verbose mode - show raw config
    if verbose:
        click.echo(f"\n📄 {click.style('Raw Configuration', bold=True)}")
        click.echo(yaml.dump(raw_config, default_flow_style=False, sort_keys=False))
    
    # Files that will be generated
    click.echo(f"\n📁 {click.style('Files to be generated', bold=True)}")
    click.echo("   Workflows:")
    workflows = []
    if project_config.strategy == "trunk-direct":
        workflows = ["pr-deploy.yaml", "prod-deploy.yaml", "pr-cleanup.yaml"]
    elif project_config.strategy == "trunk-release":
        workflows = ["pr-deploy.yaml", "prod-deploy.yaml", "pr-cleanup.yaml"]
    elif project_config.strategy == "trunk-release-stage":
        workflows = ["pr-deploy.yaml", "stage-deploy.yaml", "prod-deploy.yaml", "pr-cleanup.yaml"]
    
    for wf in workflows:
        click.echo(f"     • .github/workflows/{wf}")
    
    click.echo("   Container Apps:")
    for service in project_config.services:
        click.echo(f"     • container-apps/configs/{service.name}.yaml")
    
    click.echo("   Documentation:")
    click.echo(f"     • SETUP.md")
    
    click.echo(f"\n💡 Run {click.style('tachi generate --config ' + config, fg='green')} to generate files")


if __name__ == "__main__":
    cli()
