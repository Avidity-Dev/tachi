"""Configuration dataclasses for tachi"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import yaml


@dataclass
class Service:
    """Service configuration for Azure Container Apps"""
    name: str
    dockerfile: str = "Dockerfile"
    port: int = 8000
    external: bool = True
    cpu: float = 0.25
    memory: str = "0.5Gi"
    min_replicas: int = 1
    max_replicas: int = 10
    context: str = "."
    
    def validate(self) -> List[str]:
        """Validate service configuration"""
        errors = []
        
        # Validate port range
        if not (1 <= self.port <= 65535):
            errors.append(f"Service {self.name}: port must be between 1 and 65535")
        
        # Validate CPU
        if self.cpu <= 0:
            errors.append(f"Service {self.name}: cpu must be greater than 0")
        
        # Validate replica constraints
        if self.min_replicas < 0:
            errors.append(f"Service {self.name}: min_replicas cannot be negative")
        if self.max_replicas < self.min_replicas:
            errors.append(f"Service {self.name}: max_replicas must be >= min_replicas")
        
        return errors


@dataclass
class AzureConfig:
    """Azure-specific configuration"""
    resource_group: str
    registry: str
    location: str = "eastus"
    log_analytics_workspace_id: Optional[str] = None
    log_analytics_workspace_key: Optional[str] = None


@dataclass
class ProjectConfig:
    """Main project configuration"""
    name: str
    strategy: str
    azure: AzureConfig
    services: List[Service] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate project configuration"""
        errors = []
        
        # Validate strategy
        valid_strategies = ["basic", "blue-green", "canary"]
        if self.strategy not in valid_strategies:
            errors.append(f"Invalid strategy: {self.strategy}. Must be one of {valid_strategies}")
        
        # Check for duplicate service names
        service_names = [s.name for s in self.services]
        if len(service_names) != len(set(service_names)):
            errors.append("Duplicate service names found")
        
        # Validate each service
        for service in self.services:
            errors.extend(service.validate())
        
        return errors


def _parse_config(config_dict: Dict[str, Any]) -> ProjectConfig:
    """Parse YAML configuration dictionary into ProjectConfig"""
    # Parse Azure config
    azure_dict = config_dict.get("azure", {})
    azure_config = AzureConfig(
        resource_group=azure_dict.get("resource_group", ""),
        registry=azure_dict.get("registry", ""),
        location=azure_dict.get("location", "eastus"),
        log_analytics_workspace_id=azure_dict.get("log_analytics_workspace_id"),
        log_analytics_workspace_key=azure_dict.get("log_analytics_workspace_key")
    )
    
    # Parse services
    services = []
    for service_dict in config_dict.get("services", []):
        service = Service(
            name=service_dict.get("name", ""),
            dockerfile=service_dict.get("dockerfile", "Dockerfile"),
            port=service_dict.get("port", 8000),
            external=service_dict.get("external", True),
            cpu=service_dict.get("cpu", 0.25),
            memory=service_dict.get("memory", "0.5Gi"),
            min_replicas=service_dict.get("min_replicas", 1),
            max_replicas=service_dict.get("max_replicas", 10),
            context=service_dict.get("context", ".")
        )
        services.append(service)
    
    # Create project config
    return ProjectConfig(
        name=config_dict.get("name", ""),
        strategy=config_dict.get("strategy", "basic"),
        azure=azure_config,
        services=services
    )


def load_config(config_path: str) -> ProjectConfig:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    return _parse_config(config_dict)