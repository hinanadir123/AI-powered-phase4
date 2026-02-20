# Environment Config

Manage environment configurations for different deployment stages.

## Usage
```
/env-config [environment] [operation]
```

## Arguments
- `environment`: Target environment (dev/staging/prod)
- `operation` (optional): Operation (show/edit/sync/validate). Default: show

## What it does
1. **show**: Displays current environment configuration
2. **edit**: Opens configuration for editing
3. **sync**: Syncs configuration to cluster
4. **validate**: Validates configuration values

## Example
```
/env-config dev
/env-config prod show
/env-config staging sync
/env-config prod validate
```
