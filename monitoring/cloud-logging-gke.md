# GKE Cloud Logging Setup Guide
## Task: T5.6.3 - Cloud Logging for Google Kubernetes Engine

**Version:** 1.0
**Date:** 2026-02-15
**Based on:** constitution.md v5.0, phase5-spec.md v1.0

---

## Overview

This guide provides instructions for setting up centralized logging using Google Cloud Logging (formerly Stackdriver) for GKE (Google Kubernetes Engine) deployments. Cloud Logging provides a cloud-native alternative to self-hosted Loki for production workloads.

### Architecture

```
GKE Pods → Logging Agent (Fluentd/Fluent Bit) → Cloud Logging → Cloud Console / Grafana
```

### Benefits

- **Fully Managed**: No infrastructure to maintain
- **Auto-Enabled**: Logging enabled by default on GKE
- **Scalable**: Handles high log volumes automatically
- **Integrated**: Native integration with Google Cloud Operations
- **Advanced Features**: Log-based metrics, log sinks, log router
- **Cost Effective**: 50 GB/month free tier per project

---

## Prerequisites

- Google Cloud account with active project
- GKE cluster deployed
- gcloud CLI installed and configured
- kubectl configured for GKE cluster
- Editor or Owner role on project

---

## Step 1: Verify Cloud Logging is Enabled

### Check GKE Cluster Configuration

Cloud Logging is enabled by default on GKE clusters. Verify:

```bash
# Set variables
PROJECT_ID="your-project-id"
CLUSTER_NAME="todo-cluster"
ZONE="us-central1-a"

# Get cluster info
gcloud container clusters describe $CLUSTER_NAME \
  --zone=$ZONE \
  --project=$PROJECT_ID \
  --format="value(loggingService)"

# Expected output: logging.googleapis.com/kubernetes
```

### Enable Cloud Logging (if disabled)

```bash
# Enable Cloud Logging on existing cluster
gcloud container clusters update $CLUSTER_NAME \
  --zone=$ZONE \
  --logging=SYSTEM,WORKLOAD

# Verify logging agent pods
kubectl get pods -n kube-system | grep fluentbit
```

### For New GKE Cluster

```bash
# Create GKE cluster with Cloud Logging enabled
gcloud container clusters create $CLUSTER_NAME \
  --zone=$ZONE \
  --num-nodes=3 \
  --logging=SYSTEM,WORKLOAD \
  --monitoring=SYSTEM \
  --enable-cloud-logging \
  --enable-cloud-monitoring
```

---

## Step 2: Configure Log Collection

### Default Log Collection

GKE automatically collects:
- **Container logs**: stdout/stderr from all containers
- **System logs**: Kubernetes system components
- **Audit logs**: Kubernetes API audit logs (if enabled)
- **Node logs**: System logs from nodes

### Customize Log Collection

Create a ConfigMap to filter logs:

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentbit-gke-config
  namespace: kube-system
data:
  filter.conf: |
    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_URL            https://kubernetes.default.svc:443
        Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
        Kube_Tag_Prefix     kube.var.log.containers.
        Merge_Log           On
        Keep_Log            Off
        K8S-Logging.Parser  On
        K8S-Logging.Exclude On
        Labels              On
        Annotations         Off

    [FILTER]
        Name                grep
        Match               kube.*
        Exclude             log health|readiness

    [FILTER]
        Name                nest
        Match               kube.*
        Operation           lift
        Nested_under        kubernetes
        Add_prefix          k8s_
EOF
```

---

## Step 3: Query Logs in Cloud Console

### Access Cloud Logging

1. Navigate to Google Cloud Console: https://console.cloud.google.com
2. Select your project
3. Navigate to "Logging" → "Logs Explorer"

### Example Log Queries

**All logs from todo-app namespace:**

```
resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
```

**Error logs only:**

```
resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
severity>=ERROR
```

**Logs from specific pod:**

```
resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
resource.labels.pod_name=~"backend-.*"
```

**Logs with specific text:**

```
resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
textPayload=~"task created"
```

**JSON logs with specific field:**

```
resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
jsonPayload.level="ERROR"
```

**Logs from last hour:**

```
resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
timestamp>="2026-02-15T10:00:00Z"
```

---

## Step 4: Create Log-Based Metrics

Log-based metrics allow you to create metrics from log entries for monitoring and alerting.

### Create Counter Metric for Errors

```bash
# Create log-based metric
gcloud logging metrics create error_count \
  --description="Count of error logs" \
  --log-filter='resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
severity>=ERROR'

# Verify metric
gcloud logging metrics describe error_count
```

### Create Distribution Metric for Response Times

```bash
# Create distribution metric
gcloud logging metrics create response_time_distribution \
  --description="Distribution of response times" \
  --log-filter='resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
jsonPayload.response_time>0' \
  --value-extractor='EXTRACT(jsonPayload.response_time)' \
  --metric-kind=DELTA \
  --value-type=DISTRIBUTION
