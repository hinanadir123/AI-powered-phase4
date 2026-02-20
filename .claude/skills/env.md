# Environment

Manage environments and configurations.

## Usage
```
/env [operation] [environment]
```

## Arguments
- `operation`: Operation (list/create/switch/delete/sync/diff)
- `environment` (optional): Environment name (dev/staging/prod)

## What it does

### list
- Lists all environments
- Shows current environment
- Displays configuration differences

### create
- Creates new environment
- Copies configuration from template
- Sets up namespace and resources

### switch
- Switches kubectl context
- Updates environment variables
- Validates connectivity

### delete
- Removes environment
- Cleans up resources
- Archives configuration

### sync
- Syncs configuration between environments
- Updates secrets and configmaps
- Validates changes

### diff
- Shows configuration differences
- Compares environments
- Highlights changes

## Environments

### Development (dev)
- Local or cloud cluster
- Debug mode enabled
- Mock external services
- Relaxed security

### Staging
- Production-like environment
- Real external services
- Performance testing
- Security hardening

### Production (prod)
- Live environment
- High availability
- Monitoring and alerts
- Strict security

## Configuration Management
- Environment variables
- Secrets
- ConfigMaps
- Helm values
- Feature flags

## Example
```
/env list
/env create staging
/env switch prod
/env diff dev staging
/env sync dev staging --dry-run
```
