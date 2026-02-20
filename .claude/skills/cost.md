# Cost

Analyze and optimize cloud costs.

## Usage
```
/cost [operation]
```

## Arguments
- `operation`: Operation (analyze/optimize/report/forecast/alerts)

## What it does

### analyze
- Shows current costs by service
- Breaks down by resource type
- Identifies cost trends
- Compares to budget

### optimize
- Identifies cost-saving opportunities
- Suggests right-sizing
- Recommends reserved instances
- Finds unused resources

### report
- Generates cost report
- Shows cost breakdown
- Exports to CSV/PDF
- Sends to stakeholders

### forecast
- Predicts future costs
- Based on usage trends
- Considers growth plans
- Alerts on budget overruns

### alerts
- Sets up cost alerts
- Notifies on threshold breach
- Daily/weekly summaries
- Anomaly detection

## Cost Categories

### Compute
- Kubernetes nodes
- VM instances
- Container registry
- Load balancers

### Storage
- Persistent volumes
- Object storage (S3/Blob)
- Database storage
- Backup storage

### Network
- Data transfer
- Load balancer traffic
- VPN/NAT gateway
- CDN costs

### Services
- Managed database
- Managed Kafka
- Monitoring/logging
- DNS services

## Optimization Tips
- Right-size pods (CPU/memory requests)
- Use spot/preemptible instances
- Delete unused resources
- Optimize storage classes
- Use reserved instances
- Enable autoscaling
- Compress data
- Use caching

## Example
```
/cost analyze
/cost optimize --recommendations
/cost report --month=january
/cost forecast --months=3
/cost alerts --threshold=1000
```
