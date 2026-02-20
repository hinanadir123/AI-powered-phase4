# GitHub Actions CI/CD Workflow Documentation

## Overview
This document describes the GitHub Actions CI/CD workflow for automated deployment of the Todo AI Chatbot to Oracle OKE.

## Workflow Configuration

The CI/CD workflow is configured in `.github/workflows/deploy-oke.yml` and consists of multiple stages:

### 1. Build and Test Stage
- **Purpose**: Builds Docker images for each service and runs tests
- **Matrix Strategy**: Tests backend, frontend, and reminder worker services
- **Components**:
  - Linting (Python and JavaScript)
  - Unit tests with coverage reporting
  - Integration tests with mocked dependencies
  - Docker image building for each service
  - Docker image validation

### 2. End-to-End Testing Stage
- **Purpose**: Validates the integrated system functionality
- **Components**:
  - PostgreSQL database service
  - Kafka message broker service
  - End-to-end test execution
  - Database connectivity validation
  - Message broker integration validation

### 3. Staging Deployment Stage
- **Purpose**: Deploys to staging environment for final validation
- **Components**:
  - OCI CLI configuration
  - Docker registry authentication
  - Image pushing to Oracle Container Registry
  - Helm-based deployment to staging namespace
  - Health checks and smoke tests

### 4. Production Deployment Stage
- **Purpose**: Deploy validated release to production
- **Components**:
  - Multi-environment deployment (backend, frontend, worker)
  - Resource constraints and scheduling
  - Monitoring stack deployment
  - Production health validation
  - Automated rollback capability

### 5. Notification Stage
- **Purpose**: Provides deployment feedback
- **Components**:
  - Slack notification integration
  - Discord notification integration
  - GitHub deployment status updates
  - Rollback notifications

## Environment Configuration

The workflow uses these environments for proper deployment staging:
- **Staging**: Automated deployment on successful tests
- **Production**: Manual approval required, with concurrency control

## Secrets Management

The workflow securely handles sensitive information using GitHub Secrets:

| Secret Name | Purpose | Required |
|-------------|---------|----------|
| `OCI_REGION_KEY` | Oracle region (e.g., iad, phx) | Yes |
| `OCI_TENANCY_NAMESPACE` | Oracle tenancy namespace | Yes |
| `OCI_USER_EMAIL` | Oracle Cloud user email | Yes |
| `OCI_REGION` | Oracle region full name | Yes |
| `OCI_TENANCY_OCID` | Oracle tenancy OCID | Yes |
| `OCI_USER_OCID` | Oracle user OCID | Yes |
| `OCI_KEY_FINGERPRINT` | Public key fingerprint | Yes |
| `OCI_PRIVATE_KEY` | Private key for authentication | Yes |
| `OCI_AUTH_TOKEN` | OCI API authentication token | Yes |
| `OCI_CLUSTER_ID` | OKE cluster OCID | Yes |
| `GRAFANA_ADMIN_PASSWORD` | Grafana admin password | No |
| `SMTP_*` | Email notification configuration | No |
| `*ALERT_EMAIL` | Alert recipient emails | No |
| `*_WEBHOOK_URL` | Slack/Discord URLs | No |

## Deployment Verification Strategy

### Health Checks
- Kubernetes readiness/liveness probe validation
- Dapr sidecar health verification
- Service endpoint connectivity
- Database connection validation
- Kafka connectivity testing

### Rollback Mechanism
- Automated failure detection
- Health-based rollback triggers
- Deployment history retention
- Manual intervention capability

## Monitoring Integration

The deployment process includes monitoring stack deployment:

1. **Prometheus**
   - Metrics collection
   - Custom alert rules
   - Service discovery configuration

2. **Grafana**
   - Dashboard provisioning
   - Custom dashboards
   - Datasource configuration

3. **Alertmanager**
   - Alert routing rules
   - Notification configuration
   - Escalation policies

4. **Loki and Promtail**
   - Log aggregation setup
   - Log retention policies
   - Query interface configuration

## Dapr Integration

Special considerations for Dapr-enabled services:
- Sidecar injection validation
- Component state verification
- Service invocation testing
- Pub/Sub connectivity validation
- State store operations

## Validation Procedures

Before a deployment is considered successful, these validations are performed:
- All pods are running and healthy
- Dapr sidecars are active and communicating
- Service endpoints are accessible
- Custom metrics are being collected
- Basic API functionality is verified
- Database connectivity is confirmed
- Message broker connectivity is established
- Alert rules are not firing incorrectly

## Performance Benchmarks

The CI/CD pipeline includes performance validation checks:
- API response time thresholds (p95 < 500ms)
- System resource utilization (CPU/memory)
- Database query performance
- Event processing latency < 1 second
- Support for 100+ concurrent users

## Security Compliance

The pipeline ensures security compliance through:
- Image vulnerability scanning (via build process)
- Kubernetes RBAC validation
- Network policy verification
- Secret encryption verification
- Non-root container execution
- Service account permissions

## Resource Optimization

To stay within Oracle Always Free tier limits:
- Resource requests/limits configured for all containers
- Auto-scaling policies
- Monitoring stack resource constraints
- Cron job efficiency for worker services
- Efficient Docker image layers

## Troubleshooting Guide

### Common Issues
1. **OCI Authentication Failures**
   - Verify private key format and access
   - Check key fingerprint match
   - Validate OCI user permissions

2. **Registry Push Failures**
   - Check authentication token validity
   - Verify registry endpoint format
   - Confirm proper repository permissions

3. **Kubernetes Deployment Issues**
   - Validate Helm chart syntax
   - Check for resource conflicts
   - Verify service account permissions

4. **Dapr Integration Problems**
   - Confirm Dapr operator status
   - Validate component configurations
   - Check sidecar connectivity

### Debugging Steps
1. Enable GitHub Actions workflow debugging
2. Review container logs in Kubernetes
3. Check Dapr sidecar logs specifically
4. Verify Kubernetes events for deployment pods
5. Monitor the monitoring stack for issues

This CI/CD workflow provides comprehensive automation for the Todo AI Chatbot deployment to the Oracle OKE cluster, with robust monitoring, error handling, and security practices.