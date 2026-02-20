# Monitoring and Logging Configuration
## Todo AI Chatbot - Phase 5

**Version:** 1.0
**Date:** 2026-02-15
**Status:** Complete

---

## Overview

This directory contains all monitoring and logging configurations for the Todo AI Chatbot application, implementing Phase 5 observability requirements.

### Components

- **Prometheus + Grafana**: Metrics collection and visualization (T5.6.2)
- **Loki + Promtail**: Log aggregation and querying (T5.6.3)
- **Cloud Logging**: Azure and GKE alternatives (T5.6.3)

---

## Directory Structure

```
monitoring/
├── loki/
│   ├── loki-config.yaml          # Loki configuration (30-day retention)
│   ├── loki-deployment.yaml      # Loki Kubernetes deployment
│   └── loki-service.yaml         # Loki ClusterIP service
├── promtail/
│   ├── promtail-config.yaml      # Promtail configuration (pod discovery)
│   └── promtail-daemonset.yaml   # Promtail DaemonSet with RBAC
├── grafana/
│   └── loki-datasource.yaml      # Grafana Loki datasource
├── logging-setup.md              # Logging setup guide
├── cloud-logging-azure.md        # Azure Log Analytics guide
├── cloud-logging-gke.md          # GKE Cloud Logging guide
├── T5.6.3-validation-report.md   # Task validation report
└── README.md                     # This file
```

---

## Quick Start

### Deploy Loki and Promtail (Local/Minikube)

```bash
# Create namespace
kubectl create namespace monitoring

# Deploy Loki
kubectl apply -f loki/loki-config.yaml
kubectl apply -f loki/loki-deployment.yaml
kubectl apply -f loki/loki-service.yaml

# Deploy Promtail
kubectl apply -f promtail/promtail-config.yaml
kubectl apply -f promtail/promtail-daemonset.yaml

# Configure Grafana datasource
kubectl apply -f grafana/loki-datasource.yaml

# Verify deployment
kubectl get pods -n monitoring
```

### Access Logs in Grafana

```bash
# Port-forward Grafana (if not using ingress)
kubectl port-forward -n monitoring svc/grafana 3000:80

# Open browser: http://localhost:3000
# Navigate to: Explore → Select Loki datasource
# Query: {namespace="todo-app"}
```

---

## Configuration Details

### Loki Configuration

- **Retention**: 30 days (720 hours)
- **Ingestion Rate**: 4 MB/s (burst: 6 MB/s)
- **Storage**: Local filesystem (emptyDir for dev, PVC for prod)
- **Query Timeout**: 5 minutes
- **Compaction**: Enabled

### Promtail Configuration

- **Deployment**: DaemonSet (runs on every node)
- **Scrape**: All Kubernetes pods
- **Pipeline**: Docker logs → Multiline → Regex → Labels → Drop filters
- **Metadata**: Namespace, pod, container, node labels
- **Filtering**: Drops health check and readiness probe logs

### Grafana Integration

