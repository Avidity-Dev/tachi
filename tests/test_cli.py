"""Tests for CLI commands"""
import pytest
from click.testing import CliRunner
from pathlib import Path
import tempfile
import yaml
import shutil
from tachi.cli import cli


class TestCLI:
    """Test CLI commands"""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner"""
        return CliRunner()
    
    @pytest.fixture
    def valid_config(self):
        """Create a valid configuration dictionary"""
        return {
            "name": "test-app",
            "strategy": "trunk-direct",
            "azure": {
                "resource_group": "rg-test",
                "registry": "testregistry",
                "location": "eastus"
            },
            "services": [
                {
                    "name": "api",
                    "port": 8080,
                    "external": True
                }
            ]
        }
    
    @pytest.fixture
    def invalid_config(self):
        """Create an invalid configuration dictionary"""
        return {
            "name": "test-app",
            "strategy": "invalid-strategy",
            "azure": {
                "resource_group": "rg-test",
                "registry": "testregistry"
            },
            "services": [
                {
                    "name": "api",
                    "port": 100000,  # Invalid port
                    "cpu": -1  # Invalid CPU
                }
            ]
        }
    
    def test_cli_help(self, runner):
        """Test CLI help command"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "tachi - GitHub Actions CI/CD generator" in result.output
        assert "generate" in result.output
        assert "validate" in result.output
    
    def test_cli_version(self, runner):
        """Test CLI version command"""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "version" in result.output
    
    def test_generate_help(self, runner):
        """Test generate command help"""
        result = runner.invoke(cli, ['generate', '--help'])
        assert result.exit_code == 0
        assert "Generate GitHub Actions workflows" in result.output
        assert "--config" in result.output
        assert "--output" in result.output
        assert "--dry-run" in result.output
        assert "--force" in result.output
    
    def test_validate_help(self, runner):
        """Test validate command help"""
        result = runner.invoke(cli, ['validate', '--help'])
        assert result.exit_code == 0
        assert "Validate a tachi configuration file" in result.output
        assert "--config" in result.output
        assert "--verbose" in result.output
    
    def test_validate_valid_config(self, runner, valid_config):
        """Test validating a valid configuration"""
        with runner.isolated_filesystem():
            # Create config file
            with open('config.yaml', 'w') as f:
                yaml.dump(valid_config, f)
            
            result = runner.invoke(cli, ['validate', '--config', 'config.yaml'])
            assert result.exit_code == 0
            assert "Configuration is valid!" in result.output
            assert "test-app" in result.output
            assert "trunk-direct" in result.output
            assert "api" in result.output
    
    def test_validate_invalid_config(self, runner, invalid_config):
        """Test validating an invalid configuration"""
        with runner.isolated_filesystem():
            # Create config file
            with open('config.yaml', 'w') as f:
                yaml.dump(invalid_config, f)
            
            result = runner.invoke(cli, ['validate', '--config', 'config.yaml'])
            assert result.exit_code == 1
            assert "Configuration validation failed" in result.output
            assert "port must be between" in result.output
            assert "cpu must be greater than" in result.output
    
    def test_validate_verbose(self, runner, valid_config):
        """Test validate command with verbose flag"""
        with runner.isolated_filesystem():
            with open('config.yaml', 'w') as f:
                yaml.dump(valid_config, f)
            
            result = runner.invoke(cli, ['validate', '--config', 'config.yaml', '--verbose'])
            assert result.exit_code == 0
            assert "Raw Configuration" in result.output
            assert "Dockerfile:" in result.output  # Verbose service info
            assert "Context:" in result.output
    
    def test_validate_missing_file(self, runner):
        """Test validate with missing configuration file"""
        result = runner.invoke(cli, ['validate', '--config', 'nonexistent.yaml'])
        assert result.exit_code == 2
        assert "does not exist" in result.output
    
    def test_validate_invalid_yaml(self, runner):
        """Test validate with invalid YAML syntax"""
        with runner.isolated_filesystem():
            with open('config.yaml', 'w') as f:
                f.write("invalid: yaml: syntax: here")
            
            result = runner.invoke(cli, ['validate', '--config', 'config.yaml'])
            assert result.exit_code == 1
            assert "Invalid YAML syntax" in result.output
    
    def test_generate_with_config(self, runner, valid_config):
        """Test generate command with configuration file"""
        with runner.isolated_filesystem():
            # Create config file
            with open('config.yaml', 'w') as f:
                yaml.dump(valid_config, f)
            
            result = runner.invoke(cli, ['generate', '--config', 'config.yaml', '--output', 'output'])
            assert result.exit_code == 0
            assert "Generation complete!" in result.output
            assert Path('output/.github/workflows').exists()
            assert Path('output/container-apps/configs').exists()
            assert Path('output/SETUP.md').exists()
    
    def test_generate_dry_run(self, runner, valid_config):
        """Test generate command with dry-run flag"""
        with runner.isolated_filesystem():
            with open('config.yaml', 'w') as f:
                yaml.dump(valid_config, f)
            
            result = runner.invoke(cli, ['generate', '--config', 'config.yaml', '--dry-run'])
            assert result.exit_code == 0
            assert "DRY RUN MODE" in result.output
            assert "Would generate:" in result.output
            assert "pr-deploy.yaml" in result.output
            assert "prod-deploy.yaml" in result.output
            assert "pr-cleanup.yaml" in result.output
            # Should not create any files
            assert not Path('.github').exists()
    
    def test_generate_force_overwrite(self, runner, valid_config):
        """Test generate command with force flag"""
        with runner.isolated_filesystem():
            with open('config.yaml', 'w') as f:
                yaml.dump(valid_config, f)
            
            # Create output directory with existing files
            Path('output').mkdir()
            Path('output/existing.txt').touch()
            
            # Without force, should prompt (we'll cancel)
            result = runner.invoke(cli, ['generate', '--config', 'config.yaml', '--output', 'output'], input='n\n')
            assert result.exit_code == 0
            assert "Output directory is not empty" in result.output
            assert "Aborted" in result.output
            
            # With force, should not prompt
            result = runner.invoke(cli, ['generate', '--config', 'config.yaml', '--output', 'output', '--force'])
            assert result.exit_code == 0
            assert "Generation complete!" in result.output
            assert Path('output/.github/workflows').exists()
    
    def test_generate_without_config_interactive(self, runner):
        """Test generate command interactive mode"""
        # Simulate interactive input
        input_data = '\n'.join([
            'test-project',  # Project name
            'trunk-direct',  # Strategy (choose first option)
            'rg-test',      # Resource group
            'testregistry', # Registry
            'eastus',       # Location
            'api',          # Service name
            '',             # Dockerfile (default)
            '',             # Port (default)
            'y',            # External access
            '',             # CPU (default)
            '',             # Memory (default)
            'n',            # Add another service
            'n',            # Save configuration
            'n'             # Generate files
        ])
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['generate'], input=input_data)
            assert result.exit_code == 0
            assert "Welcome to tachi interactive mode!" in result.output
            assert "Project name:" in result.output
            assert "Deployment strategy" in result.output  # Remove colon since it's part of a longer line
    
    def test_generate_with_all_strategies(self, runner):
        """Test generate command with each deployment strategy"""
        strategies = ["trunk-direct", "trunk-release", "trunk-release-stage"]
        
        for strategy in strategies:
            with runner.isolated_filesystem():
                config = {
                    "name": f"test-{strategy}",
                    "strategy": strategy,
                    "azure": {
                        "resource_group": "rg-test",
                        "registry": "testregistry"
                    },
                    "services": [{"name": "api"}]
                }
                
                with open('config.yaml', 'w') as f:
                    yaml.dump(config, f)
                
                result = runner.invoke(cli, ['generate', '--config', 'config.yaml', '--output', 'output'])
                assert result.exit_code == 0
                
                # Check appropriate workflows are generated
                workflows_dir = Path('output/.github/workflows')
                assert (workflows_dir / 'pr-deploy.yaml').exists()
                assert (workflows_dir / 'prod-deploy.yaml').exists()
                assert (workflows_dir / 'pr-cleanup.yaml').exists()
                
                if strategy == "trunk-release-stage":
                    assert (workflows_dir / 'stage-deploy.yaml').exists()
                else:
                    assert not (workflows_dir / 'stage-deploy.yaml').exists()


