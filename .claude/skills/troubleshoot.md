# Troubleshoot

Troubleshoot common issues with the Todo AI Chatbot deployment.

## Usage
```
/troubleshoot [issue]
```

## Arguments
- `issue` (optional): Specific issue category (pods/network/storage/performance). Default: auto-detect

## What it does
1. Runs diagnostic checks
2. Identifies common issues:
   - Pods not starting
   - Network connectivity problems
   - Storage/PVC issues
   - Performance bottlenecks
   - Configuration errors
3. Provides actionable solutions
4. Shows relevant logs and events

## Example
```
/troubleshoot
/troubleshoot pods
/troubleshoot network
```
