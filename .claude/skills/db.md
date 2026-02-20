# Database Operations

Manage database operations for Todo AI Chatbot.

## Usage
```
/db [operation] [options]
```

## Arguments
- `operation`: Operation type (migrate/seed/backup/restore/query/status)
- `options` (optional): Operation-specific options

## What it does

### migrate
- Runs database migrations
- Shows migration status
- Rollback migrations

### seed
- Seeds database with test data
- Creates sample tasks and users
- Populates reference data

### backup
- Creates database backup
- Exports to file or cloud storage
- Schedules automatic backups

### restore
- Restores from backup
- Point-in-time recovery
- Validates restored data

### query
- Executes SQL queries
- Shows table schemas
- Analyzes query performance

### status
- Shows connection status
- Displays table sizes
- Monitors active connections

## Example
```
/db migrate
/db seed --env=dev
/db backup --output=backup.sql
/db restore --file=backup.sql
/db query "SELECT * FROM tasks LIMIT 10"
/db status
```
