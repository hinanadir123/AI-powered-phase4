# Monitoring and Observability Setup Documentation

## Overview
This document provides comprehensive details about the monitoring and observability setup for the Todo AI Chatbot application deployed on Oracle OKE.

## Architecture

The monitoring stack follows a cloud-native, service-oriented architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     Grafana     │    │   Prometheus     │    │  Alertmanager   │
│   (Visualize)   │←──→│   (Collect &    │←──→│  (Alerting &   │
│                 │    │   Store)        │    │   Routing)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ↑                        ↑                       ↑
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Kubernetes   │    │  Application &   │    │   Notification  │
│   (Data Source) │    │    Dapr Metrics │    │  Integrations   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Components

### 1. Prometheus
**Purpose**: Metrics collection, storage, and querying engine

**Configuration Highlights**:
- Scraping Kubernetes components (apiserver, cAdvisor, kube-state-metrics)
- Application metrics from Todo AI Chatbot services
- Dapr sidecar metrics with custom app ID labeling
- Node-level infrastructure metrics via node-exporter
- Kafka cluster metrics (when available via external configuration)

**Custom Alert Rules**:
- `HighErrorRate`: Triggers when error rate exceeds 5% for 5 minutes
- `HighRequestLatency`: Alerts on p95 response time above 1 second for 5 minutes
- `LowRequestRate`: Critical alert for 0 traffic for 2+ minutes
- `HighCPUUsage`: Warning on >80% CPU usage for 10 minutes
- `HighMemoryUsage`: Warning on >90% memory usage for 5 minutes
- `KafkaHighConsumerLag`: Warning when consumer lag exceeds 1000 messages
- `DaprSidecarDown`: Critical alert when Dapr sidecar is unresponsive
- `HighDaprAPILatency`: Warning on p95 Dapr API latency above 1 second

### 2. Grafana
**Purpose**: Dashboard visualization and alerting

**Provisioned Dashboards**:
- Application Dashboard: Request rate, latency, error rate, active tasks
- Infrastructure Dashboard: CPU, memory, pod status, restart rates
- Kafka Dashboard: Message rates, consumer lag, topic statistics
- Dapr Dashboard: API request rates, durations, state operations, pubsub metrics

**Datasource Configuration**:
- Prometheus as primary data source
- Automatic provisioning via ConfigMap
- Pre-configured panel templates
- Alert channel integration

### 3. Alertmanager
**Purpose**: Alert notification routing and deduplication

**Configuration Features**:
- Grouping alerts by alert name and priority
- 10s group wait and interval for deduplication
- Routing based on alert severity and type
- Multiple notification channels (email, Slack, Discord)

**Routing Strategy**:
- `default-receiver`: General alerts to default email
- `critical-team`: High severity alerts (CPU down, services not available)
- `dev-team`: Infrastructure alerts (CPU, memory thresholds)
- `kafka-team`: Kafka-specific alerts and performance issues

### 4. Loki
**Purpose**: Log aggregation and storage

**Integration**:
- Works alongside Prometheus for unified monitoring
- Stores logs with labels for efficient querying
- Complementary to metric-based alerting

### 5. Jaeger (Distributed Tracing)
**Purpose**: Distributed request tracing across services

**Functionality**:
- Visualizing request paths in microservices
- Identifying performance bottlenecks
- Service-to-service communication traces
- Dapr-to-Dapr communication tracing

## Dapr Monitoring Integration

### Metrics Exported
Dapr automatically provides several categories of metrics:

- **HTTP metrics**: Request rates, durations, and errors
- **gRPC metrics**: Dapr API call metrics
- **Actor metrics**: For any actor patterns used
- **Pub/Sub metrics**: Message counts and timing
- **State management metrics**: Operation counts and timing
- **Service invocation metrics**: Cross-service communication metrics

### Configuration Applied
The Dapr configuration enables comprehensive monitoring:

```yaml
tracing:
  samplingRate: "1"
  zipkin:
    endpointAddress: "http://jaeger:9411/api/v1/spans"
metric:
  enabled: true
logging:
  level: "info"
```

## Kubernetes-Specific Monitoring

