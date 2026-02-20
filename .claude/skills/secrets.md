# Secrets

Manage secrets and sensitive configuration.

## Usage
```
/secrets [operation] [secret-name]
```

## Arguments
- `operation`: Operation (create/list/update/delete/rotate/export)
- `secret-name` (optional): Secret name

## What it does

### create
- Creates new Kubernetes secret
- Encrypts sensitive data
- Sets up secret references

### list
- Lists all secrets
- Shows secret metadata
- Displays usage in pods

### update
- Updates secret values
- Triggers pod restarts if needed
- Validates secret format

### delete
- Removes secret
- Checks for dependencies
- Cleans up references

### rotate
- Rotates secret values
- Updates all references
- Zero-downtime rotation

### export
- Exports secrets to file (encrypted)
- Backs up secrets
- Migrates between environments

## Secret Types
- Database credentials
- API keys
- JWT secrets
- OAuth tokens
- TLS certificates
- Kafka credentials

## Example
```
/secrets list
/secrets create db-password --value="secure123"
/secrets rotate api-key
/secrets export --env=prod --output=secrets.enc
```
