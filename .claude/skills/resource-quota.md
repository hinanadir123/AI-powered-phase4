# Resource Quota

Manage resource quotas and limits for the Todo AI Chatbot.

## Usage
```
/resource-quota [operation] [namespace]
```

## Arguments
- `operation`: Operation (show/set/update/delete)
- `namespace` (optional): Target namespace. Default: current namespace

## What it does
1. **show**: Displays current resource quotas and usage
2. **set**: Creates new resource quota
3. **update**: Updates existing quota
4. **delete**: Removes resource quota

Manages:
- CPU and memory limits
- Pod count limits
- Storage quotas
- Service limits

## Example
```
/resource-quota show
/resource-quota set todo-app
/resource-quota update todo-app
```
