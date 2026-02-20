# Monitoring Setup - Prometheus and Grafana
## Task: T5.6.2 - Setup Prometheus and Grafana for Metrics Collection and Visualization
## Constitution: v5.0 compliant | Phase 5 Specification: v1.0

---

## Overview

This directory contains all configurations for monitoring the Todo AI Chatbot application using Prometheus for metrics collection and Grafana for visualization. The monitoring stack provides comprehensive observability across application, infrastructure, Kafka, and Dapr components.

### Components

- **Prometheus**: Time-series database for metrics collection
- **Grafana**: Visualization and dashboarding platform
- **ServiceMonitor**: Kubernetes custom resources for automatic service discovery
- **Dashboards**: Pre-configured dashboards for different monitoring aspects

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Backend    │    │   Frontend   │    │    Worker    │  │
│  │   Pod        │    │   Pod        │    │    Pod       │  │
│  │              │    │              │    │              │  │
│  │  /metrics    │    │  /metrics    │    │  /metrics    │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│         └───────────────────┼───────────────────┘           │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │   Prometheus    │                      │
│                    │   (Scraping)    │                      │
│                    │   Port: 9090    │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │    Grafana      │                      │
│                    │  (Dashboards)   │                      │
│                    │   Port: 3000    │                      │
│                    └─────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
monitoring/
├── prometheus/
│   ├── namespace.yaml                    # Monitoring namespace
│   ├── prometheus-config.yaml            # Prometheus configuration and recording rules
│   ├── prometheus-deployment.yaml        # Prometheus deployment with RBAC
│   ├── prometheus-service.yaml           # Prometheus service
│   └── servicemonitor.yaml               # ServiceMonitor CRDs for service discovery
├── grafana/
│   ├── grafana-datasource.yaml           # Prometheus datasource configuration
│   ├── grafana-deployment.yaml           # Grafana deployment
│   ├── grafana-service.yaml              # Grafana service
│   ├── grafana-dashboards-configmap.yaml # ConfigMap with all dashboards
│   └── dashboards/
│       ├── application-dashboard.json    # Application metrics dashboard
│       ├── infrastructure-dashboard.json # Infrastructure metrics dashboard
│       ├── kafka-dashboard.json          # Kafka metrics dashboard
│       └── dapr-dashboard.json           # Dapr sidecar metrics dashboard
└── README.md                             # This file
```

---

## Metrics Tracked

### Application Metrics
- **Request Rate**: Requests per second (req/sec)
- **Response Time**: p50, p95, p99 latencies in milliseconds
- **Error Rate**: 4xx and 5xx error percentages
- **HTTP Status Codes**: Distribution of 2xx, 4xx, 5xx responses

### Infrastructure Metrics
- **CPU Usage**: Per pod and cluster-wide (%)
- **Memory Usage**: Per pod and cluster-wide (MB)
- **Network I/O**: Receive/transmit bytes per second
- **Disk I/O**: Read/write bytes per second
- **Pod Health**: Liveness and readiness status

### Kafka Metrics
- **Message Throughput**: Messages per second by topic
- **Bytes Throughput**: Bytes per second by topic
- **Consumer Lag**: Lag by topic and consumer group
- **Partition Distribution**: Partition count by topic
- **Broker Health**: Kafka broker status

### Dapr Metrics
- **Sidecar Health**: Health status of all Dapr sidecars
- **HTTP Request Rate**: Requests per second through Dapr
- **Request Latency**: p95 and p99 latencies
- **Pub/Sub Message Rate**: Ingress and egress message rates
- **Component Status**: Status of Dapr components (Pub/Sub, State, Secrets)
- **State Store Operations**: Operations per second on state store
- **Error Rate**: Dapr sidecar error percentage

---

## Deployment Instructions

### Prerequisites

- Kubernetes cluster (Minikube, AKS, GKE, or OKE)
- kubectl configured and connected to cluster
- Helm 3.x (optional, for alternative deployment)

### Step 1: Create Monitoring Namespace

```bash
kubectl apply -f prometheus/namespace.yaml
```

### Step 2: Deploy Prometheus

```bash
# Apply Prometheus configuration
kubectl apply -f prometheus/prometheus-config.yaml

