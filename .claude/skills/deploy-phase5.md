# Deploy Phase 5

Deploy Phase 5 Todo AI Chatbot with Kafka and Dapr integration.

## Usage
```
/deploy-phase5 [environment]
```

## Arguments
- `environment` (optional): Target environment (local/dev/staging/prod). Default: local

## What it does
1. Validates Phase 5 prerequisites (Kafka, Dapr, PostgreSQL)
2. Deploys Dapr components (Pub/Sub, State, Jobs, Secrets)
3. Deploys backend with event handlers
4. Deploys frontend with new features
5. Sets up Kafka topics (task-events, reminders)
6. Configures recurring tasks and reminders
7. Runs integration tests
8. Provides health check endpoints

## Features Deployed
- Recurring tasks with cron expressions
- Task reminders and notifications
- Priority levels and tags
- Search, filter, and sort
- Event-driven architecture with Kafka
- Dapr Pub/Sub integration

## Example
```
/deploy-phase5
/deploy-phase5 dev
/deploy-phase5 prod
```
