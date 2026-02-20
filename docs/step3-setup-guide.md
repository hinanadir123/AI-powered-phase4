# Phase 5 Step 3: Kafka + Dapr Integration - Setup Guide

## Overview

Step 3 integrates event-driven architecture using Kafka (Redpanda) and Dapr for the Todo AI Chatbot. This enables:
- Asynchronous task event publishing
- Reminder notifications via message queue
- Scalable microservices architecture
- Easy swap between message brokers (Kafka, RabbitMQ, Redis, etc.)

## Prerequisites

1. **Docker Desktop** - Must be running
2. **Dapr CLI** - Install from https://docs.dapr.io/getting-started/install-dapr-cli/
3. **Backend and Frontend** - Already running on ports 8001 and 3001

## Step-by-Step Setup

### 1. Start Docker Desktop

Make sure Docker Desktop is running on your machine.

### 2. Start Infrastructure (Kafka, PostgreSQL, Redis)

```bash
# From project root
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps
```

This starts:
- **Redpanda** (Kafka-compatible) on port 19092
- **Redpanda Console** (Web UI) on port 8080
- **PostgreSQL** on port 5432
- **Redis** on port 6379

### 3. Create Kafka Topics

```bash
# Make script executable (Git Bash on Windows)
chmod +x scripts/setup-kafka-topics.sh

# Run the script
./scripts/setup-kafka-topics.sh
```

This creates:
- `task-events` - Task CRUD events
- `reminders` - Reminder notifications
- `task-updates` - Real-time task updates
- `task-events-dlq` - Dead letter queue for failed events
- `reminders-dlq` - Dead letter queue for failed reminders

### 4. Initialize Dapr (Local Development)

```bash
# Initialize Dapr for local development
dapr init

# Verify Dapr is running
dapr --version
```

### 5. Run Backend with Dapr Sidecar

Stop the current backend server (Ctrl+C in the terminal) and restart with Dapr:

```bash
cd backend

# Run with Dapr sidecar
dapr run \
  --app-id todo-backend \
  --app-port 8001 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ../dapr-components \
  --log-level info \
  -- python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

This starts:
- **Backend API** on port 8001
- **Dapr HTTP API** on port 3500 (for event publishing)
- **Dapr gRPC API** on port 50001

### 6. Enable Dapr Event Publishing

Set environment variable to enable Dapr:

```bash
# Windows (PowerShell)
$env:DAPR_ENABLED="true"

# Windows (CMD)
set DAPR_ENABLED=true

# Linux/Mac
export DAPR_ENABLED=true
```

Then restart the backend with Dapr (Step 5).

### 7. Verify Event Publishing

Create a task via the API and check Dapr logs:

```bash
# The Dapr sidecar logs will show:
# [EVENT PUBLISHED] task.created to task-events
```

View events in Redpanda Console: http://localhost:8080

## Architecture

```
┌─────────────┐
│   Frontend  │
│  (Port 3001)│
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────────────────────┐
│         Backend API                 │
│         (Port 8001)                 │
│  ┌──────────────────────────────┐  │
│  │  Task Routes                 │  │
│  │  - Create → Publish Event    │  │
│  │  - Update → Publish Event    │  │
│  │  - Delete → Publish Event    │  │
│  │  - Complete → Publish Event  │  │
│  └──────────┬───────────────────┘  │
└─────────────┼───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Dapr Sidecar (Port 3500)       │
│  ┌──────────────────────────────┐  │
│  │  Pub/Sub Component (Kafka)   │  │
│  │  - Publish to task-events    │  │
│  │  - Publish to reminders      │  │
│  └──────────┬───────────────────┘  │
└─────────────┼───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Kafka (Redpanda)               │
│      (Port 19092)                   │
│  ┌──────────────────────────────┐  │
│  │  Topics:                     │  │
│  │  - task-events               │  │
│  │  - reminders                 │  │
│  │  - task-updates              │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    Reminder Worker (Future)         │
│    - Subscribes to reminders        │
│    - Sends notifications            │
└─────────────────────────────────────┘
```

## Event Flow Example

1. **User creates a task** via frontend
2. **Backend API** receives POST request
3. **Task is saved** to PostgreSQL
4. **Event is published** to Dapr sidecar via HTTP:
   ```
   POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-events
   Body: {
     "event_type": "task.created",
     "timestamp": "2026-02-17T12:00:00Z",
     "data": { "task_id": 123, "title": "Buy groceries", ... }
   }
   ```
5. **Dapr publishes** event to Kafka topic `task-events`
6. **Consumers** (reminder worker, analytics) receive the event

## Monitoring

### Redpanda Console
- URL: http://localhost:8080
- View topics, messages, consumer groups
- Monitor message throughput and lag

### Dapr Dashboard
```bash
dapr dashboard
```
- URL: http://localhost:8501
- View components, applications, logs

## Troubleshooting

### Docker containers not starting
```bash
# Check Docker Desktop is running
docker ps

# View logs
docker-compose logs -f redpanda
```

### Dapr sidecar not connecting to Kafka
```bash
# Check Dapr component configuration
cat dapr-components/pubsub-kafka.yaml

# Verify broker address is localhost:19092
```

### Events not being published
```bash
# Check DAPR_ENABLED environment variable
echo $DAPR_ENABLED  # Should be "true"

# Check Dapr sidecar logs
# Look for "EVENT PUBLISHED" messages
```

### Kafka topics not created
```bash
# List topics manually
docker exec redpanda rpk topic list --brokers localhost:9092

# Create topics manually if needed
docker exec redpanda rpk topic create task-events --brokers localhost:9092 --partitions 3
```

## Next Steps

After completing Step 3:
- **Step 4**: Deploy to local Minikube with Dapr + Kafka
- **Step 5**: Deploy to cloud (Oracle OKE / Azure AKS / Google GKE)
- **Step 6**: Set up CI/CD and monitoring
- **Step 7**: Final testing and documentation

## Files Created/Modified in Step 3

**Created:**
- `docker-compose.yml` - Infrastructure setup
- `backend/event_publisher.py` - Dapr event publishing service
- `scripts/setup-kafka-topics.sh` - Kafka topics creation script
- `docs/step3-setup-guide.md` - This guide

**Modified:**
- `backend/routes/tasks.py` - Integrated event publishing
- `dapr-components/pubsub-kafka.yaml` - Updated broker configuration

## Status

✅ Step 3 Complete - Kafka + Dapr Integration Ready

**Progress:** 60% (3/7 steps done)
