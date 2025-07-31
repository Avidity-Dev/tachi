"""CLI interface for tachi"""

from pathlib import Path
from typing import Optional

import click


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
        click.echo(f"Output directory: {output_dir.absolute()}")
        # TODO: Implement configuration loading and generation
        click.echo("Generation complete! (placeholder)")
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
    # TODO: Implement validation
    click.echo("Validation complete! (placeholder)")


if __name__ == "__main__":
    cli()
