---
sidebar_position: 2
---

# Quick Start

Get up and running with tachi in just a few minutes.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** installed on your system
- **uv** package manager ([installation guide](https://github.com/astral-sh/uv))
- A **GitHub repository** for your project

## Installation

tachi can be run directly using `uvx` without installation:

```bash
uvx tachi --help
```

For frequent use, you can install it locally:

```bash
# Clone the repository
git clone https://github.com/Avidity-Dev/tachi.git
cd tachi

# Install with uv
uv pip install -e .
```

## Step 1: Create Your Configuration

Create a `tachi.yaml` file in your project root:

```yaml
name: my-awesome-app
strategy: trunk-release-stage

azure:
  resource_group: rg-myapp
  registry: myappregistry
  location: eastus

services:
  - name: web
    dockerfile: Dockerfile.web
    port: 3000
    external: true
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 10
```

## Step 2: Validate Your Configuration

Before generating files, validate your configuration:

```bash
uvx tachi validate --config tachi.yaml
```

You should see:
```
✅ Configuration is valid!
   📦 Project: my-awesome-app
   🚀 Strategy: trunk-release-stage
   🔧 Services: 1 (web)
```

## Step 3: Generate Workflows

Generate your GitHub Actions workflows and Azure configurations:

```bash
uvx tachi generate --config tachi.yaml
```

This creates:
```
.github/
└── workflows/
    ├── pr-deploy.yaml      # PR environment deployment
    ├── pr-cleanup.yaml     # PR environment cleanup
    ├── stage-deploy.yaml   # Staging deployment
    └── prod-deploy.yaml    # Production deployment

container-apps/
└── configs/
    └── web.yaml           # Container app configuration

SETUP.md                   # Setup instructions
```

## Step 4: Configure GitHub Secrets

Follow the instructions in the generated `SETUP.md` file to configure your GitHub secrets:

### Required Secrets

1. **Azure Service Principal**:
   ```bash
   az ad sp create-for-rbac --name "github-actions" \
     --role contributor \
     --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
     --json-auth
   ```

   Add the output as `AZURE_CREDENTIALS` secret.

2. **Container Registry Access**:
   - `REGISTRY_LOGIN_SERVER`: myappregistry.azurecr.io
   - `REGISTRY_USERNAME`: Service principal client ID
   - `REGISTRY_PASSWORD`: Service principal client secret

3. **Azure Resources**:
   - `AZURE_SUBSCRIPTION_ID`: Your subscription ID
   - `AZURE_RESOURCE_GROUP`: rg-myapp
   - `AZURE_LOCATION`: eastus

## Step 5: Push and Deploy

1. Commit the generated files:
   ```bash
   git add .github container-apps SETUP.md
   git commit -m "Add tachi CI/CD configuration"
   ```

2. Push to GitHub:
   ```bash
   git push origin main
   ```

3. Create a pull request to see dynamic environments in action!

## What Happens Next?

With the `trunk-release-stage` strategy:

1. **Open a PR** → Creates a dynamic preview environment
2. **Merge to main** → Deploys to staging environment
3. **Create a tag** (v*) → Deploys to production

Each environment gets its own URL, and PR environments are automatically cleaned up when closed.

## Interactive Mode

Don't have a configuration file yet? Use interactive mode:

```bash
uvx tachi generate
```

tachi will guide you through creating a configuration step by step.

## Next Steps

- Explore [Configuration Options](./configuration) for advanced settings
- Check out [Examples](./examples) for different scenarios
- Learn about [Deployment Strategies](./deployment-strategies) in detail
- Read the [Developer Guide](./developer-guide) for customization