---
sidebar_position: 7
---

# Command Reference

Complete reference for all tachi CLI commands.

## Global Options

Options available for all commands:

```bash
uvx tachi [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### `--version`
Show the version of tachi.

```bash
uvx tachi --version
```

### `--help`
Show help message and available commands.

```bash
uvx tachi --help
```

## Commands

### `generate`

Generate GitHub Actions workflows and Azure Container Apps configurations.

```bash
uvx tachi generate [OPTIONS]
```

#### Options

##### `--config, -c`
- **Type**: Path
- **Required**: No (interactive mode if not provided)
- **Description**: Path to configuration file

```bash
uvx tachi generate --config tachi.yaml
```

##### `--output, -o`
- **Type**: Path
- **Default**: Current directory
- **Description**: Output directory for generated files

```bash
uvx tachi generate --config tachi.yaml --output ./generated
```

##### `--dry-run`
- **Type**: Flag
- **Default**: False
- **Description**: Preview what would be generated without creating files

```bash
uvx tachi generate --config tachi.yaml --dry-run
```

##### `--force, -f`
- **Type**: Flag
- **Default**: False
- **Description**: Overwrite existing files without prompting

```bash
uvx tachi generate --config tachi.yaml --force
```

#### Examples

**Basic generation:**
```bash
uvx tachi generate --config tachi.yaml
```

**Generate to specific directory:**
```bash
uvx tachi generate --config tachi.yaml --output ./ci
```

**Preview without creating files:**
```bash
uvx tachi generate --config tachi.yaml --dry-run
```

**Overwrite existing files:**
```bash
uvx tachi generate --config tachi.yaml --force
```

**Interactive mode (no config file):**
```bash
uvx tachi generate
```

#### Output

The command generates:

```
output/
├── .github/
│   └── workflows/
│       ├── pr-deploy.yaml
│       ├── pr-cleanup.yaml
│       ├── stage-deploy.yaml  # Only for trunk-release-stage
│       └── prod-deploy.yaml
├── container-apps/
│   └── configs/
│       ├── service1.yaml
│       └── service2.yaml
└── SETUP.md
```

### `validate`

Validate a tachi configuration file.

```bash
uvx tachi validate [OPTIONS]
```

#### Options

##### `--config, -c`
- **Type**: Path
- **Required**: Yes
- **Description**: Path to configuration file to validate

```bash
uvx tachi validate --config tachi.yaml
```

##### `--verbose, -v`
- **Type**: Flag
- **Default**: False
- **Description**: Show detailed configuration information

```bash
uvx tachi validate --config tachi.yaml --verbose
```

#### Examples

**Basic validation:**
```bash
uvx tachi validate --config tachi.yaml
```

Output:
```
✅ Configuration is valid!
   📦 Project: my-app
   🚀 Strategy: trunk-release-stage
   🔧 Services: 3 (web, api, worker)
```

**Verbose validation:**
```bash
uvx tachi validate --config tachi.yaml --verbose
```

Output includes:
- Raw configuration display
- Detailed service information
- All configuration values with defaults

**Invalid configuration:**
```bash
uvx tachi validate --config invalid.yaml
```

Output:
```
❌ Configuration validation failed:
   - Invalid strategy 'custom'. Valid strategies: trunk-direct, trunk-release, trunk-release-stage
   - Service 'api': port must be between 1 and 65535, got 70000
   - Service 'web': cpu must be greater than 0, got -1
```

## Interactive Mode

When running `generate` without a config file, tachi enters interactive mode:

```bash
uvx tachi generate
```

### Interactive Prompts

1. **Project name**: Name for your project
2. **Deployment strategy**: Choose from available strategies
3. **Azure configuration**:
   - Resource group name
   - Container registry name
   - Azure location
4. **Service configuration** (repeatable):
   - Service name
   - Dockerfile path
   - Port number
   - External access (Y/n)
   - CPU allocation
   - Memory allocation
5. **Save configuration**: Option to save as YAML file
6. **Generate files**: Proceed with generation

### Interactive Mode Example

```
🚀 Welcome to tachi interactive mode!

Project name: my-awesome-app
Deployment strategy (trunk-direct, trunk-release, trunk-release-stage) [trunk-release]: trunk-release-stage

📍 Azure Configuration:
  Resource group: rg-myapp
  Container registry name: myappregistry
  Location [eastus]: westus2

🔧 Service Configuration:
  Service name: web
  Dockerfile path [Dockerfile]: docker/Dockerfile.web
  Port [8080]: 3000
  External access? [Y/n]: y
  CPU cores [0.25]: 0.5
  Memory [0.5Gi]: 1Gi

Add another service? [y/N]: y

🔧 Service Configuration:
  Service name: api
  Dockerfile path [Dockerfile]: docker/Dockerfile.api
  Port [8080]: 8080
  External access? [Y/n]: y
  CPU cores [0.25]: 1
  Memory [0.5Gi]: 2Gi

Add another service? [y/N]: n

💾 Save configuration to my-awesome-app.yaml? [y/N]: y
✅ Configuration saved to my-awesome-app.yaml

🚀 Generate files now? [y/N]: y
```

## Exit Codes

tachi uses standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Command line usage error

## Environment Variables

tachi respects these environment variables:

### `NO_COLOR`
Disable colored output when set to any value.

```bash
NO_COLOR=1 uvx tachi validate --config tachi.yaml
```

### `TACHI_OUTPUT_DIR`
Default output directory for generate command.

```bash
export TACHI_OUTPUT_DIR=./ci-cd
uvx tachi generate --config tachi.yaml
```

## Tips and Tricks

### Validation in CI

Add validation to your CI pipeline:

```yaml
- name: Validate tachi config
  run: uvx tachi validate --config tachi.yaml
```

### Dry Run for Safety

Always use `--dry-run` first when regenerating:

```bash
uvx tachi generate --config tachi.yaml --dry-run
```

### Script Integration

Use tachi in scripts:

```bash
#!/bin/bash
if uvx tachi validate --config tachi.yaml; then
    uvx tachi generate --config tachi.yaml --force
else
    echo "Invalid configuration!"
    exit 1
fi
```

### Multiple Configurations

Manage multiple environments:

```bash
# Development
uvx tachi generate --config tachi.dev.yaml --output ./dev

# Production
uvx tachi generate --config tachi.prod.yaml --output ./prod
```