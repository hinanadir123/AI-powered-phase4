# Kafka + Dapr Integration for Todo AI Chatbot

## Overview

This document provides comprehensive documentation for integrating Kafka and Dapr to create an event-driven architecture for the Todo AI Chatbot application. This implementation follows cloud-native best practices to deliver scalable and resilient event-driven workflows.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────┐    ┌─────────────┐
│   Frontend UI   │────▶│   Dapr Side- │────│   Kafka     │
└─────────────────┘     │     car      │    │  Cluster    │
                        └──────────────┘    └─────┬───────┘
                             │ │                 │  ▼
                        ┌────▼─┴─────┐        ┌───┴──────┐
                        │   App API  │        │ Consumers│
                        │            │        │  (DLQ)   │
                        └────────────┘        └──────────┘
```

## 1. Kafka Topics Configuration

### Main Topics

#### task-events Topic
- **Purpose**: Handles task CRUD operations and state changes
- **Partitions**: 3 (for scalable parallel processing)
- **Replication Factor**: 3 (for high availability)
- **Retention Policy**: 7 days
- **Cleanup Policy**: Compact + Delete

#### reminders Topic
- **Purpose**: Manages reminder events and notifications
- **Partitions**: 3 (for scalable parallel processing)
- **Replication Factor**: 3 (for high availability)
- **Retention Policy**: 7 days
- **Cleanup Policy**: Delete

#### task-updates Topic
- **Purpose**: Real-time synchronization of task updates
- **Partitions**: 3 (for scalable parallel processing)
- **Replication Factor**: 3 (for high availability)
- **Retention Policy**: 24 hours
- **Cleanup Policy**: Delete

### Dead Letter Queue (DLQ) Topics

#### task-events-dlq
- **Purpose**: Store messages that failed processing
- **Partitions**: 1
- **Replication Factor**: 3
- **Retention Policy**: 30 days

#### reminders-dlq
- **Purpose**: Store reminder messages that failed processing
- **Partitions**: 1
- **Replication Factor**: 3
- **Retention Policy**: 30 days

#### task-updates-dlq
- **Purpose**: Store task update messages that failed processing
- **Partitions**: 1
- **Replication Factor**: 3
- **Retention Policy**: 30 days

### Topic Creation Commands

#### For Redpanda

```bash
# Create main topics
rpk topic create task-events --partitions 3 --replicas 3 \
  --config retention.ms=604800000 \
  --config cleanup.policy=compact,delete

rpk topic create reminders --partitions 3 --replicas 3 \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete

rpk topic create task-updates --partitions 3 --replicas 3 \
  --config retention.ms=86400000 \
  --config cleanup.policy=delete

# Create DLQ topics
rpk topic create task-events-dlq --partitions 1 --replicas 3 \
  --config retention.ms=2592000000 \
  --config cleanup.policy=delete

rpk topic create reminders-dlq --partitions 1 --replicas 3 \
  --config retention.ms=2592000000 \
  --config cleanup.policy=delete

rpk topic create task-updates-dlq --partitions 1 --replicas 3 \
  --config retention.ms=2592000000 \
  --config cleanup.policy=delete
```

#### For Strimzi (Kubernetes)

Create the following KafkaTopic YAML files:

```yaml
# task-events-topic.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000
    cleanup.policy: compact,delete
    min.insync.replicas: 2
```

```yaml
# reminders-topic.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000
    cleanup.policy: delete
    min.insync.replicas: 2
```

```yaml
# task-updates-topic.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 86400000
    cleanup.policy: delete
    min.insync.replicas: 2
```

```yaml
# DLQ topics
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events-dlq
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 1
  replicas: 3
  config:
    retention.ms: 2592000000
    cleanup.policy: delete
    min.insync.replicas: 2
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders-dlq
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 1
  replicas: 3
  config:
    retention.ms: 2592000000
    cleanup.policy: delete
    min.insync.replicas: 2
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates-dlq
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 1
  replicas: 3
  config:
    retention.ms: 2592000000
    cleanup.policy: delete
    min.insync.replicas: 2
