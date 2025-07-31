"""CLI interface for tachi"""

from pathlib import Path
from typing import Optional

import click

from .config import load_config


@click.group()
@click.version_option()
def cli():
    """tachi - GitHub Actions CI/CD generator"""
    pass


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
@click.option("--output", "-o", type=click.Path(), default=".", help="Output directory")
def generate(config: Optional[str], output: str):
    """Generate GitHub Actions workflows and configurations"""
    output_dir = Path(output)

    if config:
        click.echo(f"Loading configuration from: {config}")
        try:
            project_config = load_config(config)
            errors = project_config.validate()
            
            if errors:
                click.echo("Configuration validation failed:", err=True)
                for error in errors:
                    click.echo(f"  - {error}", err=True)
                raise SystemExit(1)
            
            click.echo(f"Project: {project_config.name}")
            click.echo(f"Strategy: {project_config.strategy}")
            click.echo(f"Services: {len(project_config.services)}")
            click.echo(f"Output directory: {output_dir.absolute()}")
            # TODO: Implement actual generation
            click.echo("Generation complete! (placeholder)")
        except Exception as e:
            click.echo(f"Error loading configuration: {e}", err=True)
            raise SystemExit(1)
    else:
        click.echo("Interactive mode not yet implemented")
        click.echo("Please provide a configuration file with --config")


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Configuration file",
)
def validate(config: str):
    """Validate configuration file"""
    click.echo(f"Validating configuration: {config}")
    try:
        project_config = load_config(config)
        errors = project_config.validate()
        
        if errors:
            click.echo("Configuration validation failed:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            raise SystemExit(1)
        
        click.echo("✓ Configuration is valid")
        click.echo(f"  Project: {project_config.name}")
        click.echo(f"  Strategy: {project_config.strategy}")
        click.echo(f"  Azure Resource Group: {project_config.azure.resource_group}")
        click.echo(f"  Services: {', '.join(s.name for s in project_config.services)}")
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
