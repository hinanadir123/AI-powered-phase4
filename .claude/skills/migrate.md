# Run Migration

Run database migrations for the Todo AI Chatbot.

## Usage
```
/migrate [operation] [version]
```

## Arguments
- `operation`: Migration operation (up/down/status/create). Default: up
- `version` (optional): Target version for migration

## What it does
1. **up**: Applies pending migrations
2. **down**: Rolls back migrations
3. **status**: Shows migration status
4. **create**: Creates new migration file

## Example
```
/migrate
/migrate up
/migrate down 1
/migrate status
/migrate create add_priority_field
```