```

### Event Schema

#### CloudEvents v1.0 Schema

```json
{
  "specversion": "1.0",
  "id": "task-created-12345",
  "source": "/tasks",
  "type": "task.created",
  "datacontenttype": "application/json",
  "time": "2026-02-18T09:30:00Z",
  "subject": "task:12345",
  "data": {
    "taskId": "12345",
    "title": "New task",
    "description": "Task description",
    "dueDate": "2026-02-20T10:00:00Z",
    "priority": "high",
    "tags": ["work", "urgent"],
    "status": "pending",
    "__originalEvent": "event-payload-as-string"
  },
  "correlationId": "correlation-123",
  "userId": "user-456"
}
```

#### Event Types for task-events Topic

- `task.created` - New task created
- `task.updated` - Task updated
- `task.deleted` - Task deleted
- `task.status.changed` - Task status changed
- `task.due.date.changed` - Task due date changed

#### Event Types for reminders Topic

- `reminder.scheduled` - Reminder scheduled
- `reminder.removed` - Reminder removed
- `reminder.triggered` - Reminder triggered
- `reminder.failed` - Reminder failed processing

#### Event Types for task-updates Topic

- `task.sync` - Task synchronization event
- `task.assignee.changed` - Task assigned to someone else
- `task.comments.updated` - Task comments updated

## 2. Dapr Component YAML Files

### pubsub.kafka.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Kafka Brokers
    - name: brokers
      value: "redpanda:9092"

    # Consumer Group Configuration
    - name: consumerGroup
      value: "dapr-{{ .AppID }}"

    # Authentication (optional - comment out for non-secure clusters)
    # - name: authType
    #   value: "plaintext"
    # - name: saslUsername
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: username
    # - name: saslPassword
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: password
    # - name: saslMechanism
    #   value: "PLAIN"
    # - name: tlsDisable
    #   value: "false"

    # Component Scopes (specific to application IDs)
    - name: scopes
      value: "todo-api,reminder-worker,notification-service,frontend-sync"

    # Performance and reliability settings
    - name: disableTls
      value: "true"  # Set to false for production
    - name: version
      value: "2.8.0"  # Kafka or Redpanda version
    - name: maxMessageBytes
      value: "1048576"  # 1MB in bytes
    - name: dialTimeout
      value: "15s"
    - name: readTimeout
      value: "30s"
    - name: writeTimeout
      value: "30s"
    - name: clientID
      value: "dapr-producer-consumer"

    # Dead Letter Queue configuration
    - name: consumerRetryEnabled
      value: "true"
    - name: publishRetryCount
      value: "5"
    - name: publishRetryInterval
      value: "5s"

    # Topic specific settings
    - name: saslPasswordInSecret
      value: "false"
    - name: initialOffset
      value: "latest"
```

### state.postgresql.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgresql-statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
    # Connection String
    - name: connectionString
      secretKeyRef:
        name: postgres-secrets
        key: connectionString

    # Tables and schema configuration
    - name: tableName
      value: "state_store"

    - name: schemaName
      value: "public"

    # Configuration for key-prefixing and key-management
    - name: keyColumnName
      value: "key"

    - name: valueColumnName
      value: "value"

    - name: urlColumnName
      value: "url"

    - name: versionColumnName
      value: "version"

    - name: metadataTableName
      value: "dapr_metadata"

    # Consistency and reliability settings
    - name: actorStateStore
      value: "true"

    # Timeouts and connection pool settings
    - name: databaseName
      value: "todoapp"

    - name: maxConns
      value: "10"

    - name: maxIdleConns
      value: "5"

    - name: connMaxLifetime
      value: "60m"

    - name: connMaxIdleTime
      value: "30m"

    # Component Scopes
    - name: scopes
      value: "todo-api,reminder-worker,notification-service"
```

### jobs.dapr.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: dapr-jobs
  namespace: default
spec:
  type: workmanager.jobscheduler
  version: v1
  metadata:
    - name: workManagerEndpoint
      value: "http://localhost:3500"
    - name: defaultConcurrency
      value: "10"
    - name: defaultPartitionCount
      value: "1"
    - name: maxRetries
      value: "3"
    - name: retryDelaySeconds
      value: "5"
    - name: defaultJobTimeout
      value: "3600"  # 1 hour in seconds
    - name: maxJobTimeout
      value: "86400"  # 24 hours in seconds
    - name: enableMetrics
      value: "true"
    - name: enableHealthChecks
      value: "true"
    - name: scopes
      value: "todo-api,reminder-worker"
```

### secrets.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: local-secret-store
  namespace: default
