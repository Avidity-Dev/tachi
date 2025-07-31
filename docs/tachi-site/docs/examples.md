---
sidebar_position: 5
---

# Examples

Real-world configuration examples for different scenarios.

## Simple Web Application

Basic web application with direct deployment to production.

```yaml
# tachi.yaml
name: company-website
strategy: trunk-direct

azure:
  resource_group: rg-website
  registry: websiteregistry
  location: eastus

services:
  - name: web
    port: 80
    external: true
    cpu: 0.25
    memory: 0.5Gi
    min_replicas: 1
    max_replicas: 5
```

**Use case**: Static websites, marketing sites, simple web apps

## Microservices with Staging

Multi-service application with staging environment.

```yaml
# tachi.yaml
name: ecommerce-platform
strategy: trunk-release-stage

azure:
  resource_group: rg-ecommerce-prod
  registry: ecommerceregistry
  location: westus2
  log_analytics_workspace_id: ${LOG_ANALYTICS_ID}
  log_analytics_workspace_key: ${LOG_ANALYTICS_KEY}

services:
  # Frontend application
  - name: frontend
    dockerfile: apps/frontend/Dockerfile
    port: 3000
    external: true
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 10
    context: ./apps/frontend
    
  # API Gateway
  - name: api-gateway
    dockerfile: services/gateway/Dockerfile
    port: 8080
    external: true
    cpu: 0.75
    memory: 1.5Gi
    min_replicas: 3
    max_replicas: 15
    context: ./services/gateway
    
  # Product Service
  - name: product-service
    dockerfile: services/product/Dockerfile
    port: 8081
    external: false  # Internal only
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 10
    context: ./services/product
    
  # Order Service
  - name: order-service
    dockerfile: services/order/Dockerfile
    port: 8082
    external: false  # Internal only
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 10
    context: ./services/order
    
  # Background Worker
  - name: worker
    dockerfile: services/worker/Dockerfile
    port: 9000
    external: false
    cpu: 0.25
    memory: 0.5Gi
    min_replicas: 1
    max_replicas: 5
    context: ./services/worker
```

**Use case**: Complex applications with multiple services that need staging validation

## API with Controlled Releases

REST API with tag-based deployment strategy.

```yaml
# tachi.yaml
name: payment-api
strategy: trunk-release

azure:
  resource_group: rg-payment-api
  registry: paymentregistry
  location: eastus2

services:
  - name: api
    dockerfile: Dockerfile.api
    port: 8080
    external: true
    cpu: 1
    memory: 2Gi
    min_replicas: 3
    max_replicas: 20
    
  - name: webhook-processor
    dockerfile: Dockerfile.webhook
    port: 8090
    external: true
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 10
```

**Use case**: APIs that need versioned releases, financial services, integrations

## Internal Tools Suite

Multiple internal tools with simple deployment.

```yaml
# tachi.yaml
name: internal-tools
strategy: trunk-direct

azure:
  resource_group: rg-internal-tools
  registry: toolsregistry

services:
  # Admin Dashboard
  - name: admin-dashboard
    dockerfile: tools/admin/Dockerfile
    port: 3000
    external: true
    cpu: 0.25
    memory: 0.5Gi
    context: ./tools/admin
    
  # Metrics Dashboard
  - name: metrics
    dockerfile: tools/metrics/Dockerfile
    port: 3001
    external: true
    cpu: 0.25
    memory: 0.5Gi
    context: ./tools/metrics
    
  # Log Viewer
  - name: logs
    dockerfile: tools/logs/Dockerfile
    port: 3002
    external: true
    cpu: 0.25
    memory: 0.5Gi
    context: ./tools/logs
```

**Use case**: Internal dashboards, admin tools, development utilities

## High-Traffic Application

Application optimized for high traffic with auto-scaling.

```yaml
# tachi.yaml
name: social-platform
strategy: trunk-release-stage

azure:
  resource_group: rg-social-prod
  registry: socialregistry
  location: eastus
  log_analytics_workspace_id: ${LOG_ANALYTICS_ID}
  log_analytics_workspace_key: ${LOG_ANALYTICS_KEY}

services:
  # Web Application
  - name: web
    dockerfile: apps/web/Dockerfile
    port: 3000
    external: true
    cpu: 1.5
    memory: 3Gi
    min_replicas: 5      # Always keep 5 instances
    max_replicas: 50     # Scale up to 50 for traffic
    context: ./apps/web
    
  # API Service
  - name: api
    dockerfile: services/api/Dockerfile
    port: 8080
    external: true
    cpu: 2              # Maximum CPU
    memory: 4Gi
    min_replicas: 10
    max_replicas: 100   # Handle massive scale
    context: ./services/api
    
  # Real-time Service (WebSockets)
  - name: realtime
    dockerfile: services/realtime/Dockerfile
    port: 8081
    external: true
    cpu: 1
    memory: 2Gi
    min_replicas: 3
    max_replicas: 30
    context: ./services/realtime
    
  # Background Jobs
  - name: jobs
    dockerfile: services/jobs/Dockerfile
    port: 9000
    external: false
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 20
    context: ./services/jobs
```

**Use case**: Social media, streaming platforms, high-traffic SaaS

## Monorepo with Multiple Apps

Configuration for a monorepo containing multiple applications.

```yaml
# tachi.yaml
name: platform-services
strategy: trunk-release-stage

azure:
  resource_group: rg-platform
  registry: platformregistry
  location: westus2

services:
  # Customer-facing app
  - name: customer-app
    dockerfile: docker/Dockerfile.customer
    port: 3000
    external: true
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 10
    context: ./apps/customer
    
  # Admin application
  - name: admin-app
    dockerfile: docker/Dockerfile.admin
    port: 3001
    external: true
    cpu: 0.25
    memory: 0.5Gi
    min_replicas: 1
    max_replicas: 3
    context: ./apps/admin
    
  # Shared API
  - name: api
    dockerfile: docker/Dockerfile.api
    port: 8080
    external: true
    cpu: 1
    memory: 2Gi
    min_replicas: 3
    max_replicas: 15
    context: ./services/api
    
  # Authentication Service
  - name: auth
    dockerfile: docker/Dockerfile.auth
    port: 8081
    external: false
    cpu: 0.5
    memory: 1Gi
    min_replicas: 2
    max_replicas: 5
    context: ./services/auth
```

**Use case**: Monorepos, platform applications, shared services

## Development Environment

Minimal configuration for development and testing.

```yaml
# tachi.yaml
name: dev-environment
strategy: trunk-direct

azure:
  resource_group: rg-dev
  registry: devregistry
  location: eastus

services:
  - name: app
    port: 8000
    external: true
    # Use minimal resources for dev
    cpu: 0.25
    memory: 0.5Gi
    min_replicas: 1
    max_replicas: 2
```

**Use case**: Development environments, proof of concepts, demos

## Tips for Different Scenarios

### For Microservices
- Use `external: false` for internal services
- Consider service mesh integration
- Group related services in contexts

### For High Traffic
- Set higher `min_replicas` for baseline capacity
- Use maximum CPU/memory for critical services
- Enable Log Analytics for monitoring

### For Cost Optimization
- Use lower `min_replicas` for non-critical services
- Set appropriate `max_replicas` limits
- Consider time-based scaling

### For Security
- Keep sensitive services internal (`external: false`)
- Use environment variables for secrets
- Enable Log Analytics for audit trails