# Deploy Prometheus with RBAC
kubectl apply -f prometheus/prometheus-deployment.yaml

# Create Prometheus service
kubectl apply -f prometheus/prometheus-service.yaml

# Apply ServiceMonitors (if using Prometheus Operator)
kubectl apply -f prometheus/servicemonitor.yaml
```

### Step 3: Deploy Grafana

```bash
# Apply Grafana datasource configuration
kubectl apply -f grafana/grafana-datasource.yaml

# Deploy Grafana
kubectl apply -f grafana/grafana-deployment.yaml

# Create Grafana service
kubectl apply -f grafana/grafana-service.yaml

# Apply dashboards ConfigMap
kubectl apply -f grafana/grafana-dashboards-configmap.yaml
```

### Step 4: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n monitoring

# Expected output:
# NAME                          READY   STATUS    RESTARTS   AGE
# prometheus-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
# grafana-xxxxxxxxxx-xxxxx      1/1     Running   0          1m

# Check services
kubectl get svc -n monitoring

# Expected output:
# NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
# prometheus   ClusterIP   10.96.xxx.xxx   <none>        9090/TCP   2m
# grafana      ClusterIP   10.96.xxx.xxx   <none>        3000/TCP   1m
```

---

## Accessing Dashboards

### Local Access (Port Forwarding)

#### Prometheus UI

```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

Access Prometheus at: http://localhost:9090

#### Grafana UI

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

Access Grafana at: http://localhost:3000

**Default Credentials:**
- Username: `admin`
- Password: `admin123` (change immediately after first login)

### Cloud Access (Ingress)

For production deployments, configure an Ingress resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: monitoring-ingress
  namespace: monitoring
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - grafana.yourdomain.com
    - prometheus.yourdomain.com
    secretName: monitoring-tls
  rules:
  - host: grafana.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 3000
  - host: prometheus.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: prometheus
            port:
              number: 9090
```

---

## Dashboard Descriptions

### 1. Application Dashboard (todo-app-dashboard)

**Purpose**: Monitor application-level metrics for backend API

**Panels**:
- Request Rate: Total requests per second by service
- Total Request Rate: Gauge showing current request rate
- Error Rate: Percentage of 5xx errors
- Response Time: p50, p95, p99 latencies
- HTTP Status Codes: Distribution of 2xx, 4xx, 5xx responses

**Use Cases**:
- Identify performance bottlenecks
- Monitor error rates and investigate spikes
- Track API response times
- Validate SLA compliance (p95 < 500ms)

### 2. Infrastructure Dashboard (todo-infra-dashboard)

**Purpose**: Monitor Kubernetes infrastructure and resource usage

**Panels**:
- CPU Usage by Pod: CPU percentage per pod
- Memory Usage by Pod: Memory consumption per pod
- Average CPU Usage: Cluster-wide CPU gauge
- Total Memory Usage: Cluster-wide memory gauge
- Network I/O by Pod: Network receive/transmit rates
- Disk I/O by Pod: Disk read/write rates
- Pod Health Status: Liveness/readiness status

**Use Cases**:
- Identify resource-hungry pods
- Plan capacity and scaling
- Detect resource exhaustion
- Monitor pod health

### 3. Kafka Dashboard (todo-kafka-dashboard)

**Purpose**: Monitor Kafka messaging infrastructure

**Panels**:
- Kafka Message Throughput: Messages per second by topic
- Kafka Bytes Throughput: Bytes per second by topic
- Consumer Lag (task-events): Lag for task-events topic
- Consumer Lag (reminders): Lag for reminders topic
- Consumer Lag by Topic and Group: Detailed lag view
- Partition Distribution: Partition count by topic
- Kafka Broker Health: Broker status
- Topic Partition Count: Partition count over time

**Use Cases**:
- Monitor message flow and throughput
- Detect consumer lag issues
- Ensure Kafka broker health
- Validate partition distribution

### 4. Dapr Dashboard (todo-dapr-dashboard)

**Purpose**: Monitor Dapr sidecar health and component status

