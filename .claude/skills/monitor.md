# Monitor

Monitor application health, metrics, and performance.

## Usage
```
/monitor [component] [metric]
```

## Arguments
- `component` (optional): Component to monitor (all/backend/frontend/database/kafka/dapr). Default: all
- `metric` (optional): Specific metric (cpu/memory/requests/errors/latency)

## What it does
1. Shows real-time metrics dashboard
2. Monitors resource usage (CPU, memory, disk)
3. Tracks request rates and latency
4. Monitors error rates and types
5. Shows Kafka consumer lag
6. Displays Dapr sidecar metrics
7. Alerts on threshold violations

## Metrics Tracked

### Application
- Request rate (req/sec)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Active connections

### Infrastructure
- CPU usage (%)
- Memory usage (MB)
- Disk I/O
- Network traffic

### Kafka
- Message throughput
- Consumer lag
- Partition distribution
- Replication status

### Dapr
- Sidecar health
- Component status
- API call latency
- State store operations

## Example
```
/monitor
/monitor backend cpu
/monitor kafka --consumer-lag
/monitor all --alerts
```
