# Logging Setup Guide - Loki and Promtail
## Task: T5.6.3 - Configure Logging with Loki and Promtail

**Version:** 1.0
**Date:** 2026-02-15
**Based on:** constitution.md v5.0, phase5-spec.md v1.0

---

## Overview

This guide provides instructions for setting up centralized logging using Loki and Promtail for the Todo AI Chatbot application. Loki is a horizontally-scalable, highly-available log aggregation system inspired by Prometheus, and Promtail is an agent that ships logs to Loki.

### Architecture

```
Kubernetes Pods → Promtail (DaemonSet) → Loki → Grafana
                     ↓
              /var/log/pods
```

### Components

- **Loki**: Log aggregation and storage system
- **Promtail**: Log collection agent (runs on every node)
- **Grafana**: Log visualization and querying interface

---

## Prerequisites

- Kubernetes cluster (Minikube, AKS, or GKE)
- kubectl configured and connected to cluster
- Helm 3.x installed (optional, for alternative installation)
- Grafana already deployed (from T5.6.2)

---

## Installation Steps

### Step 1: Create Monitoring Namespace

```bash
kubectl create namespace monitoring
```

### Step 2: Deploy Loki Configuration

Apply the Loki ConfigMap:

```bash
kubectl apply -f monitoring/loki/loki-config.yaml
```

This ConfigMap contains:
- **Retention**: 30 days (720 hours)
- **Storage**: Local filesystem (for Minikube) or object storage (for cloud)
- **Ingestion rate limits**: 4MB/s
- **Query timeout**: 5 minutes (721 hours max query length)
- **Compaction**: Enabled for storage optimization

### Step 3: Deploy Loki

Apply the Loki Deployment and Service:

```bash
kubectl apply -f monitoring/loki/loki-deployment.yaml
kubectl apply -f monitoring/loki/loki-service.yaml
```

Verify Loki is running:

```bash
kubectl get pods -n monitoring -l app=loki
kubectl logs -n monitoring -l app=loki
```

Expected output:
```
NAME                    READY   STATUS    RESTARTS   AGE
loki-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

### Step 4: Deploy Promtail Configuration

Apply the Promtail ConfigMap:

```bash
kubectl apply -f monitoring/promtail/promtail-config.yaml
```

This ConfigMap contains:
- **Scrape configs**: Kubernetes pod discovery
- **Pipeline stages**: Log parsing, multiline support, label extraction
- **Drop rules**: Filter out noisy logs (health checks, readiness probes)
- **Relabel configs**: Extract Kubernetes metadata (namespace, pod, container)

### Step 5: Deploy Promtail DaemonSet

Apply the Promtail DaemonSet with RBAC:

```bash
kubectl apply -f monitoring/promtail/promtail-daemonset.yaml
```

This creates:
- **DaemonSet**: Runs Promtail on every node
- **ServiceAccount**: For Kubernetes API access
- **ClusterRole**: Permissions to read pod metadata
- **ClusterRoleBinding**: Binds role to service account

Verify Promtail is running on all nodes:

```bash
kubectl get daemonset -n monitoring promtail
kubectl get pods -n monitoring -l app=promtail
```

Expected output:
```
NAME       DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
promtail   3         3         3       3            3           <none>          30s
```

### Step 6: Configure Grafana Datasource

Apply the Loki datasource configuration:

```bash
kubectl apply -f monitoring/grafana/loki-datasource.yaml
```

If Grafana is deployed via Helm, you can also add the datasource via values:

```yaml
# values.yaml for Grafana Helm chart
datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
    - name: Loki
      type: loki
      access: proxy
      url: http://loki:3100
      isDefault: false
```

Then upgrade Grafana:

```bash
helm upgrade grafana grafana/grafana -f values.yaml -n monitoring
```

### Step 7: Verify Loki Integration in Grafana

1. Port-forward Grafana (if not using ingress):
   ```bash
   kubectl port-forward -n monitoring svc/grafana 3000:80
   ```

2. Open Grafana in browser: http://localhost:3000

3. Navigate to **Configuration → Data Sources**

4. Verify Loki datasource is listed and working

5. Click **Test** button - should show "Data source is working"

### Step 8: Explore Logs in Grafana

1. Navigate to **Explore** in Grafana

2. Select **Loki** as datasource

3. Use LogQL queries to search logs:

   **Example queries:**

   - All logs from todo-app namespace:
     ```logql
     {namespace="todo-app"}
     ```

   - Error logs only:
     ```logql
     {namespace="todo-app"} |= "ERROR"
     ```

   - Logs from backend pod:
     ```logql
     {namespace="todo-app", app="backend"}
     ```

   - Logs with specific label:
     ```logql
     {namespace="todo-app", level="error"}
     ```

   - Rate of error logs (last 5 minutes):
     ```logql
     rate({namespace="todo-app"} |= "ERROR" [5m])
     ```

---

## Log Levels

The application uses the following log levels:

- **ERROR**: Critical errors requiring immediate attention
- **WARN**: Warnings that may indicate issues
- **INFO**: Informational messages (e.g., "Task created")
- **DEBUG**: Detailed debugging information

Configure log levels in application environment variables:

```yaml
env:
- name: LOG_LEVEL
  value: "INFO"
