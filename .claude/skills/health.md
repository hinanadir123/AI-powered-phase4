# Health Check

Check health status of all services.

## Usage
```
/health [service]
```

## Arguments
- `service` (optional): Service to check (all/backend/frontend/database/kafka/dapr). Default: all

## What it does
1. Checks pod status
2. Validates readiness probes
3. Tests liveness probes
4. Verifies service endpoints
5. Checks database connections
6. Validates Kafka connectivity
7. Tests Dapr components
8. Shows dependency health

## Health Indicators

### Pod Health
- ✅ Running
- ⚠️ Pending
- ❌ Failed
- 🔄 Restarting

### Service Health
- ✅ Healthy (all checks pass)
- ⚠️ Degraded (some checks fail)
- ❌ Unhealthy (critical checks fail)
- ❓ Unknown (cannot determine)

## Checks Performed

### Backend
- HTTP endpoint responding
- Database connection active
- Dapr sidecar healthy
- Kafka producer connected

### Frontend
- HTTP endpoint responding
- Static assets loading
- API connectivity

### Database
- Connection pool available
- Query response time
- Replication status

### Kafka
- Brokers reachable
- Topics accessible
- Consumer groups active

### Dapr
- Sidecar running
- Components loaded
- State store accessible
- Pub/Sub connected

## Example
```
/health
/health backend
/health --verbose
/health --watch
```