spec:
  type: secretstores.local.file
  version: v1
  metadata:
    - name: secretsFile
      value: "/path/to/secrets.json"
    - name: nestedSeparator
      value: ":"
    - name: multiValued
      value: "false"

---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secret-store
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
    - name: name
      value: "kubernetes"
    - name: scopes
      value: "todo-api,reminder-worker,notification-service"
```

## 3. Code Examples

### Publishing Events

#### Golang Task Event Publisher

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "time"
)

// CloudEvent represents the CloudEvents v1.0 schema
type CloudEvent struct {
    SpecVersion     string      `json:"specversion"`
    ID              string      `json:"id"`
    Source          string      `json:"source"`
    Type            string      `json:"type"`
    DataContentType string      `json:"datacontenttype"`
    Time            time.Time   `json:"time"`
    Subject         string      `json:"subject"`
    Data            interface{} `json:"data"`
    CorrelationID   string      `json:"correlationId,omitempty"`
    UserID          string      `json:"userId,omitempty"`
}

// Task represents the task structure
type Task struct {
    ID          string   `json:"id"`
    Title       string   `json:"title"`
    Description string   `json:"description"`
    DueDate     string   `json:"dueDate,omitempty"`
    Priority    string   `json:"priority"`
    Tags        []string `json:"tags"`
    Status      string   `json:"status"`
    Assignee    string   `json:"assignee,omitempty"`
    CreatedBy   string   `json:"createdBy"`
}

// publishTaskEvent publishes task events to the task-events topic
func publishTaskEvent(daprEndpoint, appID, eventType string, task Task, correlationID, userID string) error {
    // Create CloudEvent
    event := CloudEvent{
        SpecVersion:     "1.0",
        ID:              fmt.Sprintf("task-%s-%s", eventType, task.ID),
        Source:          fmt.Sprintf("/apps/%s/services/todo-api", appID),
        Type:            fmt.Sprintf("task.%s", eventType),
        DataContentType: "application/json",
        Time:            time.Now().UTC(),
        Subject:         fmt.Sprintf("task:%s", task.ID),
        Data: map[string]interface{}{
            "taskId":      task.ID,
            "title":       task.Title,
            "description": task.Description,
            "dueDate":     task.DueDate,
            "priority":    task.Priority,
            "tags":        task.Tags,
            "status":      task.Status,
            "assignee":    task.Assignee,
            "createdBy":   task.CreatedBy,
        },
        CorrelationID: correlationID,
        UserID:        userID,
    }

    // Serialize event to JSON
    eventData, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("failed to marshal event: %w", err)
    }

    // Dapr pubsub endpoint
    url := fmt.Sprintf("%s/v1.0/publish/kafka-pubsub/task-events", daprEndpoint)

    // Create HTTP request
    req, err := http.NewRequest("POST", url, bytes.NewReader(eventData))
    if err != nil {
        return fmt.Errorf("failed to create request: %w", err)
    }

    // Set headers
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("traceparent", generateTraceParent()) // For distributed tracing

    // Make the HTTP call
    client := &http.Client{Timeout: 30 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return fmt.Errorf("failed to publish event: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 400 {
        body, _ := io.ReadAll(resp.Body)
        return fmt.Errorf("publish failed with status %d: %s", resp.StatusCode, string(body))
    }

    fmt.Printf("Task event published successfully: %s\n", event.ID)
    return nil
}

// publishReminderEvent publishes reminder events to the reminders topic
func publishReminderEvent(daprEndpoint, appID, eventType string, taskID, reminderMessage string, reminderTime time.Time, correlationID string) error {
    // Create CloudEvent for reminder
    event := CloudEvent{
        SpecVersion:     "1.0",
        ID:              fmt.Sprintf("reminder-%s-%s", eventType, taskID),
        Source:          fmt.Sprintf("/apps/%s/services/reminder-worker", appID),
        Type:            fmt.Sprintf("reminder.%s", eventType),
        DataContentType: "application/json",
        Time:            time.Now().UTC(),
        Subject:         fmt.Sprintf("reminder:%s", taskID),
        Data: map[string]interface{}{
            "taskID":           taskID,
            "reminderMessage":  reminderMessage,
            "reminderTime":     reminderTime.Format(time.RFC3339),
            "reminderType":     "task_due_soon",
        },
        CorrelationID: correlationID,
    }

    // Serialize event to JSON
    eventData, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("failed to marshal reminder event: %w", err)
    }

    // Dapr pubsub endpoint for reminders topic
    url := fmt.Sprintf("%s/v1.0/publish/kafka-pubsub/reminders", daprEndpoint)

    // Create HTTP request
    req, err := http.NewRequest("POST", url, bytes.NewReader(eventData))
    if err != nil {
        return fmt.Errorf("failed to create reminder request: %w", err)
    }

    // Set headers
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("traceparent", generateTraceParent())

    // Make the HTTP call
    client := &http.Client{Timeout: 30 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return fmt.Errorf("failed to publish reminder event: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 400 {
        body, _ := io.ReadAll(resp.Body)
        return fmt.Errorf("reminder publish failed with status %d: %s", resp.StatusCode, string(body))
    }

    fmt.Printf("Reminder event published successfully: %s\n", event.ID)
    return nil
}

// generateTraceParent creates a traceparent header for distributed tracing
func generateTraceParent() string {
    // In a real implementation, this would generate a proper W3C traceparent
    return "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
}

// Example usage
func main() {
    daprEndpoint := "http://localhost:3500"
    appID := "todo-api"

    // Example task
    task := Task{
        ID:          "task-12345",
        Title:       "Complete Dapr Integration",
        Description: "Implement Kafka and Dapr integration for the Todo app",
        DueDate:     "2026-02-25T10:00:00Z",
        Priority:    "high",
        Tags:        []string{"dapr", "kafka", "integration"},
        Status:      "pending",
        Assignee:    "user-001",
        CreatedBy:   "user-001",
    }

    // Publish task created event
    err := publishTaskEvent(daprEndpoint, appID, "created", task, "corr-12345", "user-001")
    if err != nil {
        fmt.Printf("Error publishing event: %v\n", err)
        return
    }

    // Publish reminder event
    reminderTime := time.Now().Add(24 * time.Hour) // Tomorrow
    err = publishReminderEvent(daprEndpoint, appID, "scheduled", task.ID, "Task is due soon: Complete Dapr Integration", reminderTime, "corr-12345")
    if err != nil {
        fmt.Printf("Error publishing reminder: %v\n", err)
        return
    }
}
```

