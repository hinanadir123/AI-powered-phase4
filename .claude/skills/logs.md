# View Logs

View and filter logs from Kubernetes pods.

## Usage
```
/logs [service] [options]
```

## Arguments
- `service` (optional): Service name (backend/frontend/worker/kafka/dapr). Default: prompts for selection
- `options` (optional): Log options (follow/tail/since/grep)

## What it does
1. Lists available pods
2. Streams logs in real-time
3. Filters by keywords or patterns
4. Shows logs from multiple containers
5. Supports log aggregation
6. Exports logs to file

## Options
- `--follow` or `-f`: Stream logs in real-time
- `--tail=N`: Show last N lines
- `--since=TIME`: Show logs since time (e.g., 1h, 30m)
- `--grep=PATTERN`: Filter logs by pattern
- `--container=NAME`: Specific container in pod

## Example
```
/logs backend --follow
/logs frontend --tail=100
/logs worker --since=1h --grep=ERROR
```