```

---

## Log Retention

Loki is configured with 30-day retention:

```yaml
limits_config:
  retention_period: 720h  # 30 days

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h
```

To change retention, edit `monitoring/loki/loki-config.yaml` and reapply:

```bash
kubectl apply -f monitoring/loki/loki-config.yaml
kubectl rollout restart deployment/loki -n monitoring
```

---

## Troubleshooting

### Loki Pod Not Starting

Check logs:
```bash
kubectl logs -n monitoring -l app=loki
```

Common issues:
- **Permission denied**: Check volume mounts and security context
- **Config error**: Validate loki.yaml syntax
- **Out of memory**: Increase memory limits in deployment

### Promtail Not Collecting Logs

Check Promtail logs:
```bash
kubectl logs -n monitoring -l app=promtail
```

Common issues:
- **RBAC permissions**: Verify ServiceAccount, ClusterRole, and ClusterRoleBinding
- **Volume mounts**: Ensure /var/log and /var/lib/docker/containers are mounted
- **Loki unreachable**: Check Loki service and network connectivity

### No Logs in Grafana

1. Verify Loki datasource is configured correctly
2. Check Loki is receiving logs:
   ```bash
   kubectl port-forward -n monitoring svc/loki 3100:3100
   curl http://localhost:3100/loki/api/v1/label
   ```
3. Check Promtail is sending logs:
   ```bash
   kubectl logs -n monitoring -l app=promtail | grep "POST /loki/api/v1/push"
   ```

### High Memory Usage

Reduce retention or increase memory limits:

```yaml
# In loki-deployment.yaml
resources:
  limits:
    memory: 1Gi  # Increase from 512Mi
```

---

## Performance Tuning

### Ingestion Rate Limits

Adjust in `loki-config.yaml`:

```yaml
limits_config:
  ingestion_rate_mb: 4        # MB/s per stream
  ingestion_burst_size_mb: 6  # Burst size
```

### Query Performance

- Use label filters before line filters: `{app="backend"} |= "error"`
- Limit time range for queries
- Use metric queries for aggregations: `rate()`, `count_over_time()`

### Storage Optimization

For production, use object storage instead of filesystem:

```yaml
storage_config:
  aws:
    s3: s3://region/bucket
    s3forcepathstyle: true
```

Or Azure Blob Storage:

```yaml
storage_config:
  azure:
    container_name: loki
    account_name: <account>
    account_key: <key>
```

---

## Monitoring Loki

Create Prometheus alerts for Loki:

```yaml
groups:
- name: loki
  rules:
  - alert: LokiDown
    expr: up{job="loki"} == 0
    for: 5m
    annotations:
      summary: "Loki is down"

  - alert: LokiHighIngestionRate
    expr: rate(loki_ingester_bytes_received_total[5m]) > 10000000
    for: 5m
    annotations:
      summary: "Loki ingestion rate is high"
```

---

## Cleanup

To remove Loki and Promtail:

```bash
kubectl delete -f monitoring/promtail/promtail-daemonset.yaml
kubectl delete -f monitoring/promtail/promtail-config.yaml
kubectl delete -f monitoring/loki/loki-service.yaml
kubectl delete -f monitoring/loki/loki-deployment.yaml
kubectl delete -f monitoring/loki/loki-config.yaml
kubectl delete -f monitoring/grafana/loki-datasource.yaml
```

---

## Next Steps

1. Create Grafana dashboards for log visualization
2. Set up alerting rules for error logs
3. Configure log-based metrics
4. Integrate with distributed tracing (Tempo)
5. Consider cloud-native logging for production (see cloud-logging-azure.md and cloud-logging-gke.md)

---

## References

- Loki Documentation: https://grafana.com/docs/loki/latest/
- Promtail Documentation: https://grafana.com/docs/loki/latest/clients/promtail/
- LogQL Query Language: https://grafana.com/docs/loki/latest/logql/
- Grafana Loki Best Practices: https://grafana.com/docs/loki/latest/best-practices/

---

**END OF LOGGING SETUP GUIDE**
