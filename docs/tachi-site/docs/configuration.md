---
sidebar_position: 3
---

# Configuration Reference

Complete reference for tachi configuration files.

## Configuration File Structure

tachi uses YAML configuration files with the following structure:

```yaml
name: string              # Project name (required)
strategy: string          # Deployment strategy (required)
azure:                    # Azure configuration (required)
  resource_group: string
  registry: string
  location: string
  log_analytics_workspace_id: string
  log_analytics_workspace_key: string
services:                 # List of services (required)
  - name: string
    dockerfile: string
    port: number
    external: boolean
    cpu: number
    memory: string
    min_replicas: number
    max_replicas: number
    context: string
```

## Project Configuration

### `name` (required)
- **Type**: `string`
- **Description**: Project name used in resource naming
- **Example**: `my-app`
- **Constraints**: Alphanumeric with hyphens, lowercase

### `strategy` (required)
- **Type**: `string`
- **Description**: Deployment strategy
- **Valid values**:
  - `trunk-direct`: Deploy to production on merge to main
  - `trunk-release`: Deploy to production on tag creation
  - `trunk-release-stage`: Deploy to staging on merge, production on tag
- **Example**: `trunk-release-stage`

## Azure Configuration

Configuration for Azure resources under the `azure` key:

### `resource_group` (required)
- **Type**: `string`
- **Description**: Azure resource group name
- **Example**: `rg-myapp-prod`

### `registry` (required)
- **Type**: `string`
- **Description**: Azure Container Registry name (without .azurecr.io)
- **Example**: `myappregistry`

### `location`
- **Type**: `string`
- **Default**: `eastus`
- **Description**: Azure region for resources
- **Example**: `westus2`

### `log_analytics_workspace_id`
- **Type**: `string`
- **Description**: Log Analytics workspace ID for monitoring
- **Example**: `12345678-1234-1234-1234-123456789012`
- **Note**: Can use environment variable syntax: `${LOG_ANALYTICS_ID}`

### `log_analytics_workspace_key`
- **Type**: `string`
- **Description**: Log Analytics workspace key
- **Example**: `${LOG_ANALYTICS_KEY}`
- **Note**: Recommended to use environment variable

## Service Configuration

Each service in the `services` array supports:

### `name` (required)
- **Type**: `string`
- **Description**: Service identifier
- **Example**: `api`
- **Constraints**: Alphanumeric with hyphens, lowercase

### `dockerfile`
- **Type**: `string`
- **Default**: `Dockerfile`
- **Description**: Path to Dockerfile relative to context
- **Example**: `docker/Dockerfile.api`

### `port`
- **Type**: `integer`
- **Default**: `8000`
- **Description**: Container port to expose
- **Range**: 1-65535
- **Example**: `3000`

### `external`
- **Type**: `boolean`
- **Default**: `true`
- **Description**: Enable external ingress
- **Example**: `false` (for internal services)

### `cpu`
- **Type**: `float`
- **Default**: `0.25`
- **Description**: CPU cores allocation
- **Range**: 0.25-2.0
- **Example**: `0.5`

### `memory`
- **Type**: `string`
- **Default**: `0.5Gi`
- **Description**: Memory allocation
- **Format**: Number followed by Gi
- **Example**: `1Gi`, `2Gi`

### `min_replicas`
- **Type**: `integer`
- **Default**: `1`
- **Description**: Minimum number of instances
- **Range**: 0-30
- **Example**: `2`

### `max_replicas`
- **Type**: `integer`
- **Default**: `10`
- **Description**: Maximum number of instances
- **Range**: 1-30
- **Example**: `20`

### `context`
- **Type**: `string`
- **Default**: `.`
- **Description**: Docker build context path
- **Example**: `./services/api`

## Environment Variables

tachi supports environment variable substitution using the `${VAR_NAME}` syntax:

```yaml
azure:
  log_analytics_workspace_id: ${LOG_ANALYTICS_ID}
  log_analytics_workspace_key: ${LOG_ANALYTICS_KEY}
```

Variables are resolved at runtime from:
1. System environment variables
2. GitHub secrets (when running in Actions)

## Complete Example

Here's a comprehensive configuration example:

```yaml
name: ecommerce-platform
strategy: trunk-release-stage

azure:
  resource_group: rg-ecommerce-prod
  registry: ecommerceregistry
  location: eastus2
  log_analytics_workspace_id: ${LOG_ANALYTICS_ID}
  log_analytics_workspace_key: ${LOG_ANALYTICS_KEY}

services:
  # Public-facing web application
  - name: web
    dockerfile: apps/web/Dockerfile
    port: 3000
    external: true
    cpu: 1
    memory: 2Gi
    min_replicas: 3
    max_replicas: 20
    context: ./apps/web
    
  # API service
  - name: api
    dockerfile: services/api/Dockerfile
    port: 8080
    external: true
    cpu: 0.75
    memory: 1.5Gi
    min_replicas: 2
    max_replicas: 15
    context: ./services/api
    
  # Background worker (internal only)
  - name: worker
    dockerfile: services/worker/Dockerfile
    port: 9000
    external: false
    cpu: 0.5
    memory: 1Gi
    min_replicas: 1
    max_replicas: 5
    context: ./services/worker
```

## Validation Rules

tachi validates your configuration to ensure:

1. **Required fields** are present
2. **Strategies** are valid
3. **Service names** are unique
4. **Ports** are in valid range (1-65535)
5. **CPU** values are positive
6. **Replica counts** are logical (max >= min)

Run validation with:

```bash
uvx tachi validate --config tachi.yaml --verbose
```

## Best Practices

1. **Resource Allocation**
   - Start with lower CPU/memory and scale up based on monitoring
   - Set min_replicas based on baseline traffic
   - Set max_replicas with headroom for traffic spikes

2. **Service Organization**
   - Use descriptive service names
   - Group related Dockerfiles in service directories
   - Keep contexts as specific as possible for faster builds

3. **Security**
   - Never commit sensitive values directly
   - Use environment variables for secrets
   - Store Log Analytics keys in GitHub secrets

4. **Naming Conventions**
   - Use lowercase with hyphens for names
   - Be consistent across services
   - Include environment in resource group names