# tachi

A CLI tool for generating production-ready GitHub Actions workflows and Azure Container Apps configurations. Tachi automates the creation of CI/CD pipelines with support for multiple deployment strategies, dynamic PR environments, and multi-service applications.

Developed for internal use at Avidity Biosciences.

## Features

- 🚀 **Multiple Deployment Strategies**
  - `trunk-direct`: Simple deployment directly to production on merge
  - `trunk-release`: Tag-based releases without staging
  - `trunk-release-stage`: Full pipeline with staging environment

- 🔄 **Dynamic PR Environments**
  - Automatic environment creation for each pull request
  - Environment URLs posted as PR comments
  - Automatic cleanup when PRs are closed

- 📦 **Multi-Service Support**
  - Configure multiple services in a single project
  - Independent scaling and resource allocation
  - Internal and external service types

- ⚙️ **Azure Container Apps Integration**
  - Automatic container app configuration generation
  - Support for Log Analytics integration
  - CPU and memory resource configuration
  - Auto-scaling configuration

## Installation

### Using uvx (Recommended)

Run tachi directly without installation:

```bash
uvx tachi generate --config tachi.yaml
```

### Local Installation

For development or frequent use:

```bash
# Clone the repository
git clone https://github.com/aviditybio/tachi.git
cd tachi

# Install with uv
uv pip install -e .
```

## Quick Start

1. **Create a configuration file** (`tachi.yaml`):

```yaml
name: my-app
strategy: trunk-release-stage

azure:
  resource_group: rg-myapp
  registry: myappregistry
  location: eastus

services:
  - name: api
    dockerfile: Dockerfile.api
    port: 8080
    external: true
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 10

  - name: worker
    dockerfile: Dockerfile.worker
    port: 9000
    external: false
    cpu: 0.25
    memory: 0.5Gi
```

2. **Validate your configuration**:

```bash
uvx tachi validate --config tachi.yaml
```

3. **Generate workflows and configurations**:

```bash
uvx tachi generate --config tachi.yaml --output ./generated
```

4. **Review generated files**:
   - `.github/workflows/`: GitHub Actions workflows
   - `container-apps/configs/`: Azure Container Apps configurations
   - `SETUP.md`: Setup instructions with required secrets

## Configuration

### Project Configuration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Project name (used in resource naming) |
| `strategy` | string | Yes | Deployment strategy (see below) |
| `azure` | object | Yes | Azure configuration |
| `services` | array | Yes | List of services to deploy |

### Azure Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `resource_group` | string | Yes | - | Azure resource group name |
| `registry` | string | Yes | - | Azure Container Registry name |
| `location` | string | No | eastus | Azure region |
| `log_analytics_workspace_id` | string | No | - | Log Analytics workspace ID |
| `log_analytics_workspace_key` | string | No | - | Log Analytics workspace key |

### Service Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | Yes | - | Service name |
| `dockerfile` | string | No | Dockerfile | Path to Dockerfile |
| `port` | integer | No | 8000 | Container port |
| `external` | boolean | No | true | External ingress enabled |
| `cpu` | float | No | 0.25 | CPU cores (0.25 - 2) |
| `memory` | string | No | 0.5Gi | Memory allocation |
| `min_replicas` | integer | No | 1 | Minimum replicas |
| `max_replicas` | integer | No | 10 | Maximum replicas |
| `context` | string | No | . | Docker build context |

## Deployment Strategies

### trunk-direct
- **PR**: Creates dynamic environment
- **Merge to main**: Deploys to production
- **Use case**: Low-risk applications, internal tools

### trunk-release
- **PR**: Creates dynamic environment
- **Merge to main**: No automatic deployment
- **Tag (v*)**: Deploys to production
- **Use case**: Applications requiring controlled releases

### trunk-release-stage
- **PR**: Creates dynamic environment
- **Merge to main**: Deploys to staging
- **Tag (v*)**: Deploys to production
- **Use case**: Applications requiring staging validation

## Commands

### generate

Generate GitHub Actions workflows and configurations:

```bash
uvx tachi generate --config <config-file> [OPTIONS]

Options:
  -c, --config PATH    Configuration file (YAML)
  -o, --output PATH    Output directory (default: current directory)
  --dry-run           Preview files without creating them
  -f, --force         Overwrite existing files without prompting
```

### validate

Validate a configuration file:

```bash
uvx tachi validate --config <config-file> [OPTIONS]

Options:
  -c, --config PATH    Configuration file to validate
  -v, --verbose       Show detailed configuration information
```

### Interactive Mode

Run without a config file to use interactive mode:

```bash
uvx tachi generate
```

## Required GitHub Secrets

After generating workflows, configure these secrets in your GitHub repository:

### Azure Authentication
- `AZURE_CREDENTIALS`: Service principal credentials
- `AZURE_SUBSCRIPTION_ID`: Azure subscription ID

### Container Registry
- `REGISTRY_LOGIN_SERVER`: ACR login server URL
- `REGISTRY_USERNAME`: Service principal client ID
- `REGISTRY_PASSWORD`: Service principal client secret

### Azure Resources
- `AZURE_RESOURCE_GROUP`: Resource group name
- `AZURE_LOCATION`: Azure region

### Log Analytics (Optional)
- `LOG_ANALYTICS_WORKSPACE_ID`: Workspace ID
- `LOG_ANALYTICS_WORKSPACE_KEY`: Workspace key

## Examples

### Simple Web Application

```yaml
name: web-app
strategy: trunk-direct

azure:
  resource_group: rg-webapp
  registry: webappregistry
  location: eastus

services:
  - name: web
    port: 80
    external: true
```

### Microservices with Staging

```yaml
name: microservices
strategy: trunk-release-stage

azure:
  resource_group: rg-microservices
  registry: microservicesreg
  location: westus2
  log_analytics_workspace_id: ${LOG_ANALYTICS_ID}
  log_analytics_workspace_key: ${LOG_ANALYTICS_KEY}

services:
  - name: frontend
    dockerfile: frontend/Dockerfile
    port: 3000
    external: true
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 10
    context: ./frontend

  - name: api
    dockerfile: api/Dockerfile
    port: 8080
    external: true
    cpu: 1
    memory: 2Gi
    min_replicas: 3
    max_replicas: 20
    context: ./api

  - name: worker
    dockerfile: worker/Dockerfile
    port: 9000
    external: false
    cpu: 0.5
    memory: 1Gi
    context: ./worker
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/Avidity-Dev/tachi.git
cd tachi

# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=tachi

# Run specific test file
uv run pytest tests/test_config.py
```

### Project Structure

```
tachi/
├── src/tachi/
│   ├── __init__.py
│   ├── cli.py              # CLI commands and interface
│   ├── config.py           # Configuration dataclasses
│   ├── azure_generator.py  # Workflow generation logic
│   └── templates/azure/    # Jinja2 templates
├── tests/
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_generator.py
└── pyproject.toml
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is a tool for internal use at Avidity Biosciences but contains no proprietary code/IP.

The scripts and documentation in this project are released under the [MIT License](LICENSE).
