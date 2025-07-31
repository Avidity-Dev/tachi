---
sidebar_position: 8
---

# Troubleshooting

Common issues and solutions when using tachi.

## Installation Issues

### uvx command not found

**Problem**: `uvx: command not found`

**Solution**: Install uv first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Python version error

**Problem**: `Python 3.8+ is required`

**Solution**: Upgrade Python:
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11
```

## Configuration Issues

### Invalid YAML syntax

**Problem**: `Invalid YAML syntax in configuration file`

**Solution**: Validate your YAML:
1. Check for proper indentation (use spaces, not tabs)
2. Ensure colons have spaces after them
3. Quote strings with special characters
4. Use online YAML validator

**Example fix**:
```yaml
# Wrong
services:
-name: api  # Missing space after dash

# Correct
services:
  - name: api
```

### Strategy not recognized

**Problem**: `Invalid strategy 'custom-strategy'`

**Solution**: Use one of the valid strategies:
- `trunk-direct`
- `trunk-release`
- `trunk-release-stage`

### Port validation error

**Problem**: `port must be between 1 and 65535`

**Solution**: Use a valid port number:
```yaml
services:
  - name: api
    port: 8080  # Valid: 1-65535
```

## Generation Issues

### Output directory not empty

**Problem**: `Output directory is not empty. Overwrite existing files?`

**Solutions**:
1. Use `--force` flag to overwrite:
   ```bash
   uvx tachi generate --config tachi.yaml --force
   ```

2. Specify a different output directory:
   ```bash
   uvx tachi generate --config tachi.yaml --output ./new-output
   ```

3. Clean the existing directory first:
   ```bash
   rm -rf .github container-apps SETUP.md
   uvx tachi generate --config tachi.yaml
   ```

### Template rendering error

**Problem**: `Error rendering template`

**Possible causes**:
1. Missing required configuration values
2. Invalid configuration structure
3. Template syntax error (rare)

**Solution**: Validate configuration first:
```bash
uvx tachi validate --config tachi.yaml --verbose
```

## GitHub Actions Issues

### Workflow syntax error

**Problem**: GitHub Actions shows syntax error

**Solution**: 
1. Check generated YAML files for syntax
2. Validate in GitHub Actions workflow editor
3. Ensure no manual edits broke the syntax

### Missing secrets

**Problem**: `Error: Required secret 'AZURE_CREDENTIALS' not found`

**Solution**: Add all required secrets in GitHub:
1. Go to Settings → Secrets → Actions
2. Add each secret from SETUP.md
3. Ensure secret names match exactly

### Container registry authentication failed

**Problem**: `Error: unauthorized: authentication required`

**Solution**:
1. Verify registry credentials:
   ```bash
   az acr login --name myregistry
   ```

2. Check service principal permissions:
   ```bash
   az role assignment list --assignee <sp-client-id>
   ```

3. Ensure secrets are correct:
   - `REGISTRY_LOGIN_SERVER`: myregistry.azurecr.io
   - `REGISTRY_USERNAME`: Service principal client ID
   - `REGISTRY_PASSWORD`: Service principal client secret

## Azure Container Apps Issues

### Deployment fails

**Problem**: Container app deployment fails

**Common causes**:
1. Insufficient resources in region
2. Invalid configuration
3. Image pull errors

**Solutions**:
1. Check Azure quotas:
   ```bash
   az containerapp list --resource-group rg-myapp
   ```

2. Verify image exists:
   ```bash
   az acr repository list --name myregistry
   ```

3. Check container app logs:
   ```bash
   az containerapp logs show --name myapp-web --resource-group rg-myapp
   ```

### Environment URL not accessible

**Problem**: Container app URL returns 404 or timeout

**Solutions**:
1. Check ingress configuration:
   ```bash
   az containerapp show --name myapp-web --resource-group rg-myapp
   ```

2. Verify external access:
   ```yaml
   services:
     - name: web
       external: true  # Must be true for public access
   ```

3. Check application logs for startup errors

### Scaling issues

**Problem**: Container app not scaling as expected

**Solutions**:
1. Verify scaling rules in Azure Portal
2. Check CPU/memory usage:
   ```bash
   az monitor metrics list --resource <resource-id> --metric "CpuPercentage"
   ```

3. Adjust replica configuration:
   ```yaml
   services:
     - name: api
       min_replicas: 2  # Increase minimum
       max_replicas: 20  # Increase maximum
   ```

## Interactive Mode Issues

### Input not accepted

**Problem**: Interactive mode doesn't accept input

**Solution**: Ensure terminal supports interactive input:
```bash
# Run in proper terminal, not in CI/CD environment
uvx tachi generate
```

### Validation errors in interactive mode

**Problem**: Configuration created interactively fails validation

**Solution**: Save configuration and validate:
```bash
# Save during interactive mode
💾 Save configuration to my-app.yaml? [y/N]: y

# Then validate
uvx tachi validate --config my-app.yaml --verbose
```

## Performance Issues

### Slow generation

**Problem**: Generation takes a long time

**Solutions**:
1. Use specific output directory to avoid scanning
2. Ensure template directory is accessible
3. Check disk I/O performance

### Large output files

**Problem**: Generated files are very large

**Solution**: This usually indicates:
1. Too many services configured
2. Verbose configuration

Consider splitting into multiple projects if needed.

## Common Error Messages

### "Configuration file not found"

```bash
uvx tachi validate --config tachi.yml  # Wrong extension
```

**Fix**: Use correct filename:
```bash
uvx tachi validate --config tachi.yaml  # Correct
```

### "Service names must be unique"

```yaml
services:
  - name: api
  - name: api  # Duplicate!
```

**Fix**: Use unique names:
```yaml
services:
  - name: api
  - name: worker
```

### "CPU must be greater than 0"

```yaml
cpu: 0  # Invalid
```

**Fix**: Use valid CPU value:
```yaml
cpu: 0.25  # Minimum valid value
```

## Getting Help

If you encounter issues not covered here:

1. **Check the documentation**: Review relevant sections
2. **Validate your configuration**: Use `--verbose` flag
3. **Check GitHub issues**: Search existing issues
4. **Open a new issue**: Provide:
   - tachi version
   - Configuration file (sanitized)
   - Complete error message
   - Steps to reproduce

### Debug mode

For detailed output:
```bash
# Verbose validation
uvx tachi validate --config tachi.yaml --verbose

# Dry run to see what would be generated
uvx tachi generate --config tachi.yaml --dry-run
```

### Reporting bugs

When reporting issues:
1. Use minimal reproducible example
2. Include full error messages
3. Specify environment details
4. Check if issue exists in latest version