### Custom Resource Monitoring
- Kubernetes API server metrics
- Pod lifecycle monitoring
- Service, deployment, and HPA metrics
- Resource usage and limits

### Infrastructure Metrics
- Node resource usage (CPU, memory, disk I/O)
- Network I/O and bandwidth usage
- Storage latency and throughput
- Scheduling metrics

## Application Health Checks

### HTTP Metrics Setup
Application containers must expose appropriate metrics for collection:
```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/path: "/metrics"
    prometheus.io/port: "8000"
```

### Custom Application Metrics
- Task creation and update rates
- Reminder scheduling and processing rates
- Database operation performance
- Kafka message processing latencies

## Security Considerations

### RBAC Configuration
- Minimal required permissions for prometheus service account
- ClusterRole for node and pod access
- Secret management for sensitive configurations
- Network policies restricting access

### Data Protection
- TLS encryption for metrics transmission
- Authentication for dashboard access
- Encrypted storage for sensitive alert routing configurations
- Audit logging for configuration changes

## Performance and Resource Allocation

### Resource Constraints (for Always Free tier)
- Prometheus: 300m CPU limit, 400Mi memory limit
- Grafana: 200m CPU limit, 256Mi memory limit
- Alertmanager: 50m CPU limit, 128Mi memory limit
- Loki: Optimized for non-persistent scenarios
- Jaeger: Memory-only storage for minimal resource usage

### Scaling Considerations
- Prometheus federated setup possible for cluster metrics
- HA configurations available for production workloads
- Long-term storage options via remote write
- Multiple Grafana replicas for high availability

## Alert Configuration

### Severity Levels
- **Critical**: System down, data loss risk
- **Warning**: Performance degradation, elevated metrics
- **Info**: Informational status updates

### Alert Routing Logic
1. Alerts are grouped by common labels
2. Deduplicated within group wait period
3. Routed to appropriate teams based on rules
4. Escalated with repeat intervals
5. Resolved with clear status reporting

## Integration Endpoints

### Prometheus
- `http://<prometheus-ip>:9090`: Web UI and API
- `http://<prometheus-ip>:9090/graph`: Expression browser
- `http://<prometheus-ip>:9090/rules`: Rule status
- `http://<prometheus-ip>:9090/alerts`: Active alerts

### Grafana
- `http://<grafana-ip>:3000`: Dashboard UI
- Default credentials controlled via secrets

### Alertmanager
- `http://<alertmanager-ip>:9093`: Web UI
- Receives alerts from Prometheus based on rule firing

## Troubleshooting Monitoring

### Common Issues
1. **Metrics aren't scraping**
   - Verify Prometheus discovery configuration
   - Check pod annotations for scraping hints
   - Confirm network connectivity between Prometheus and targets

2. **Alerts aren't firing**
   - Validate alert rule syntax
   - Check Prometheus rule evaluation
   - Confirm Alertmanager routing configuration

3. **Grafana dashboards are empty**
   - Verify Grafana Prometheus data source
   - Check that data source name matches configuration
   - Ensure Prometheus has collected metrics

4. **High resource usage**
   - Tune Prometheus retention policies
   - Optimize recording rule queries
   - Adjust service resource limits based on actual usage

### Diagnostic Commands
```bash
# Check prometheus targets
kubectl get --raw /api/v1/nodes/<node>/proxy/metrics

# Check prometheus configuration
kubectl get configmaps prometheus-server-config -o yaml

# Check grafana logs for errors
kubectl logs -l app=grafana

# Check prometheus rule evaluation
kubectl logs -l app=prometheus-server | grep -i error
```

## Best Practices

### Dashboard Design
- Use consistent naming conventions
- Group related metrics together
- Include appropriate time ranges
- Provide actionable information

### Alert Management
- Keep alerts actionable
- Minimize alert fatigue with proper grouping
- Regular evaluation and pruning of stale alerts
- Clear documentation for each alert purpose

### Metrics Collection
- Export business metrics from applications
- Use appropriate metric types (counter, gauge, histogram)
- Apply proper labels for dimensionality
- Retain only necessary historical data

This monitoring setup provides comprehensive observability for the Todo AI Chatbot deployment, enabling proactive detection and resolution of issues while staying within Oracle OKE Always Free tier limits.