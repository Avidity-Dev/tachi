"""Tests for configuration dataclasses and validation"""
import pytest
from tachi.config import Service, AzureConfig, ProjectConfig, load_config, _parse_config
import tempfile
import yaml
from pathlib import Path


class TestService:
    """Test Service dataclass validation"""
    
    def test_valid_service(self):
        """Test creating a valid service"""
        service = Service(
            name="api",
            dockerfile="Dockerfile",
            port=8080,
            external=True,
            cpu=0.5,
            memory="1Gi"
        )
        errors = service.validate()
        assert errors == []
    
    def test_invalid_port_range(self):
        """Test service with invalid port"""
        service = Service(name="api", port=70000)
        errors = service.validate()
        assert len(errors) == 1
        assert "port must be between 1 and 65535" in errors[0]
        
        service = Service(name="api", port=0)
        errors = service.validate()
        assert len(errors) == 1
        assert "port must be between 1 and 65535" in errors[0]
    
    def test_invalid_cpu(self):
        """Test service with invalid CPU"""
        service = Service(name="api", cpu=-1)
        errors = service.validate()
        assert len(errors) == 1
        assert "cpu must be greater than 0" in errors[0]
        
        service = Service(name="api", cpu=0)
        errors = service.validate()
        assert len(errors) == 1
        assert "cpu must be greater than 0" in errors[0]
    
    def test_invalid_replicas(self):
        """Test service with invalid replica configuration"""
        # Negative min replicas
        service = Service(name="api", min_replicas=-1)
        errors = service.validate()
        assert len(errors) == 1
        assert "min_replicas cannot be negative" in errors[0]
        
        # Max replicas less than min
        service = Service(name="api", min_replicas=5, max_replicas=3)
        errors = service.validate()
        assert len(errors) == 1
        assert "max_replicas must be >= min_replicas" in errors[0]
    
    def test_multiple_errors(self):
        """Test service with multiple validation errors"""
        service = Service(
            name="api",
            port=100000,
            cpu=-1,
            min_replicas=10,
            max_replicas=5
        )
        errors = service.validate()
        assert len(errors) == 3


class TestProjectConfig:
    """Test ProjectConfig validation"""
    
    def test_valid_project_config(self):
        """Test creating a valid project configuration"""
        azure = AzureConfig(
            resource_group="rg-test",
            registry="testregistry",
            location="eastus"
        )
        service = Service(name="api")
        config = ProjectConfig(
            name="test-app",
            strategy="trunk-direct",
            azure=azure,
            services=[service]
        )
        errors = config.validate()
        assert errors == []
    
    def test_invalid_strategy(self):
        """Test project with invalid strategy"""
        azure = AzureConfig(resource_group="rg", registry="reg")
        config = ProjectConfig(
            name="test",
            strategy="invalid-strategy",
            azure=azure,
            services=[]
        )
        errors = config.validate()
        assert len(errors) == 1
        assert "Invalid strategy" in errors[0]
        assert "trunk-direct" in errors[0]
        assert "trunk-release" in errors[0]
        assert "trunk-release-stage" in errors[0]
    
    def test_duplicate_service_names(self):
        """Test project with duplicate service names"""
        azure = AzureConfig(resource_group="rg", registry="reg")
        service1 = Service(name="api")
        service2 = Service(name="api")
        config = ProjectConfig(
            name="test",
            strategy="trunk-direct",
            azure=azure,
            services=[service1, service2]
        )
        errors = config.validate()
        assert any("Duplicate service names" in error for error in errors)
    
    def test_service_validation_propagation(self):
        """Test that service validation errors propagate to project"""
        azure = AzureConfig(resource_group="rg", registry="reg")
        service = Service(name="api", port=70000, cpu=-1)
        config = ProjectConfig(
            name="test",
            strategy="trunk-direct",
            azure=azure,
            services=[service]
        )
        errors = config.validate()
        assert len(errors) >= 2
        assert any("port must be between" in error for error in errors)
        assert any("cpu must be greater than" in error for error in errors)


class TestConfigParsing:
    """Test YAML configuration parsing"""
    
    def test_parse_minimal_config(self):
        """Test parsing minimal configuration"""
        config_dict = {
            "name": "test-app",
            "strategy": "trunk-direct",
            "azure": {
                "resource_group": "rg-test",
                "registry": "testregistry"
            },
            "services": [
                {"name": "api"}
            ]
        }
        
        config = _parse_config(config_dict)
        assert config.name == "test-app"
        assert config.strategy == "trunk-direct"
        assert config.azure.resource_group == "rg-test"
        assert config.azure.registry == "testregistry"
        assert config.azure.location == "eastus"  # default
        assert len(config.services) == 1
        assert config.services[0].name == "api"
        assert config.services[0].port == 8000  # default
    
    def test_parse_full_config(self):
        """Test parsing full configuration with all fields"""
        config_dict = {
            "name": "test-app",
            "strategy": "trunk-release-stage",
            "azure": {
                "resource_group": "rg-test",
                "registry": "testregistry",
                "location": "westus2",
                "log_analytics_workspace_id": "workspace-123",
                "log_analytics_workspace_key": "key-123"
            },
            "services": [
                {
                    "name": "api",
                    "dockerfile": "Dockerfile.api",
                    "port": 3000,
                    "external": False,
                    "cpu": 1.5,
                    "memory": "2Gi",
                    "min_replicas": 3,
                    "max_replicas": 20,
                    "context": "./api"
                }
            ]
        }
        
        config = _parse_config(config_dict)
        assert config.azure.location == "westus2"
        assert config.azure.log_analytics_workspace_id == "workspace-123"
        assert config.azure.log_analytics_workspace_key == "key-123"
        
        service = config.services[0]
        assert service.dockerfile == "Dockerfile.api"
        assert service.port == 3000
        assert service.external is False
        assert service.cpu == 1.5
        assert service.memory == "2Gi"
        assert service.min_replicas == 3
        assert service.max_replicas == 20
        assert service.context == "./api"
    
    def test_load_config_from_file(self):
        """Test loading configuration from YAML file"""
        config_dict = {
            "name": "test-app",
            "strategy": "trunk-release",
            "azure": {
                "resource_group": "rg-test",
                "registry": "testregistry"
            },
            "services": [
                {"name": "web", "port": 80},
                {"name": "api", "port": 8080}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            temp_path = f.name
        
        try:
            config = load_config(temp_path)
            assert config.name == "test-app"
            assert config.strategy == "trunk-release"
            assert len(config.services) == 2
            assert config.services[0].name == "web"
            assert config.services[0].port == 80
            assert config.services[1].name == "api"
            assert config.services[1].port == 8080
        finally:
            Path(temp_path).unlink()


class TestValidStrategies:
    """Test all valid deployment strategies"""
    
    @pytest.mark.parametrize("strategy", ["trunk-direct", "trunk-release", "trunk-release-stage"])
    def test_valid_strategies(self, strategy):
        """Test that all documented strategies are valid"""
        azure = AzureConfig(resource_group="rg", registry="reg")
        config = ProjectConfig(
            name="test",
            strategy=strategy,
            azure=azure,
            services=[]
        )
        errors = config.validate()
        assert errors == []