**Panels**:
- Dapr Sidecar Health Status: Health of all sidecars
- Dapr HTTP Request Rate: Requests per second through Dapr
- Dapr HTTP Request Latency: p95 and p99 latencies
- Dapr Pub/Sub Message Rate (Ingress): Messages published
- Dapr Pub/Sub Message Rate (Egress): Messages consumed
- Dapr Component Status: Status of all Dapr components
- Dapr State Store Operations: State store ops per second
- Dapr Sidecar Error Rate: Error percentage

**Use Cases**:
- Monitor Dapr sidecar health
- Track Pub/Sub message flow
- Validate component connectivity
- Identify Dapr-related issues

---

## Prometheus Configuration

### Scrape Interval

- **Global Scrape Interval**: 15 seconds
- **Scrape Timeout**: 10 seconds
- **Evaluation Interval**: 15 seconds

### Retention

- **Retention Time**: 15 days
- **Storage**: EmptyDir (ephemeral) for local deployments
- **Recommendation**: Use persistent volumes for production

### Scrape Targets

Prometheus automatically discovers and scrapes metrics from:

1. **Kubernetes API Server**: Cluster-level metrics
2. **Kubernetes Nodes**: Node-level metrics
3. **Kubernetes Pods**: Pod-level metrics (with `prometheus.io/scrape: "true"` annotation)
4. **Backend API**: Application metrics on `/metrics` endpoint
5. **Frontend**: Frontend metrics on `/metrics` endpoint
6. **Reminder Worker**: Worker metrics on `/metrics` endpoint
7. **Dapr Sidecars**: Dapr metrics on port 9090
8. **Kafka**: Kafka broker metrics (if JMX exporter is configured)
9. **PostgreSQL**: Database metrics (if postgres-exporter is deployed)

### Recording Rules

Pre-aggregated metrics for faster queries:

- `job:http_requests_total:rate5m`: Request rate per service
- `job:http_requests_errors:rate5m`: Error rate per service
- `job:http_request_duration_seconds:p95`: p95 latency per service
- `job:http_request_duration_seconds:p99`: p99 latency per service
- `pod:cpu_usage:rate5m`: CPU usage per pod
- `pod:memory_usage:bytes`: Memory usage per pod
- `kafka:consumer_lag:sum`: Kafka consumer lag
- `kafka:messages_in:rate5m`: Kafka message rate

---

## Grafana Configuration

### Datasource

- **Name**: Prometheus
- **Type**: Prometheus
- **URL**: http://prometheus:9090
- **Access**: Proxy (through Grafana backend)
- **Default**: Yes

### Security

- **Anonymous Access**: Disabled
- **Admin User**: admin
- **Admin Password**: admin123 (stored in Kubernetes Secret)
- **Recommendation**: Change password immediately after first login

### Dashboard Provisioning

Dashboards are automatically loaded from ConfigMap on startup. Changes to dashboards in the UI are allowed but will be reset on pod restart. For persistent changes, update the JSON files and reapply the ConfigMap.

---

## Troubleshooting

### Prometheus Not Scraping Targets

**Symptoms**: Targets show as "down" in Prometheus UI

**Solutions**:
1. Check pod annotations: `prometheus.io/scrape: "true"`, `prometheus.io/port: "9090"`, `prometheus.io/path: "/metrics"`
2. Verify metrics endpoint is accessible: `kubectl exec -it <pod> -- curl localhost:9090/metrics`
3. Check Prometheus logs: `kubectl logs -n monitoring deployment/prometheus`
4. Verify RBAC permissions: `kubectl get clusterrolebinding prometheus`

### Grafana Dashboards Not Loading

**Symptoms**: Dashboards are empty or show "No data"

**Solutions**:
1. Verify Prometheus datasource is configured: Grafana UI → Configuration → Data Sources
2. Test datasource connection: Click "Test" button in datasource settings
3. Check Grafana logs: `kubectl logs -n monitoring deployment/grafana`
4. Verify ConfigMap is mounted: `kubectl describe pod -n monitoring <grafana-pod>`

### High Memory Usage

