# Tachi Configuration Examples

This directory contains example configuration files demonstrating various deployment scenarios and strategies.

## Examples

### simple-web-app.yaml
- **Strategy**: `trunk-direct`
- **Use Case**: Simple web applications, internal tools
- **Features**: Single service, direct deployment to production

### microservices-staging.yaml
- **Strategy**: `trunk-release-stage`
- **Use Case**: Complex applications requiring staging validation
- **Features**: Multiple services, staging environment, Log Analytics integration

### tag-based-release.yaml
- **Strategy**: `trunk-release`
- **Use Case**: Applications requiring controlled releases
- **Features**: Tag-based production deployments, no staging

### internal-tools.yaml
- **Strategy**: `trunk-direct`
- **Use Case**: Low-risk internal applications
- **Features**: Minimal configuration, uses defaults

### high-traffic-app.yaml
- **Strategy**: `trunk-release-stage`
- **Use Case**: High-traffic production applications
- **Features**: Advanced scaling configuration, multiple services, resource optimization

## Usage

1. Copy an example that matches your use case:
   ```bash
   cp examples/simple-web-app.yaml tachi.yaml
   ```

2. Modify the configuration to match your project:
   - Update the `name` field
   - Adjust Azure settings (`resource_group`, `registry`, etc.)
   - Customize services as needed

3. Validate your configuration:
   ```bash
   uvx tachi validate --config tachi.yaml
   ```

4. Generate workflows:
   ```bash
   uvx tachi generate --config tachi.yaml
   ```

## Configuration Tips

- **Defaults**: Many fields have sensible defaults. Start minimal and add as needed.
- **Environment Variables**: Use `${VAR_NAME}` syntax for sensitive values like Log Analytics keys.
- **Scaling**: Set `min_replicas` based on minimum traffic and `max_replicas` based on peak load.
- **Resources**: Start with lower CPU/memory and adjust based on monitoring.
- **Strategy Selection**:
  - `trunk-direct`: Fast iteration, good for development and internal tools
  - `trunk-release`: Controlled releases without staging overhead
  - `trunk-release-stage`: Full pipeline for critical production applications