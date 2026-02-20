# Azure Log Analytics Setup Guide
## Task: T5.6.3 - Cloud Logging for Azure AKS

**Version:** 1.0
**Date:** 2026-02-15
**Based on:** constitution.md v5.0, phase5-spec.md v1.0

---

## Overview

This guide provides instructions for setting up centralized logging using Azure Log Analytics and Container Insights for AKS (Azure Kubernetes Service) deployments. Azure Log Analytics provides a cloud-native alternative to self-hosted Loki for production workloads.

### Architecture

```
AKS Pods → Container Insights Agent → Log Analytics Workspace → Azure Portal / Grafana
```

### Benefits

- **Fully Managed**: No infrastructure to maintain
- **Scalable**: Handles high log volumes automatically
- **Integrated**: Native integration with Azure Monitor and AKS
- **Advanced Analytics**: KQL (Kusto Query Language) for powerful queries
- **Cost Effective**: Pay-as-you-go pricing with free tier

---

## Prerequisites

- Azure account with active subscription
- AKS cluster deployed
- Azure CLI installed and configured
- kubectl configured for AKS cluster
- Contributor or Owner role on subscription

---

## Step 1: Create Log Analytics Workspace

### Using Azure Portal

1. Navigate to Azure Portal: https://portal.azure.com
2. Search for "Log Analytics workspaces"
3. Click "Create"
4. Fill in details:
   - **Subscription**: Select your subscription
   - **Resource Group**: Use existing or create new (e.g., `todo-app-rg`)
   - **Name**: `todo-app-logs`
   - **Region**: Same as AKS cluster (e.g., `East US`)
   - **Pricing Tier**: Pay-as-you-go (includes 5GB free per month)
5. Click "Review + Create" → "Create"

### Using Azure CLI

```bash
# Set variables
RESOURCE_GROUP="todo-app-rg"
LOCATION="eastus"
WORKSPACE_NAME="todo-app-logs"

# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group $RESOURCE_GROUP \
  --workspace-name $WORKSPACE_NAME \
  --location $LOCATION \
  --sku PerGB2018

# Get workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group $RESOURCE_GROUP \
  --workspace-name $WORKSPACE_NAME \
  --query id -o tsv)

echo "Workspace ID: $WORKSPACE_ID"
```

---

## Step 2: Enable Container Insights on AKS

### For Existing AKS Cluster

```bash
# Set variables
AKS_CLUSTER_NAME="todo-cluster"
RESOURCE_GROUP="todo-app-rg"

# Enable Container Insights
az aks enable-addons \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME \
  --addons monitoring \
  --workspace-resource-id $WORKSPACE_ID

# Verify addon is enabled
az aks show \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME \
  --query addonProfiles.omsagent
```

### For New AKS Cluster

```bash
# Create AKS cluster with Container Insights enabled
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME \
  --node-count 3 \
  --enable-addons monitoring \
  --workspace-resource-id $WORKSPACE_ID \
  --generate-ssh-keys
```

---

## Step 3: Verify Container Insights Deployment

Check that the monitoring agent is running:

```bash
# Get AKS credentials
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER_NAME

# Check omsagent pods
kubectl get pods -n kube-system | grep omsagent

# Expected output:
# omsagent-xxxxx          1/1     Running   0          5m
# omsagent-rs-xxxxxxxxx   1/1     Running   0          5m
```

Check agent logs:

```bash
kubectl logs -n kube-system -l component=oms-agent --tail=50
```

---

## Step 4: Configure Log Collection

### Configure Data Collection Rules

By default, Container Insights collects:
- Container logs (stdout/stderr)
- Performance metrics (CPU, memory, disk, network)
- Kubernetes events

To customize collection, create a ConfigMap:

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: container-azm-ms-agentconfig
  namespace: kube-system
data:
  schema-version: v1
  config-version: ver1
  log-data-collection-settings: |-
    [log_collection_settings]
       [log_collection_settings.stdout]
          enabled = true
          exclude_namespaces = ["kube-system", "kube-public"]
       [log_collection_settings.stderr]
          enabled = true
          exclude_namespaces = ["kube-system", "kube-public"]
       [log_collection_settings.env_var]
          enabled = true
       [log_collection_settings.enrich_container_logs]
          enabled = true
       [log_collection_settings.collect_all_kube_events]
          enabled = false
  prometheus-data-collection-settings: |-
    [prometheus_data_collection_settings.cluster]
        interval = "1m"
        monitor_kubernetes_pods = true
    [prometheus_data_collection_settings.node]
        interval = "1m"
