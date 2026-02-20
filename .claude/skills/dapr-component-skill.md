# Dapr Component Skill v1

Generate valid Dapr component YAML files for Phase 5 Todo AI Chatbot.

## Usage

```
/dapr-component [type] [name]
```

### Examples
- "Generate pubsub.kafka for task-events topic"
- "Create state.postgresql component for todo-state"
- "Generate jobs.dapr for reminder-scheduler"
- "Create secretstores.kubernetes for api-keys"

## Instructions

When generating Dapr components:
1. **Output only valid YAML** - no explanations in the YAML file
2. **Always include metadata.name** - use descriptive names
3. **Use placeholders** - never hard-code sensitive values
4. **Add retries and dead-letter queues** where applicable
5. **Include scopes** to limit component access to specific apps
6. **Use dapr.io/v1alpha1** API version consistently

## Strict Rules

- ✅ API Version: Always use `dapr.io/v1alpha1`
- ✅ Kafka: Support Redpanda/Strimzi Kafka for Pub/Sub
- ✅ State: Use PostgreSQL (Neon DB connection string format)
- ✅ Jobs: Use Jobs API for scheduled reminders
- ✅ Secrets: Use Kubernetes Secret Store for API keys
- ❌ No hard-coded values: Use `{PLACEHOLDER}` format
- ✅ Metadata: Include namespace, labels, and annotations

## Sample YAML Templates

### 1. Pub/Sub - Kafka (Redpanda/Strimzi)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: {NAMESPACE}
  labels:
    app: todo-chatbot
    component: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  # Kafka brokers
  - name: brokers
    value: "{KAFKA_BROKERS}"  # e.g., "redpanda-0.redpanda.default.svc.cluster.local:9092"
  - name: consumerGroup
    value: "{CONSUMER_GROUP}"  # e.g., "todo-backend-group"
  - name: clientId
    value: "{CLIENT_ID}"  # e.g., "todo-backend"

  # Authentication (optional for Redpanda in dev)
  - name: authType
    value: "none"  # or "password" for production
  # - name: saslUsername
  #   secretKeyRef:
  #     name: kafka-secrets
  #     key: username
  # - name: saslPassword
  #   secretKeyRef:
  #     name: kafka-secrets
  #     key: password

  # Consumer configuration
  - name: consumeRetryInterval
    value: "200ms"
  - name: maxMessageBytes
    value: "1024000"

  # Topic configuration
  - name: initialOffset
    value: "newest"  # or "oldest"

  # Dead letter queue
  - name: deadLetterTopic
    value: "{DLQ_TOPIC}"  # e.g., "task-events-dlq"

scopes:
- todo-backend
- todo-worker
```

### 2. State Store - PostgreSQL (Neon DB)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-postgresql
  namespace: {NAMESPACE}
  labels:
    app: todo-chatbot
    component: state
spec:
  type: state.postgresql
  version: v1
  metadata:
  # Connection string from Neon DB
  - name: connectionString
    secretKeyRef:
      name: postgres-secrets
      key: connection-string
    # Format: "host={HOST} user={USER} password={PASSWORD} dbname={DBNAME} port=5432 sslmode=require"

  # Table configuration
  - name: tableName
    value: "{TABLE_NAME}"  # e.g., "todo_state"
  - name: metadataTableName
    value: "{METADATA_TABLE}"  # e.g., "todo_state_metadata"

  # Performance tuning
  - name: timeout
    value: "20s"
  - name: maxConns
    value: "10"
  - name: connectionMaxIdleTime
    value: "5m"

  # Cleanup policy
  - name: cleanupIntervalInSeconds
    value: "3600"  # 1 hour

scopes:
- todo-backend
```

### 3. Jobs API - Scheduled Reminders

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: jobs-scheduler
  namespace: {NAMESPACE}
  labels:
    app: todo-chatbot
    component: jobs
spec:
  type: jobs.dapr
  version: v1
  metadata:
  # Job store backend (uses state store)
  - name: stateStore
    value: "statestore-postgresql"

  # Scheduler configuration
  - name: maxConcurrentJobs
    value: "10"
  - name: jobTimeout
    value: "5m"

  # Retry policy
  - name: maxRetries
    value: "3"
  - name: retryBackoff
    value: "exponential"
  - name: initialRetryInterval
    value: "1s"
  - name: maxRetryInterval
    value: "60s"