#### Golang Event Consumer

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "time"
)

// EventHandler defines the interface for processing events
type EventHandler interface {
    Handle(ctx *Context, event *CloudEvent) error
}

// Context provides context for event handling
type Context struct {
    AppID        string
    DaprEndpoint string
    CorrelationID string
}

// ReminderEventHandler handles reminder events
type ReminderEventHandler struct {
    Context
}

// Handle processes reminder events
func (h *ReminderEventHandler) Handle(ctx *Context, event *CloudEvent) error {
    fmt.Printf("Processing reminder event: %s, type: %s\n", event.ID, event.Type)

    switch event.Type {
    case "reminder.scheduled":
        return h.handleReminderScheduled(event)
    case "reminder.triggered", "reminder.removed":
        return h.handleReminderOther(event)
    default:
        return fmt.Errorf("unsupported event type: %s", event.Type)
    }
}

func (h *ReminderEventHandler) handleReminderScheduled(event *CloudEvent) error {
    // Extract reminder data
    data, ok := event.Data.(map[string]interface{})
    if !ok {
        return fmt.Errorf("invalid event data format")
    }

    // Process reminder scheduling
    taskID, _ := data["taskID"].(string)
    reminderTimeStr, _ := data["reminderTime"].(string)

    reminderTime, err := time.Parse(time.RFC3339, reminderTimeStr)
    if err != nil {
        return fmt.Errorf("failed to parse reminder time: %w", err)
    }

    // Schedule the actual reminder (in a real app, this would call a scheduler service)
    fmt.Printf("Scheduled reminder for task %s at %s\n", taskID, reminderTime.Format(time.RFC3339))

    // Create a job using Dapr Jobs API
    err = h.scheduleReminderJob(ctx, taskID, event.CorrelationID)
    if err != nil {
        return fmt.Errorf("failed to schedule job: %w", err)
    }

    return nil
}

func (h *ReminderEventHandler) handleReminderOther(event *CloudEvent) error {
    // Handle other reminder events
    fmt.Printf("Handling other reminder event: %s\n", event.Type)
    return nil
}

