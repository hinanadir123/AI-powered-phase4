# Scale

Scale application components up or down.

## Usage
```
/scale [service] [replicas]
```

## Arguments
- `service`: Service to scale (backend/frontend/worker)
- `replicas`: Number of replicas (or auto for autoscaling)

## What it does
1. Shows current replica count
2. Validates scaling request
3. Updates deployment
4. Monitors scaling progress
5. Verifies new pods are healthy
6. Configures autoscaling (HPA)

## Scaling Strategies

### Manual
- Set specific replica count
- Immediate scaling
- Fixed capacity

### Auto (HPA)
- CPU-based autoscaling
- Memory-based autoscaling
- Custom metrics
- Min/max replicas

## Autoscaling Configuration
- Target CPU: 70%
- Target Memory: 80%
- Min replicas: 2
- Max replicas: 10
- Scale up: +2 pods at a time
- Scale down: -1 pod at a time
- Cooldown: 5 minutes

## Example
```
/scale backend 5
/scale frontend 3
/scale worker auto --min=2 --max=10
/scale backend auto --cpu=70 --memory=80
/scale --status
```