```

---

## Step 5: Create Log Sinks

Log sinks export logs to external destinations for long-term storage or analysis.

### Export Logs to Cloud Storage (Archive)

```bash
# Create Cloud Storage bucket
BUCKET_NAME="${PROJECT_ID}-logs-archive"
gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME

# Create log sink
gcloud logging sinks create todo-app-archive \
  gs://$BUCKET_NAME \
  --log-filter='resource.type="k8s_container"
resource.labels.namespace_name="todo-app"'

# Grant sink permission to write to bucket
SERVICE_ACCOUNT=$(gcloud logging sinks describe todo-app-archive --format='value(writerIdentity)')
gsutil iam ch ${SERVICE_ACCOUNT}:objectCreator gs://$BUCKET_NAME
```

### Export Logs to BigQuery (Analytics)

```bash
# Create BigQuery dataset
bq mk --dataset --location=US ${PROJECT_ID}:todo_app_logs

# Create log sink
gcloud logging sinks create todo-app-bigquery \
  bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/todo_app_logs \
  --log-filter='resource.type="k8s_container"
resource.labels.namespace_name="todo-app"'

# Grant sink permission
SERVICE_ACCOUNT=$(gcloud logging sinks describe todo-app-bigquery --format='value(writerIdentity)')
bq add-iam-policy-binding \
  --member=${SERVICE_ACCOUNT} \
  --role=roles/bigquery.dataEditor \
  ${PROJECT_ID}:todo_app_logs
```

### Export Logs to Pub/Sub (Real-time Processing)

```bash
# Create Pub/Sub topic
gcloud pubsub topics create todo-app-logs

# Create log sink
gcloud logging sinks create todo-app-pubsub \
  pubsub.googleapis.com/projects/${PROJECT_ID}/topics/todo-app-logs \
  --log-filter='resource.type="k8s_container"
resource.labels.namespace_name="todo-app"
severity>=ERROR'

# Grant sink permission
SERVICE_ACCOUNT=$(gcloud logging sinks describe todo-app-pubsub --format='value(writerIdentity)')
gcloud pubsub topics add-iam-policy-binding todo-app-logs \
  --member=${SERVICE_ACCOUNT} \
  --role=roles/pubsub.publisher
```

---

## Step 6: Create Log-Based Alerts

### Create Alert for High Error Rate

```bash
# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 10/min" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=300s \
  --condition-filter='resource.type="k8s_container"
metric.type="logging.googleapis.com/user/error_count"
resource.labels.namespace_name="todo-app"'
```

### Create Notification Channel

```bash
# Create email notification channel
gcloud alpha monitoring channels create \
  --display-name="Admin Email" \
  --type=email \
  --channel-labels=email_address=admin@example.com

# List channels to get ID
gcloud alpha monitoring channels list
```

---

## Step 7: Integrate with Grafana

### Option 1: Cloud Monitoring Datasource

Add Google Cloud Monitoring datasource in Grafana:

1. Navigate to Grafana → Configuration → Data Sources
2. Click "Add data source"
3. Select "Google Cloud Monitoring"
4. Configure:
   - **Authentication**: GCE Default Service Account or JWT
   - **Default Project**: Select your project
5. Click "Save & Test"

### Option 2: Use Loki with Cloud Logging

Export logs from Cloud Logging to Loki:

```bash
# Deploy log forwarder
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudlogging-to-loki
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cloudlogging-to-loki
  template:
    metadata:
      labels:
        app: cloudlogging-to-loki
    spec:
      containers:
      - name: forwarder
        image: gcr.io/google.com/cloudsdktool/cloud-sdk:slim
        command:
        - /bin/bash
        - -c
        - |
          while true; do
            gcloud logging read "resource.type=k8s_container" \
              --format=json \
              --limit=100 | \
            curl -X POST http://loki:3100/loki/api/v1/push \
              -H "Content-Type: application/json" \
              -d @-
            sleep 60
          done
EOF
```

---

## Step 8: Query Logs with gcloud CLI

### Basic Queries

```bash
# View recent logs
gcloud logging read "resource.type=k8s_container
resource.labels.namespace_name=todo-app" \
  --limit=50 \
  --format=json

# View error logs
gcloud logging read "resource.type=k8s_container
resource.labels.namespace_name=todo-app
severity>=ERROR" \
  --limit=20

# Follow logs in real-time
gcloud logging tail "resource.type=k8s_container
resource.labels.namespace_name=todo-app"

# Export logs to file
gcloud logging read "resource.type=k8s_container
resource.labels.namespace_name=todo-app" \
  --format=json > logs.json
```

---

## Step 9: Structured Logging Best Practices

### Use JSON Logging in Applications

**Node.js Example:**

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [
    new winston.transports.Console()
  ]
});

logger.info('Task created', {
  task_id: '123',
  user_id: '456',
  trace_id: 'abc-def-ghi'
});
```

**Python Example:**