// scheduleReminderJob creates a Dapr job to trigger the reminder
func (h *ReminderEventHandler) scheduleReminderJob(ctx *Context, taskID, correlationID string) error {
    job := map[string]interface{}{
        "jobName":      fmt.Sprintf("reminder-job-%s", taskID),
        "scheduleTime": time.Now().Add(24 * time.Hour).Format(time.RFC3339),
        "retries":      3,
        "maxFailureRetries": 2,
        "timeoutSeconds": 300, // 5 minutes
        "concurrency": 1,
        "jobData": map[string]interface{}{
            "taskID":        taskID,
            "correlationID": correlationID,
            "type":          "reminder-trigger",
        },
    }

    // Create HTTP request to Dapr Jobs endpoint
    url := fmt.Sprintf("%s/v1.0/jobscheduler/dapr-jobs/schedule", h.DaprEndpoint)
    jobData, err := json.Marshal(job)
    if err != nil {
        return fmt.Errorf("failed to marshal job: %w", err)
    }

    req, err := http.NewRequest("POST", url, bytes.NewReader(jobData))
    if err != nil {
        return fmt.Errorf("failed to create job request: %w", err)
    }

    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("traceparent", h.generateTraceParent())

    client := &http.Client{Timeout: 30 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return fmt.Errorf("failed to schedule job: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 400 {
        body, _ := io.ReadAll(resp.Body)
        return fmt.Errorf("job scheduling failed with status %d: %s", resp.StatusCode, string(body))
    }

    fmt.Printf("Reminder job scheduled successfully for task %s\n", taskID)
    return nil
}

// StateManagementHandler manages state operations
type StateManagementHandler struct {
    Context
}

// Handle updates task state
func (h *StateManagementHandler) Handle(ctx *Context, event *CloudEvent) error {
    fmt.Printf("Processing task state update event: %s\n", event.Type)

    // Get the updated task data
    data, ok := event.Data.(map[string]interface{})
    if !ok {
        return fmt.Errorf("invalid event data format for state update")
    }

    taskID, _ := data["taskId"].(string)
    if taskID == "" {
        return fmt.Errorf("missing taskID in event data")
    }

    // Construct state item
    stateItem := map[string]interface{}{
        "taskId":    taskID,
        "title":     data["title"],
        "status":    data["status"],
        "updatedAt": time.Now().UTC().Format(time.RFC3339),
    }

    // Save to Dapr state store
    return h.saveTaskState(taskID, stateItem, event.CorrelationID)
}

// saveTaskState saves the task state using Dapr
func (h *StateManagementHandler) saveTaskState(key string, data map[string]interface{}, etag string) error {
    // Prepare the state operation
    stateOperation := map[string]interface{}{
        "key":   fmt.Sprintf("task:%s", key),
        "value": data,
    }

    if etag != "" {
        stateOperation["etag"] = etag
    }

    operations := []map[string]interface{}{stateOperation}

    url := fmt.Sprintf("%s/v1.0/state/postgresql-statestore", h.DaprEndpoint)

    stateData, err := json.Marshal(operations)
    if err != nil {
        return fmt.Errorf("failed to marshal state data: %w", err)
    }

    req, err := http.NewRequest("POST", url, bytes.NewReader(stateData))
    if err != nil {
        return fmt.Errorf("failed to create state request: %w", err)
    }

    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{Timeout: 30 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return fmt.Errorf("failed to save state: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 400 {
        body, _ := io.ReadAll(resp.Body)
        return fmt.Errorf("state save failed with status %d: %s", resp.StatusCode, string(body))
    }

    fmt.Printf("State saved successfully for task: %s\n", key)
    return nil
}

// TaskHTTPService implements HTTP endpoints for event subscription
type TaskHTTPService struct {
    DaprEndpoint string
}

// RegisterRoutes registers the HTTP handlers for subscriptions
func (s *TaskHTTPService) RegisterRoutes(mux *http.ServeMux) {
    mux.HandleFunc("/dapr/subscribe", s.handleSubscription)
    mux.HandleFunc("/task-events", s.handleTaskEvents)
    mux.HandleFunc("/reminder-events", s.handleReminderEvents)
    mux.HandleFunc("/task-update-events", s.handleTaskUpdates)
}

// handleSubscription returns the subscription configuration
func (s *TaskHTTPService) handleSubscription(w http.ResponseWriter, r *http.Request) {
    subscriptions := []map[string]interface{}{
        // Subscribe to task events
        {
            "pubsubname": "kafka-pubsub",
            "topic":      "task-events",
            "route":      "/task-events",
            "deadLetterTopic": "task-events-dlq",
        },
        // Subscribe to reminder events
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/reminder-events",
            "metadata": map[string]string{
                "consumerGroup": "dapr-{{.AppID}}-reminders",
            },
            "deadLetterTopic": "reminders-dlq",
        },
        // Subscribe to task update events
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-updates",
            "route": "/task-update-events",
            "metadata": map[string]string{
                "consumerGroup": "dapr-{{.AppID}}-updates",
            },
            "deadLetterTopic": "task-updates-dlq",
        },
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(subscriptions)
}

// handleTaskEvents processes task-related events
func (s *TaskHTTPService) handleTaskEvents(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
        return
    }

    // Read and parse the CloudEvent
    body, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "failed to read request body", http.StatusBadRequest)
        return
    }

    var event CloudEvent
    if err := json.Unmarshal(body, &event); err != nil {
        fmt.Printf("Error parsing CloudEvent: %v, body: %s\n", err, string(body))
        http.Error(w, "invalid event format", http.StatusBadRequest)
        return
    }

    // Create context
    ctx := &Context{
        AppID:        r.Header.Get("dapr-app-id"),
        DaprEndpoint: s.DaprEndpoint,
        CorrelationID: event.CorrelationID,
    }

    // Handle the event based on type
    switch event.Type {
    case "task.created", "task.updated", "task.deleted", "task.status.changed":
        handler := &StateManagementHandler{Context: *ctx}
        if err := handler.Handle(ctx, &event); err != nil {
            fmt.Printf("Error handling task event %s: %v\n", event.ID, err)
            http.Error(w, "failed to process event", http.StatusInternalServerError)
            return
        }
    default:
        fmt.Printf("Unsupported task event type: %s\n", event.Type)
        w.WriteHeader(http.StatusOK)
        return
    }

    w.WriteHeader(http.StatusOK)
    w.Write([]byte("Task event processed successfully"))
}

