# Port Forward

Forward ports from Kubernetes pods to local machine.

## Usage
```
/port-forward [service] [local-port]
```

## Arguments
- `service` (optional): Service to forward (backend/frontend/database/redis). Default: prompts for selection
- `local-port` (optional): Local port to use. Default: same as service port

## What it does
1. Lists available services
2. Sets up port forwarding
3. Shows connection details
4. Keeps connection alive
5. Provides cleanup instructions

## Example
```
/port-forward
/port-forward backend 8080
/port-forward database 5432
```