- **Datasource**: Loki (http://loki:3100)
- **Access Mode**: Proxy
- **Trace Correlation**: Derived fields for trace IDs
- **Max Lines**: 1000 per query

---

## Cloud Logging Alternatives

### Azure AKS

For production deployments on Azure AKS, use Azure Log Analytics:

- **Free Tier**: 5 GB/month
- **Retention**: 31 days included
- **Query Language**: KQL (Kusto Query Language)
- **Integration**: Container Insights

See: `cloud-logging-azure.md`

### Google GKE

For production deployments on Google GKE, use Cloud Logging:

- **Free Tier**: 50 GB/month per project
- **Retention**: 30 days included
- **Query Language**: Cloud Logging query syntax
- **Integration**: Auto-enabled on GKE

See: `cloud-logging-gke.md`

---

## Log Levels

The application uses these log levels:

- **ERROR**: Critical errors requiring immediate attention
- **WARN**: Warnings that may indicate issues
- **INFO**: Informational messages (e.g., "Task created")
- **DEBUG**: Detailed debugging information

Configure in application:

```yaml
env:
- name: LOG_LEVEL
  value: "INFO"
```

---

## Example Queries

### LogQL (Loki)

```logql
# All logs from todo-app namespace
{namespace="todo-app"}

# Error logs only
{namespace="todo-app"} |= "ERROR"

# Logs from backend pod
{namespace="todo-app", app="backend"}

# Rate of errors (last 5 minutes)
rate({namespace="todo-app"} |= "ERROR" [5m])
```

### KQL (Azure)

```kql
// All logs from todo-app namespace
ContainerLog
| where Namespace == "todo-app"
| project TimeGenerated, ContainerName, LogEntry

// Error logs only
ContainerLog
| where Namespace == "todo-app"
| where LogEntry contains "ERROR"
```

### Cloud Logging (GKE)

```
# All logs from todo-app namespace
resource.type="k8s_container"
resource.labels.namespace_name="todo-app"

# Error logs only
resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
severity>=ERROR
```

---

## Troubleshooting

### Loki Not Starting

```bash
# Check logs
kubectl logs -n monitoring -l app=loki

# Common issues:
# - Config syntax error: Validate loki-config.yaml
# - Permission denied: Check security context
# - Out of memory: Increase memory limits
```

### Promtail Not Collecting Logs

```bash
# Check logs
kubectl logs -n monitoring -l app=promtail

# Common issues:
# - RBAC permissions: Verify ServiceAccount, ClusterRole
# - Volume mounts: Check /var/log and /var/lib/docker/containers
# - Loki unreachable: Verify Loki service
```

### No Logs in Grafana

```bash
# Verify Loki datasource
kubectl port-forward -n monitoring svc/loki 3100:3100
curl http://localhost:3100/ready
curl http://localhost:3100/loki/api/v1/labels

# Check Promtail is sending logs
kubectl logs -n monitoring -l app=promtail | grep "POST /loki/api/v1/push"
```

---

## Performance Tuning

### Reduce Log Volume

1. **Filter noisy logs** in promtail-config.yaml:
   ```yaml
   - drop:
       source: message
       expression: ".*health.*"
   ```

2. **Reduce log verbosity** in application code

3. **Sample logs** for high-volume services

### Optimize Storage

For production, use object storage:

```yaml
# S3
storage_config:
  aws:
    s3: s3://region/bucket

# Azure Blob
storage_config:
  azure:
    container_name: loki
    account_name: <account>

# GCS
storage_config:
  gcs:
    bucket_name: loki-logs
```

---

## Cost Optimization

### Local Deployment (Loki)

- **Infrastructure**: Self-hosted (compute costs only)
- **Storage**: Local disk or PVC
- **Estimated Cost**: $0 (Minikube) or ~$10-20/month (cloud VMs)

### Cloud Logging

**Azure Log Analytics:**
- Free: 5 GB/month
- Paid: $2.30/GB after free tier
- Estimated: $0-10/month for small apps

**GKE Cloud Logging:**
- Free: 50 GB/month per project
- Paid: $0.50/GB after free tier
- Estimated: $0-5/month for small apps

---

## Next Steps

1. **Deploy to Minikube** using quick start commands
2. **Verify logs** in Grafana Explore
3. **Create dashboards** for log visualization
4. **Setup alerts** for error rate and Loki health
5. **Consider cloud logging** for production deployments

---

## References

- Loki Documentation: https://grafana.com/docs/loki/latest/
- Promtail Documentation: https://grafana.com/docs/loki/latest/clients/promtail/
- LogQL Query Language: https://grafana.com/docs/loki/latest/logql/
- Azure Log Analytics: https://docs.microsoft.com/azure/azure-monitor/
- GKE Cloud Logging: https://cloud.google.com/logging/docs

---

**Task:** T5.6.3 - Configure Logging with Loki and Promtail
**Status:** ✅ Complete
**Agent:** cicd-monitoring-agent
**Date:** 2026-02-15