EOF
```

Restart omsagent to apply changes:

```bash
kubectl rollout restart daemonset/omsagent -n kube-system
kubectl rollout restart deployment/omsagent-rs -n kube-system
```

---

## Step 5: Query Logs with KQL

### Access Log Analytics

1. Navigate to Azure Portal
2. Go to your Log Analytics workspace (`todo-app-logs`)
3. Click "Logs" in the left menu

### Example KQL Queries

**All container logs from todo-app namespace:**

```kql
ContainerLog
| where Namespace == "todo-app"
| project TimeGenerated, ContainerName, LogEntry
| order by TimeGenerated desc
| take 100
```

**Error logs only:**

```kql
ContainerLog
| where Namespace == "todo-app"
| where LogEntry contains "ERROR" or LogEntry contains "error"
| project TimeGenerated, ContainerName, LogEntry
| order by TimeGenerated desc
```

**Logs from specific pod:**

```kql
ContainerLog
| where Namespace == "todo-app"
| where Name contains "backend"
| project TimeGenerated, Name, LogEntry
| order by TimeGenerated desc
| take 50
```

**Log count by container:**

```kql
ContainerLog
| where Namespace == "todo-app"
| summarize Count=count() by ContainerName
| order by Count desc
```

**Error rate over time:**

```kql
ContainerLog
| where Namespace == "todo-app"
| where LogEntry contains "ERROR"
| summarize ErrorCount=count() by bin(TimeGenerated, 5m)
| render timechart
```

**Logs with specific trace ID:**

```kql
ContainerLog
| where Namespace == "todo-app"
| where LogEntry contains "trace_id=abc123"
| project TimeGenerated, ContainerName, LogEntry
| order by TimeGenerated desc
```

---

## Step 6: Create Log Alerts

### Create Alert Rule for High Error Rate

```bash
# Set variables
ALERT_NAME="HighErrorRate"
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group $RESOURCE_GROUP \
  --workspace-name $WORKSPACE_NAME \
  --query id -o tsv)

# Create alert rule
az monitor scheduled-query create \
  --name $ALERT_NAME \
  --resource-group $RESOURCE_GROUP \
  --scopes $WORKSPACE_ID \
  --condition "count 'Heartbeat' > 5" \
  --condition-query "ContainerLog | where Namespace == 'todo-app' | where LogEntry contains 'ERROR' | summarize ErrorCount=count() by bin(TimeGenerated, 5m)" \
  --description "Alert when error rate exceeds threshold" \
  --evaluation-frequency 5m \
  --window-size 5m \
  --severity 2
```

### Configure Action Group for Notifications

```bash
# Create action group for email notifications
az monitor action-group create \
  --name "TodoAppAlerts" \
  --resource-group $RESOURCE_GROUP \
  --short-name "TodoAlerts" \
  --email-receiver name="Admin" email-address="admin@example.com"
```

---

## Step 7: Integrate with Grafana

### Option 1: Azure Managed Grafana

```bash
# Create Azure Managed Grafana instance
az grafana create \
  --name "todo-app-grafana" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Link to Log Analytics workspace
az grafana data-source create \
  --name "todo-app-grafana" \
  --resource-group $RESOURCE_GROUP \
  --definition '{
    "type": "grafana-azure-monitor-datasource",
    "access": "proxy",
    "jsonData": {
      "subscriptionId": "'$SUBSCRIPTION_ID'",
      "logAnalyticsDefaultWorkspace": "'$WORKSPACE_ID'"
    }
  }'
