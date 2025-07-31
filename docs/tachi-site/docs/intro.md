---
slug: /
sidebar_position: 1
sidebar_label: Introduction
---

import styles from '@site/src/css/ConstructionBanner.module.css';

export function ConstructionBanner() {
  return (
    <div className={styles.constructionBanner}>
      <div className="container">
        <p className={styles.constructionText}>
          🚧 <strong>Documentation Under Construction</strong> 🚧
        </p>
        <p className={styles.constructionSubtext}>
          This documentation site is currently under development and may not reflect accurate information. 
          Please check back later for the complete documentation.
        </p>
      </div>
    </div>
  );
}

<ConstructionBanner />

# Introduction

Welcome to **tachi** - a CLI tool for generating GitHub Actions workflows.

## What is tachi?

tachi automates the creation of CI/CD pipelines for project deployments. It generates:

- 🔧 **GitHub Actions workflows** for building, testing, and deploying your applications
- 📦 **Azure Container Apps configurations** with proper resource allocation and scaling
- 📋 **Setup documentation** with all required secrets and configuration steps

## Key Features

### 🚀 Multiple Deployment Strategies

Choose the deployment strategy that fits your project needs:

- **trunk-direct**: Simple deployment directly to production on merge
- **trunk-release**: Tag-based releases without staging
- **trunk-release-stage**: Full pipeline with staging environment

All strategies include dynamic PR environments for testing changes in isolation.

> **Note**: The current implementation supports deployment to Azure Container Apps. Support for Azure Functions and Azure Kubernetes Service (AKS) is on the roadmap.

## Quick Example

Here's how simple it is to get started:

```yaml
# tachi.yaml
name: my-app
strategy: trunk-release-stage

azure:
  resource_group: rg-myapp
  registry: myappregistry
  location: eastus

services:
  - name: api
    port: 8080
    external: true
    cpu: 0.5
    memory: 1Gi
```

Run tachi to generate everything:

```bash
uvx tachi generate --config tachi.yaml
```

That's it! You now have complete GitHub Actions workflows and Azure configurations ready to deploy.

## Next Steps

- [Quick Start Guide](./quickstart) - Get up and running in 5 minutes
- [Configuration Reference](./configuration) - Detailed configuration options
- [Examples](./examples) - Real-world configuration examples
- [Deployment Strategies](./deployment-strategies) - Choose the right strategy
