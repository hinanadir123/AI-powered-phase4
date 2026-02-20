# Helm Operations

Manage Helm releases for the Todo AI Chatbot.

## Usage
```
/helm [operation] [release]
```

## Arguments
- `operation`: Helm operation (list/upgrade/uninstall/history/rollback/values)
- `release` (optional): Release name. Default: prompts for selection

## What it does
1. **list**: Shows all Helm releases
2. **upgrade**: Upgrades release with new values
3. **uninstall**: Removes Helm release
4. **history**: Shows release history
5. **rollback**: Rolls back to previous revision
6. **values**: Displays current values

## Example
```
/helm list
/helm upgrade todo-backend
/helm history todo-frontend
/helm rollback todo-backend 3
```
