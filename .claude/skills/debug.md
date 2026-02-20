# Debug

Debug issues in the Todo AI Chatbot application.

## Usage
```
/debug [component] [issue-type]
```

## Arguments
- `component` (optional): Component to debug (backend/frontend/database/kafka/dapr/network)
- `issue-type` (optional): Issue type (crash/slow/error/connection)

## What it does
1. Analyzes recent logs for errors
2. Checks pod events and status
3. Validates configuration
4. Tests network connectivity
5. Inspects resource usage
6. Reviews recent deployments
7. Provides troubleshooting steps

## Debug Scenarios

### Pod Crashes
- Check restart count
- Review crash logs
- Analyze OOMKilled events
- Check liveness/readiness probes
- Validate resource limits

### Slow Performance
- Profile CPU usage
- Check memory leaks
- Analyze database queries
- Review network latency
- Check Kafka consumer lag

### Connection Errors
- Test service endpoints
- Validate DNS resolution
- Check network policies
- Review firewall rules
- Test database connectivity

### Kafka Issues
- Check broker connectivity
- Validate topic configuration
- Review consumer lag
- Check partition distribution
- Analyze message throughput

### Dapr Issues
- Check sidecar status
- Validate component configuration
- Test state store connection
- Review pub/sub connectivity
- Check API call logs

## Example
```
/debug backend crash
/debug kafka connection
/debug dapr --verbose
/debug --recent-errors
```