```

### Option 2: Self-Hosted Grafana

Add Azure Monitor datasource in Grafana:

1. Navigate to Grafana → Configuration → Data Sources
2. Click "Add data source"
3. Select "Azure Monitor"
4. Configure:
   - **Authentication**: Managed Identity or Service Principal
   - **Subscription**: Select your subscription
   - **Default Workspace**: Select `todo-app-logs`
5. Click "Save & Test"

---

## Step 8: Create Dashboards

### Import Pre-Built Dashboards

Azure provides pre-built dashboards for Container Insights:

1. Navigate to AKS cluster in Azure Portal
2. Click "Insights" in the left menu
3. Explore pre-built views:
   - **Cluster**: Overall cluster health
   - **Nodes**: Node-level metrics
   - **Controllers**: Deployment/StatefulSet metrics
   - **Containers**: Container-level metrics
   - **Logs**: Log explorer

### Create Custom Dashboard

In Log Analytics workspace:

1. Click "Dashboards" → "New dashboard"
2. Add tiles with KQL queries
3. Example tiles:
   - Error rate chart
   - Log volume by container
   - Top error messages
   - Response time percentiles

---

## Cost Optimization

### Free Tier

Azure Log Analytics includes:
- **5 GB/month free** data ingestion
- **31 days retention** included

### Cost Reduction Tips

1. **Filter unnecessary logs:**
   ```yaml
   exclude_namespaces = ["kube-system", "kube-public"]
   ```

2. **Reduce retention for non-critical logs:**
   ```bash
   az monitor log-analytics workspace table update \
     --resource-group $RESOURCE_GROUP \
     --workspace-name $WORKSPACE_NAME \
     --name ContainerLog \
     --retention-time 30
   ```

3. **Use sampling for high-volume logs:**
   ```kql
   ContainerLog
   | where rand() < 0.1  // Sample 10% of logs
   ```

4. **Archive old logs to storage:**
   ```bash
   # Export logs to Azure Storage (cheaper long-term storage)
   az monitor log-analytics workspace data-export create \
     --resource-group $RESOURCE_GROUP \
     --workspace-name $WORKSPACE_NAME \
     --name "archive-logs" \
     --destination "storage-account-id" \
     --table-names ContainerLog
   ```

5. **Monitor costs:**
   ```bash
   # Check data ingestion volume
   az monitor log-analytics workspace show \
     --resource-group $RESOURCE_GROUP \
     --workspace-name $WORKSPACE_NAME \
     --query "retentionInDays"
   ```

### Estimated Costs

For a small application (3 pods, moderate logging):
- **Data ingestion**: ~2-3 GB/month (within free tier)
- **Data retention**: 31 days (free)
- **Total cost**: $0/month (if under 5GB)

For larger applications:
- **Data ingestion**: $2.30/GB after free tier
- **Data retention**: $0.10/GB/month after 31 days

---

## Troubleshooting

### Logs Not Appearing

1. **Check omsagent status:**
   ```bash
   kubectl get pods -n kube-system -l component=oms-agent
   kubectl logs -n kube-system -l component=oms-agent
   ```

2. **Verify workspace connection:**
   ```bash
   kubectl get configmap -n kube-system omsagent-rs-config -o yaml
   ```

3. **Check data ingestion:**
   ```kql
   Heartbeat
   | where TimeGenerated > ago(5m)
   | summarize count() by Computer
   ```

### High Costs

1. **Identify high-volume sources:**
   ```kql
   Usage
   | where TimeGenerated > ago(7d)
   | where IsBillable == true
   | summarize DataVolume=sum(Quantity) by DataType
   | order by DataVolume desc
   ```

2. **Reduce log verbosity** in application code

3. **Filter out noisy logs** in ConfigMap

---

## Migration from Loki to Azure Log Analytics

If migrating from self-hosted Loki:

1. **Keep both running** during transition period
2. **Update application logging** to use structured logs (JSON)
3. **Migrate dashboards** from Grafana to Azure Portal or Azure Managed Grafana
4. **Update alert rules** from Prometheus to Azure Monitor
5. **Test queries** to ensure KQL equivalents work
6. **Decommission Loki** after validation period

---

## References

- Azure Monitor Documentation: https://docs.microsoft.com/azure/azure-monitor/
- Container Insights: https://docs.microsoft.com/azure/azure-monitor/containers/container-insights-overview
- KQL Reference: https://docs.microsoft.com/azure/data-explorer/kusto/query/
- Azure Monitor Pricing: https://azure.microsoft.com/pricing/details/monitor/

---

**END OF AZURE LOG ANALYTICS SETUP GUIDE**
