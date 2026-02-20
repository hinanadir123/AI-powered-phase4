# Backup

Backup application data and configuration.

## Usage
```
/backup [component] [options]
```

## Arguments
- `component`: Component to backup (all/database/state/config/volumes)
- `options` (optional): Backup options (destination/schedule)

## What it does

### database
- Backs up PostgreSQL database
- Creates SQL dump
- Compresses backup
- Uploads to storage

### state
- Backs up Dapr state store
- Exports state data
- Preserves metadata

### config
- Backs up ConfigMaps
- Exports Secrets (encrypted)
- Saves Helm values
- Archives Kubernetes manifests

### volumes
- Backs up persistent volumes
- Creates snapshots
- Copies to remote storage

## Backup Strategies

### Full Backup
- Complete data backup
- All components included
- Larger size, slower

### Incremental
- Only changed data
- Faster, smaller
- Requires full backup base

### Differential
- Changes since last full backup
- Medium size and speed
- Easier restore than incremental

## Storage Options
- Local filesystem
- Cloud storage (S3, Azure Blob, GCS)
- Network storage (NFS)
- Backup service (Velero)

## Scheduling
- Manual: On-demand backups
- Hourly: Every hour
- Daily: Once per day (2 AM)
- Weekly: Sunday 2 AM
- Monthly: 1st of month

## Example
```
/backup all
/backup database --destination=s3://backups
/backup config --schedule=daily
/backup volumes --incremental
```
