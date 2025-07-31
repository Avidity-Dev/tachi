"""
Configuration dataclasses for tachi.

This module defines the data structures used to represent tachi project configurations,
including services, Azure settings, and deployment strategies. All configurations are
validated to ensure they meet the requirements for successful deployment.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import yaml


@dataclass
class Service:
    """
    Service configuration for Azure Container Apps.
    
    Represents a single service/container that will be deployed to Azure Container Apps.
    Each service can have its own resource allocation, scaling rules, and network settings.
    
    Attributes
    ----------
    name : str
        Unique name for the service
    dockerfile : str, default="Dockerfile"
        Path to the Dockerfile relative to the service context
    port : int, default=8000
        Port the service listens on
    external : bool, default=True
        Whether the service should be accessible from the internet
    cpu : float, default=0.25
        CPU cores allocated to each instance (e.g., 0.25, 0.5, 1.0)
    memory : str, default="0.5Gi"
        Memory allocated to each instance (e.g., "0.5Gi", "1Gi", "2Gi")
    min_replicas : int, default=1
        Minimum number of instances to run
    max_replicas : int, default=10
        Maximum number of instances for autoscaling
    context : str, default="."
        Build context path relative to the repository root
    """
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
        """
        Validate service configuration.
        
        Checks that all service parameters meet the requirements for Azure Container Apps
        deployment, including port ranges, resource allocations, and scaling constraints.
        
        Returns
        -------
        List[str]
            List of validation error messages. Empty list if configuration is valid.
        """
        errors = []
        
        if not (1 <= self.port <= 65535):
            errors.append(f"Service {self.name}: port must be between 1 and 65535")
        
        if self.cpu <= 0:
            errors.append(f"Service {self.name}: cpu must be greater than 0")
        
        if self.min_replicas < 0:
            errors.append(f"Service {self.name}: min_replicas cannot be negative")
        if self.max_replicas < self.min_replicas:
            errors.append(f"Service {self.name}: max_replicas must be >= min_replicas")
        
        return errors


@dataclass
class AzureConfig:
    """
    Azure-specific configuration.
    
    Contains all Azure resource settings required for deploying container apps,
    including resource group, container registry, and optional monitoring configuration.
    
    Attributes
    ----------
    resource_group : str
        Azure resource group name where resources will be created
    registry : str
        Azure Container Registry name (without .azurecr.io suffix)
    location : str, default="eastus"
        Azure region for resource deployment
    log_analytics_workspace_id : Optional[str], default=None
        Log Analytics workspace ID for container app monitoring
    log_analytics_workspace_key : Optional[str], default=None
        Log Analytics workspace key for authentication
    """
    resource_group: str
    registry: str
    location: str = "eastus"
    log_analytics_workspace_id: Optional[str] = None
    log_analytics_workspace_key: Optional[str] = None


@dataclass
class ProjectConfig:
    """
    Main project configuration.
    
    Top-level configuration that combines all settings needed to generate GitHub Actions
    workflows and Azure Container Apps configurations for a project.
    
    Attributes
    ----------
    name : str
        Project name used for naming Azure resources
    strategy : str
        Deployment strategy: "trunk-direct", "trunk-release", or "trunk-release-stage"
    azure : AzureConfig
        Azure-specific configuration settings
    services : List[Service]
        List of services to deploy
    """
    name: str
    strategy: str
    azure: AzureConfig
    services: List[Service] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """
        Validate project configuration.
        
        Validates the project configuration including strategy, service name 
        uniqueness, and individual service settings.
        
        Returns
        -------
        List[str]
            List of validation error messages. Empty list if configuration is valid.
        """
        errors = []
        
        valid_strategies = ["trunk-direct", "trunk-release", "trunk-release-stage"]
        if self.strategy not in valid_strategies:
            errors.append(f"Invalid strategy: {self.strategy}. Must be one of {valid_strategies}")
        
        service_names = [s.name for s in self.services]
        if len(service_names) != len(set(service_names)):
            errors.append("Duplicate service names found")
        
        for service in self.services:
            errors.extend(service.validate())
        
        return errors


def _parse_config(config_dict: Dict[str, Any]) -> ProjectConfig:
    """
    Parse YAML configuration dictionary into ProjectConfig.
    
    Converts a dictionary loaded from YAML into typed configuration objects,
    applying defaults where values are not specified.
    
    Parameters
    ----------
    config_dict : Dict[str, Any]
        Dictionary containing configuration data, typically loaded from YAML
    
    Returns
    -------
    ProjectConfig
        Parsed and typed project configuration
    """
    azure_dict = config_dict.get("azure", {})
    azure_config = AzureConfig(
        resource_group=azure_dict.get("resource_group", ""),
        registry=azure_dict.get("registry", ""),
        location=azure_dict.get("location", "eastus"),
        log_analytics_workspace_id=azure_dict.get("log_analytics_workspace_id"),
        log_analytics_workspace_key=azure_dict.get("log_analytics_workspace_key")
    )
    
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
    
    return ProjectConfig(
        name=config_dict.get("name", ""),
        strategy=config_dict.get("strategy", "basic"),
        azure=azure_config,
        services=services
    )


def load_config(config_path: str) -> ProjectConfig:
    """
    Load configuration from YAML file.
    
    Reads a YAML configuration file and parses it into a validated ProjectConfig object.
    
    Parameters
    ----------
    config_path : str
        Path to the YAML configuration file
    
    Returns
    -------
    ProjectConfig
        Parsed and typed project configuration
    
    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist
    yaml.YAMLError
        If the YAML file is malformed
    """
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    return _parse_config(config_dict)