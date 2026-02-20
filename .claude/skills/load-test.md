# Load Test

Run load tests against the Todo AI Chatbot.

## Usage
```
/load-test [scenario] [options]
```

## Arguments
- `scenario`: Test scenario (api/ui/kafka/full)
- `options` (optional): Test parameters (users/duration/rps)

## What it does
1. Prepares test environment
2. Generates test data
3. Runs load test scenarios
4. Monitors system metrics
5. Analyzes results
6. Generates performance report

## Test Scenarios

### API Load Test
- Tests REST endpoints
- Simulates concurrent users
- Measures response times
- Tracks error rates

### UI Load Test
- Tests frontend performance
- Simulates user interactions
- Measures page load times
- Tracks client-side errors

### Kafka Load Test
- Tests message throughput
- Measures producer/consumer performance
- Validates message ordering
- Tests under high load

### Full System Test
- End-to-end load testing
- All components under load
- Realistic user scenarios
- Stress testing

## Test Parameters
- Users: 1-10000 concurrent users
- Duration: 1m-60m
- RPS: 1-10000 requests/second
- Ramp-up: Gradual or instant

## Metrics Collected
- Response time (p50, p95, p99)
- Throughput (req/sec)
- Error rate (%)
- CPU/Memory usage
- Database connections
- Kafka consumer lag

## Example
```
/load-test api --users=100 --duration=5m
/load-test kafka --rps=1000 --duration=10m
/load-test full --users=500 --ramp-up=2m
```