scopes:
- todo-backend
- reminder-worker
```

### 4. Secret Store - Kubernetes

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore-kubernetes
  namespace: {NAMESPACE}
  labels:
    app: todo-chatbot
    component: secrets
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  # Namespace where secrets are stored
  - name: namespace
    value: "{NAMESPACE}"

  # Optional: Use default namespace if not specified
  - name: defaultNamespace
    value: "default"

scopes:
- todo-backend
- todo-frontend
```

## Additional Components

### 5. Pub/Sub - Task Events Topic

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-task-events
  namespace: {NAMESPACE}
  labels:
    app: todo-chatbot
    component: pubsub
    topic: task-events
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "{KAFKA_BROKERS}"
  - name: consumerGroup
    value: "task-events-consumer"
  - name: clientId
    value: "task-events-publisher"
  - name: authType
    value: "none"
  - name: consumeRetryInterval
    value: "200ms"
  - name: initialOffset
    value: "newest"
  - name: deadLetterTopic
    value: "task-events-dlq"
scopes:
- todo-backend
```

### 6. Pub/Sub - Reminders Topic

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-reminders
  namespace: {NAMESPACE}
  labels:
    app: todo-chatbot
    component: pubsub
    topic: reminders
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "{KAFKA_BROKERS}"
  - name: consumerGroup
    value: "reminders-consumer"
  - name: clientId
    value: "reminders-publisher"
  - name: authType
    value: "none"
  - name: consumeRetryInterval
    value: "200ms"
  - name: initialOffset
    value: "newest"
  - name: deadLetterTopic
    value: "reminders-dlq"
scopes:
- todo-backend
- reminder-worker
```

## Placeholder Reference

Replace these placeholders when generating actual components:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{NAMESPACE}` | Kubernetes namespace | `todo-app` or `default` |
| `{KAFKA_BROKERS}` | Kafka broker addresses | `redpanda-0.redpanda.default.svc.cluster.local:9092` |
| `{CONSUMER_GROUP}` | Kafka consumer group ID | `todo-backend-group` |
| `{CLIENT_ID}` | Kafka client identifier | `todo-backend` |
| `{DLQ_TOPIC}` | Dead letter queue topic | `task-events-dlq` |
| `{TABLE_NAME}` | PostgreSQL table name | `todo_state` |
| `{METADATA_TABLE}` | Metadata table name | `todo_state_metadata` |
| `{HOST}` | Database host | `ep-cool-cloud-123456.us-east-2.aws.neon.tech` |
| `{USER}` | Database user | `neondb_owner` |
| `{PASSWORD}` | Database password | `<from-secret>` |
| `{DBNAME}` | Database name | `neondb` |

## Best Practices

1. **Secrets Management**: Always use `secretKeyRef` for sensitive data
2. **Scopes**: Limit component access to only necessary apps
3. **Retries**: Configure retry policies for resilience
4. **Dead Letter Queues**: Set up DLQs for failed messages
5. **Monitoring**: Add labels for easier tracking and debugging
6. **Namespaces**: Use consistent namespacing across components
7. **Connection Pooling**: Configure appropriate connection limits
8. **Timeouts**: Set reasonable timeout values

## Deployment

After generating components, deploy them:

```bash
kubectl apply -f {component-file}.yaml
```

Verify deployment:

```bash
kubectl get components -n {NAMESPACE}
kubectl describe component {component-name} -n {NAMESPACE}
```

## Troubleshooting

Common issues and solutions:

1. **Component not loading**: Check Dapr sidecar logs
   ```bash
   kubectl logs {pod-name} -c daprd -n {NAMESPACE}
   ```

2. **Connection failures**: Verify secret values and network policies

3. **Scope issues**: Ensure app ID matches scope configuration

4. **Version mismatch**: Always use `dapr.io/v1alpha1`

## References

- [Dapr Components Documentation](https://docs.dapr.io/reference/components-reference/)
- [Kafka Pub/Sub](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [PostgreSQL State Store](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-postgresql/)
- [Jobs API](https://docs.dapr.io/developing-applications/building-blocks/jobs/)
- [Kubernetes Secrets](https://docs.dapr.io/reference/components-reference/supported-secret-stores/kubernetes-secret-store/)
