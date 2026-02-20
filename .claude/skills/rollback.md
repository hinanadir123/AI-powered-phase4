# Rollback

Rollback deployments to previous versions.

## Usage
```
/rollback [service] [version]
```

## Arguments
- `service`: Service to rollback (backend/frontend/all)
- `version` (optional): Target version or revision. Default: previous version

## What it does
1. Shows deployment history
2. Identifies current version
3. Validates target version
4. Performs rollback
5. Monitors rollback progress
6. Runs health checks
7. Verifies rollback success

## Rollback Strategies

### Instant
- Immediate rollback
- No gradual transition
- Use for critical issues

### Gradual
- Canary rollback
- Progressive traffic shift
- Monitors during rollback

### Blue-Green
- Switches to previous environment
- Zero downtime
- Easy to revert

## Safety Checks
- Validates target version exists
- Checks database compatibility
- Verifies configuration
- Tests health endpoints
- Monitors error rates

## Example
```
/rollback backend
/rollback frontend --to-version=1.2.3
/rollback all --strategy=gradual
/rollback backend --dry-run
```