**Symptoms**: Prometheus pod is using excessive memory

**Solutions**:
1. Reduce retention time: Change `--storage.tsdb.retention.time=15d` to lower value
2. Reduce scrape frequency: Increase `scrape_interval` in prometheus.yml
3. Increase memory limits: Update `resources.limits.memory` in deployment
4. Use persistent volume: Replace emptyDir with PVC for better performance

### Missing Metrics

**Symptoms**: Some metrics are not appearing in dashboards

**Solutions**:
1. Verify application is exposing metrics: Check `/metrics` endpoint
2. Check metric names: Prometheus UI → Graph → Metrics Explorer
3. Verify ServiceMonitor is created: `kubectl get servicemonitor -n monitoring`
4. Check Prometheus targets: Prometheus UI → Status → Targets

---

## Maintenance

### Updating Dashboards

1. Edit JSON files in `grafana/dashboards/`
2. Regenerate ConfigMap:
   ```bash
   kubectl create configmap grafana-dashboards \
     --from-file=grafana/dashboards/ \
     --namespace=monitoring \
     --dry-run=client -o yaml | kubectl apply -f -
   ```
3. Restart Grafana pod:
   ```bash
   kubectl rollout restart deployment/grafana -n monitoring
   ```

### Updating Prometheus Configuration

1. Edit `prometheus/prometheus-config.yaml`
2. Apply changes:
   ```bash
   kubectl apply -f prometheus/prometheus-config.yaml
   ```
3. Reload Prometheus configuration:
   ```bash
   kubectl exec -n monitoring deployment/prometheus -- \
     curl -X POST http://localhost:9090/-/reload
   ```

### Backup and Restore

#### Backup Prometheus Data

```bash
kubectl exec -n monitoring deployment/prometheus -- \
  tar czf /tmp/prometheus-backup.tar.gz /prometheus

kubectl cp monitoring/<prometheus-pod>:/tmp/prometheus-backup.tar.gz \
  ./prometheus-backup.tar.gz
```

#### Backup Grafana Dashboards

```bash
kubectl get configmap grafana-dashboards -n monitoring -o yaml > \
  grafana-dashboards-backup.yaml
```

---

## Performance Tuning

### Prometheus

- **Scrape Interval**: Balance between data granularity and resource usage
- **Retention**: Longer retention requires more storage
- **Recording Rules**: Pre-aggregate frequently used queries
- **Remote Write**: Send data to long-term storage (Thanos, Cortex)

### Grafana

- **Query Caching**: Enable query result caching for better performance
- **Dashboard Variables**: Use variables for dynamic filtering
- **Panel Refresh**: Set appropriate refresh intervals (10s-30s)
- **Alerting**: Configure alert rules in Prometheus, not Grafana

---

## Integration with CI/CD

The monitoring stack integrates with the CI/CD pipeline (T5.6.1) for:

- **Deployment Validation**: Health checks after deployment
- **Performance Testing**: Baseline metrics comparison
- **Alerting**: Notifications on deployment issues
- **Rollback Triggers**: Automatic rollback on metric thresholds

See `.github/workflows/deploy.yml` for CI/CD integration details.

---

## Next Steps (T5.6.3 and T5.6.4)

### T5.6.3: Configure Logging

- Deploy Loki for log aggregation
- Configure Promtail for log collection
- Add log panels to Grafana dashboards

### T5.6.4: Setup Alerting Rules

- Define alert rules in Prometheus
- Configure Alertmanager
- Setup notification channels (email, Slack, Discord)
- Test alert firing and resolution

---

## References

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **Prometheus Operator**: https://prometheus-operator.dev/
- **Kubernetes Monitoring**: https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/
- **Dapr Observability**: https://docs.dapr.io/operations/observability/

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Prometheus and Grafana logs
3. Consult phase5-spec.md and constitution.md v5.0
4. Open an issue in the project repository

---

**Generated by**: cicd-monitoring-agent
**Task**: T5.6.2 - Setup Prometheus and Grafana
**Date**: 2026-02-15
**Constitution**: v5.0 compliant
**Phase**: 5 - Advanced Cloud Deployment