// handleReminderEvents processes reminder-related events
func (s *TaskHTTPService) handleReminderEvents(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
        return
    }

    // Read and parse the CloudEvent
    body, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "failed to read request body", http.StatusBadRequest)
        return
    }

    var event CloudEvent
    if err := json.Unmarshal(body, &event); err != nil {
        fmt.Printf("Error parsing CloudEvent: %v, body: %s\n", err, string(body))
        http.Error(w, "invalid event format", http.StatusBadRequest)
        return
    }

    // Create context
    ctx := &Context{
        AppID:        r.Header.Get("dapr-app-id"),
        DaprEndpoint: s.DaprEndpoint,
        CorrelationID: event.CorrelationID,
    }

    // Handle the event
    handler := &ReminderEventHandler{Context: *ctx}
    if err := handler.Handle(ctx, &event); err != nil {
        fmt.Printf("Error handling reminder event %s: %v\n", event.ID, err)
        http.Error(w, "failed to process event", http.StatusInternalServerError)
        return
    }

    w.WriteHeader(http.StatusOK)
    w.Write([]byte("Reminder event processed successfully"))
}

// handleTaskUpdates handles real-time task updates
func (s *TaskHTTPService) handleTaskUpdates(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
        return
    }

    body, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "failed to read request body", http.StatusBadRequest)
        return
    }

    var event CloudEvent
    if err := json.Unmarshal(body, &event); err != nil {
        fmt.Printf("Error parsing CloudEvent: %v, body: %s\n", err, string(body))
        http.Error(w, "invalid event format", http.StatusBadRequest)
        return
    }

    // Log for real-time sync service
    fmt.Printf("Task update received for event %s: %s\n", event.ID, event.Subject)

    // In a real implementation, this would update frontend sync or push notifications
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("Task update processed"))
}

// generateTraceParent creates a new trace parent
func (s *TaskHTTPService) generateTraceParent() string {
    return "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
}

