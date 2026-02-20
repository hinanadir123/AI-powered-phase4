# Health Check

Run comprehensive health checks on the Todo AI Chatbot.

## Usage
```
/health-check [component]
```

## Arguments
- `component` (optional): Component to check (backend/frontend/database/kafka/dapr/all). Default: all

## What it does
1. Checks pod health and readiness
2. Verifies service endpoints
3. Tests database connectivity
4. Validates Kafka/Dapr components
5. Checks resource utilization
6. Verifies external dependencies
7. Generates health report

## Example
```
/health-check
/health-check backend
/health-check database
```