```python
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'trace_id': getattr(record, 'trace_id', None)
        }
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger()
logger.addHandler(handler)

logger.info('Task created', extra={'trace_id': 'abc-def-ghi'})
```

### Add Trace Context

Link logs to traces for distributed tracing:

```javascript
// Add trace context to logs
const traceHeader = req.headers['x-cloud-trace-context'];
const [traceId, spanId] = traceHeader.split('/');

logger.info('Processing request', {
  'logging.googleapis.com/trace': `projects/${projectId}/traces/${traceId}`,
  'logging.googleapis.com/spanId': spanId
});
```

---

## Cost Optimization

### Free Tier

Google Cloud Logging includes:
- **50 GB/month free** per project
- **30 days retention** included

### Cost Reduction Tips

1. **Exclude verbose logs:**
   ```bash
   # Create exclusion filter
   gcloud logging exclusions create exclude-health-checks \
     --log-filter='resource.type="k8s_container"
   textPayload=~"health|readiness"'
   ```

2. **Reduce retention for non-critical logs:**
   ```bash
   # Set custom retention (1-3650 days)
   gcloud logging buckets update _Default \
     --location=global \
     --retention-days=30
   ```

3. **Use log sampling:**
   ```bash
   # Sample 10% of logs
   gcloud logging exclusions create sample-logs \
     --log-filter='resource.type="k8s_container"
   sample(insertId, 0.1)'
   ```

4. **Archive to Cloud Storage:**
   - Cloud Logging: $0.50/GB after free tier
   - Cloud Storage: $0.02/GB/month (Nearline)
   - Cloud Storage: $0.004/GB/month (Coldline)

5. **Monitor usage:**
   ```bash
   # Check log ingestion volume
   gcloud logging metrics list --filter="name:byte_count"
   ```

### Estimated Costs

For a small application (3 pods, moderate logging):
- **Log ingestion**: ~10-20 GB/month (within free tier)
- **Log retention**: 30 days (free)
- **Total cost**: $0/month (if under 50GB)

For larger applications:
- **Log ingestion**: $0.50/GB after free tier
- **Log retention**: Included for 30 days
- **Archive storage**: $0.02/GB/month (Nearline)

---

## Troubleshooting

### Logs Not Appearing

1. **Check logging agent status:**
   ```bash
   kubectl get pods -n kube-system | grep fluentbit
   kubectl logs -n kube-system -l k8s-app=fluentbit-gke
   ```

2. **Verify logging is enabled:**
   ```bash
   gcloud container clusters describe $CLUSTER_NAME \
     --zone=$ZONE \
     --format="value(loggingService)"
   ```

3. **Check IAM permissions:**
   ```bash
   # Verify service account has logging.logWriter role
   gcloud projects get-iam-policy $PROJECT_ID \
     --flatten="bindings[].members" \
     --filter="bindings.role:roles/logging.logWriter"
   ```

### High Costs

1. **Identify high-volume sources:**
   ```bash
   # Query log volume by resource
   gcloud logging read "timestamp>=2026-02-01" \
     --format="table(resource.type, count())" \
     --limit=1000 | sort | uniq -c | sort -rn
   ```

2. **Create exclusion filters** for noisy logs

3. **Reduce log verbosity** in application code

---

## Migration from Loki to Cloud Logging

If migrating from self-hosted Loki:

1. **Enable Cloud Logging** on GKE cluster
2. **Keep both running** during transition period
3. **Update dashboards** to use Cloud Monitoring datasource
4. **Migrate alert rules** to Cloud Monitoring
5. **Test queries** to ensure equivalents work
6. **Decommission Loki** after validation period

---

## Advanced Features

### Log Router

Route logs to multiple destinations:

```bash
# Route error logs to Pub/Sub for real-time alerts
gcloud logging sinks create error-alerts \
  pubsub.googleapis.com/projects/${PROJECT_ID}/topics/error-alerts \
  --log-filter='severity>=ERROR'

# Route all logs to BigQuery for analytics
gcloud logging sinks create all-logs-bigquery \
  bigquery.googleapis.com/projects/${PROJECT_ID}/datasets/all_logs
```

### Log Analytics

Query logs with SQL in BigQuery:

```sql
-- Top 10 error messages
SELECT
  jsonPayload.message,
  COUNT(*) as count
FROM `project.dataset.table`
WHERE severity = 'ERROR'
GROUP BY jsonPayload.message
ORDER BY count DESC
LIMIT 10;

-- Error rate by hour
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
  COUNT(*) as error_count
FROM `project.dataset.table`
WHERE severity = 'ERROR'
GROUP BY hour
ORDER BY hour DESC;
```

---

## References

- Cloud Logging Documentation: https://cloud.google.com/logging/docs
- GKE Logging: https://cloud.google.com/kubernetes-engine/docs/how-to/logging
- Log Query Language: https://cloud.google.com/logging/docs/view/logging-query-language
- Cloud Logging Pricing: https://cloud.google.com/stackdriver/pricing

---

**END OF GKE CLOUD LOGGING SETUP GUIDE**