// Main function to start the HTTP service
func main() {
    service := &TaskHTTPService{
        DaprEndpoint: "http://localhost:3500",
    }

    mux := http.NewServeMux()
    service.RegisterRoutes(mux)

    fmt.Println("Starting task event service on :8080")
    if err := http.ListenAndServe(":8080", mux); err != nil {
        fmt.Printf("Server failed to start: %v\n", err)
    }
}
```

## 4. Deployment Instructions

### Prerequisites

- Kubernetes cluster (Minikube, EKS, GKE, or AKS)
- Dapr CLI and Dapr initialized in Kubernetes
- Helm 3
- Kafka/Redpanda cluster running in Kubernetes

### Local Development Setup

```bash
# 1. Initialize Dapr for Kubernetes
dapr init -k

# 2. Apply Dapr components
kubectl apply -f pubsub.kafka.yaml
kubectl apply -f state.postgresql.yaml
kubectl apply -f jobs.dapr.yaml
kubectl apply -f secrets.yaml

# 3. Deploy applications with Dapr sidecar injection
kubectl apply -f task-api-deployment.yaml
kubectl apply -f reminder-worker-deployment.yaml
```

### Kafka/Redpanda Deployment

```bash
# For Redpanda in Kubernetes
kubectl apply -f https://github.com/redpanda-data/redpanda/releases/download/v22.2.1/redpanda.yaml

# For Strimzi Kafka Operator
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f kafka-cluster.yaml
```

### Dapr Components Deployment

```bash
# Create the Dapr components directory structure
mkdir -p dapr-components
kubectl create namespace dapr-system

# Apply all Dapr components
kubectl apply -f ./dapr-components/pubsub-kafka.yaml
kubectl apply -f ./dapr-components/state-postgresql.yaml
kubectl apply -f ./dapr-components/jobs-dapr.yaml
kubectl apply -f ./dapr-components/secrets.yaml
```

### Example Application Deployment YAML

```yaml
# task-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
  namespace: default
  labels:
    app: todo-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-api
  template:
    metadata:
      labels:
        app: todo-api
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-api"
        dapr.io/app-port: "8080"
        dapr.io/app-protocol: "http"
        dapr.io/log-level: "info"
        dapr.io/components-path: "/dapr/components"
        dapr.io/config: "app-config"
    spec:
      containers:
      - name: todo-api
        image: your-todo-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DAPR_HTTP_ENDPOINT
          value: "http://localhost:3500"
        - name: DAPR_GRPC_ENDPOINT
          value: "localhost:50001"
---
apiVersion: v1
kind: Service
metadata:
  name: todo-api-service
  namespace: default
spec:
  selector:
    app: todo-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

### Verification Steps

```bash
# 1. Check if Dapr components are loaded
kubectl get components -n dapr-system

# 2. Check application pods with Dapr sidecar
kubectl get pods -l app=todo-api -o yaml | grep init

# 3. Check Kafka topics
kubectl run kafka-test --image=docker.io/bitnami/kafka:latest --rm -it --restart=Never -- \
  kafka-topics.sh --list --bootstrap-server my-cluster-kafka-brokers:9092

# 4. Check Dapr logs
kubectl logs -l app=todo-api -c daprd

# 5. Test the service
kubectl port-forward svc/todo-api-service 8080:80
curl -v http://localhost:8080/health
```

### Testing Event Flow

```bash
# 1. Publish a test event using Dapr CLI
dapr publish --pubsub kafka-pubsub -t task-events -d '{"taskId":"123","title":"Test task","status":"pending"}'

# 2. Check event consumption
dapr logs todo-api -k --tail 100

# 3. Verify state changes
kubectl exec -it deploy/todo-api -- dapr get todo-api-state-store
```

## Best Practices

1. **Event Design**:
   - Always use CloudEvents v1.0 format
   - Include correlation IDs for traceability
   - Use consistent naming conventions for event types
   - Include timestamps in UTC

2. **Error Handling**:
   - Implement dead-letter queues for failed events
   - Use exponential backoff for retries
   - Log all errors for monitoring

3. **Security**:
   - Use Dapr secrets for all credentials
   - Enable TLS for Kafka connections in production
   - Use Dapr sidecar authentication

4. **Observability**:
   - Enable distributed tracing with correlation IDs
   - Implement metrics collection
   - Add health checks for all services

5. **Scalability**:
   - Use multiple partitions for topics
   - Configure appropriate consumer groups
   - Monitor throughput and adjust accordingly

6. **Idempotency**:
   - Design event handlers to be idempotent
   - Use event IDs to prevent duplicate processing
   - Store processed event IDs for reference