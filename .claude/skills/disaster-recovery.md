# Disaster Recovery

Setup and test disaster recovery procedures.

## Usage
```
/disaster-recovery [operation]
```

## Arguments
- `operation`: Operation (setup/test/execute/status)

## What it does
1. **setup**: Configures disaster recovery plan
   - Backup schedules
   - Replication strategies
   - Recovery procedures
2. **test**: Runs DR drills and validates recovery
3. **execute**: Executes disaster recovery plan
4. **status**: Shows DR readiness and last test results

## Example
```
/disaster-recovery setup
/disaster-recovery test
/disaster-recovery status
```
