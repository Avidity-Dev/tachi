"""Tests for Azure generator functionality"""
import pytest
from pathlib import Path
import tempfile
import shutil
from tachi.azure_generator import AzureGenerator
from tachi.config import ProjectConfig, AzureConfig, Service


class TestAzureGenerator:
    """Test AzureGenerator class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def sample_config(self):
        """Create a sample project configuration"""
        azure = AzureConfig(
            resource_group="rg-test",
            registry="testregistry",
            location="eastus"
        )
        service = Service(
            name="api",
            port=8080,
            external=True
        )
        return ProjectConfig(
            name="test-app",
            strategy="trunk-direct",
            azure=azure,
            services=[service]
        )
    
    @pytest.fixture
    def template_dir(self):
        """Get the template directory"""
        return Path(__file__).parent.parent / "src" / "tachi" / "templates" / "azure"
    
    def test_generator_initialization(self, template_dir):
        """Test generator initializes correctly"""
        generator = AzureGenerator(template_dir)
        assert generator.template_dir == template_dir
        assert generator.env is not None
    
    def test_get_workflows_for_strategy(self, template_dir):
        """Test workflow selection based on strategy"""
        generator = AzureGenerator(template_dir)
        
        # Test trunk-direct
        workflows = generator._get_workflows_for_strategy("trunk-direct")
        assert set(workflows) == {"pr-deploy", "prod-deploy", "pr-cleanup"}
        
        # Test trunk-release
        workflows = generator._get_workflows_for_strategy("trunk-release")
        assert set(workflows) == {"pr-deploy", "prod-deploy", "pr-cleanup"}
        
        # Test trunk-release-stage
        workflows = generator._get_workflows_for_strategy("trunk-release-stage")
        assert set(workflows) == {"pr-deploy", "stage-deploy", "prod-deploy", "pr-cleanup"}
        
        # Test unknown strategy (should default)
        workflows = generator._get_workflows_for_strategy("unknown")
        assert set(workflows) == {"pr-deploy", "prod-deploy", "pr-cleanup"}
    
    def test_directory_creation(self, temp_dir, sample_config, template_dir):
        """Test that generator creates correct directory structure"""
        generator = AzureGenerator(template_dir)
        generator.generate(sample_config, temp_dir)
        
        # Check workflows directory
        workflows_dir = temp_dir / ".github" / "workflows"
        assert workflows_dir.exists()
        assert workflows_dir.is_dir()
        
        # Check container apps directory
        container_apps_dir = temp_dir / "container-apps" / "configs"
        assert container_apps_dir.exists()
        assert container_apps_dir.is_dir()
        
        # Check SETUP.md
        setup_file = temp_dir / "SETUP.md"
        assert setup_file.exists()
        assert setup_file.is_file()
    
    def test_workflow_generation_trunk_direct(self, temp_dir, sample_config, template_dir):
        """Test workflow generation for trunk-direct strategy"""
        generator = AzureGenerator(template_dir)
        generator.generate(sample_config, temp_dir)
        
        workflows_dir = temp_dir / ".github" / "workflows"
        
        # Check expected workflow files
        assert (workflows_dir / "pr-deploy.yaml").exists()
        assert (workflows_dir / "prod-deploy.yaml").exists()
        assert (workflows_dir / "pr-cleanup.yaml").exists()
        
        # Should not have stage-deploy
        assert not (workflows_dir / "stage-deploy.yaml").exists()
    
    def test_workflow_generation_trunk_release_stage(self, temp_dir, template_dir):
        """Test workflow generation for trunk-release-stage strategy"""
        azure = AzureConfig(resource_group="rg", registry="reg")
        service = Service(name="api")
        config = ProjectConfig(
            name="test",
            strategy="trunk-release-stage",
            azure=azure,
            services=[service]
        )
        
        generator = AzureGenerator(template_dir)
        generator.generate(config, temp_dir)
        
        workflows_dir = temp_dir / ".github" / "workflows"
        
        # Check all expected workflow files
        assert (workflows_dir / "pr-deploy.yaml").exists()
        assert (workflows_dir / "stage-deploy.yaml").exists()
        assert (workflows_dir / "prod-deploy.yaml").exists()
        assert (workflows_dir / "pr-cleanup.yaml").exists()
    
    def test_container_config_generation(self, temp_dir, template_dir):
        """Test container app configuration generation"""
        azure = AzureConfig(resource_group="rg", registry="reg")
        services = [
            Service(name="web", port=80),
            Service(name="api", port=8080),
            Service(name="worker", port=9000, external=False)
        ]
        config = ProjectConfig(
            name="multi-service",
            strategy="trunk-direct",
            azure=azure,
            services=services
        )
        
        generator = AzureGenerator(template_dir)
        generator.generate(config, temp_dir)
        
        configs_dir = temp_dir / "container-apps" / "configs"
        
        # Check config files for each service
        assert (configs_dir / "web.yaml").exists()
        assert (configs_dir / "api.yaml").exists()
        assert (configs_dir / "worker.yaml").exists()
        
        # Verify content includes service-specific info
        web_config = (configs_dir / "web.yaml").read_text()
        assert "multi-service-web" in web_config
        assert "80" in web_config
        assert "external: true" in web_config
        
        worker_config = (configs_dir / "worker.yaml").read_text()
        assert "multi-service-worker" in worker_config
        assert "9000" in worker_config
        assert "external: false" in worker_config
    
    def test_setup_instructions_generation(self, temp_dir, template_dir):
        """Test SETUP.md generation"""
        azure = AzureConfig(
            resource_group="rg-prod",
            registry="prodregistry",
            location="westus2",
            log_analytics_workspace_id="workspace-123"
        )
        service = Service(
            name="api",
            port=8080,
            cpu=0.5,
            memory="1Gi",
            min_replicas=2,
            max_replicas=10
        )
        config = ProjectConfig(
            name="production-app",
            strategy="trunk-release-stage",
            azure=azure,
            services=[service]
        )
        
        generator = AzureGenerator(template_dir)
        generator.generate(config, temp_dir)
        
        setup_file = temp_dir / "SETUP.md"
        content = setup_file.read_text()
        
        # Check for required sections
        assert "# Setup Instructions for production-app" in content
        assert "## Required GitHub Secrets" in content
        assert "AZURE_CREDENTIALS" in content
        assert "`REGISTRY_LOGIN_SERVER`: prodregistry.azurecr.io" in content
        assert "`AZURE_RESOURCE_GROUP`: rg-prod" in content
        assert "`AZURE_LOCATION`: westus2" in content
        assert "`LOG_ANALYTICS_WORKSPACE_ID`: workspace-123" in content
        
        # Check service configuration
        assert "## Services Configuration" in content
        assert "### api" in content
        assert "Port: 8080" in content
        assert "CPU: 0.5" in content
        assert "Memory: 1Gi" in content
        assert "Min replicas: 2" in content
        assert "Max replicas: 10" in content
        
        # Check deployment strategy
        assert "## Deployment Strategy" in content
        assert "trunk-release-stage" in content
    
    def test_workflow_content_validation(self, temp_dir, sample_config, template_dir):
        """Test that generated workflows contain expected content"""
        generator = AzureGenerator(template_dir)
        generator.generate(sample_config, temp_dir)
        
        # Check prod-deploy.yaml for trunk-direct
        prod_workflow = (temp_dir / ".github" / "workflows" / "prod-deploy.yaml").read_text()
        assert "name: Deploy to Production" in prod_workflow
        assert "branches:" in prod_workflow
        assert "- main" in prod_workflow
        assert "test-app" in prod_workflow  # project name
        assert "api" in prod_workflow  # service name
        
        # Check pr-deploy.yaml
        pr_workflow = (temp_dir / ".github" / "workflows" / "pr-deploy.yaml").read_text()
        assert "name: Deploy PR Environment" in pr_workflow
        assert "pull_request:" in pr_workflow
        assert "pr-${PR_NUM}" in pr_workflow


class TestTemplateRendering:
    """Test Jinja2 template rendering"""
    
    @pytest.fixture
    def generator(self):
        """Create generator with test templates"""
        template_dir = Path(__file__).parent.parent / "src" / "tachi" / "templates" / "azure"
        return AzureGenerator(template_dir)
    
    def test_custom_jinja_delimiters(self, generator):
        """Test that custom Jinja2 delimiters work correctly"""
        # Verify environment uses custom delimiters
        assert generator.env.variable_start_string == '[['
        assert generator.env.variable_end_string == ']]'
        assert generator.env.block_start_string == '[%'
        assert generator.env.block_end_string == '%]'