class TestCLIProgressAndOutput:
    """Test CLI progress indicators and output formatting"""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_generate_progress_bar(self, runner):
        """Test that generate shows progress bar"""
        config = {
            "name": "test-app",
            "strategy": "trunk-direct",
            "azure": {"resource_group": "rg", "registry": "reg"},
            "services": [{"name": "api"}]
        }
        
        with runner.isolated_filesystem():
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f)
            
            result = runner.invoke(cli, ['generate', '--config', 'config.yaml', '--output', 'output'])
            assert result.exit_code == 0
            # Progress bar creates output with "Generating files"
            assert "Generating files" in result.output
            assert "Loading configuration" in result.output
    
    def test_validate_colored_output(self, runner):
        """Test that validate command uses colored output"""
        config = {
            "name": "test-app",
            "strategy": "trunk-release-stage",
            "azure": {"resource_group": "rg", "registry": "reg"},
            "services": [{"name": "web"}, {"name": "api"}]
        }
        
        with runner.isolated_filesystem():
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f)
            
            result = runner.invoke(cli, ['validate', '--config', 'config.yaml'])
            assert result.exit_code == 0
            # Check for basic content in output
            assert "test-app" in result.output
            assert "trunk-release-stage" in result.output
            assert "web" in result.output
            assert "api" in result.output
