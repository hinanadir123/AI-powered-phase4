# Clean Resources

Clean up Kubernetes resources and Docker artifacts.

## Usage
```
/clean [target]
```

## Arguments
- `target` (optional): What to clean (pods/images/volumes/all). Default: prompts for selection

## What it does
1. **pods**: Removes failed/completed pods
2. **images**: Cleans unused Docker images
3. **volumes**: Removes unused persistent volumes
4. **all**: Comprehensive cleanup

Shows what will be deleted and asks for confirmation before proceeding.

## Example
```
/clean
/clean pods
/clean images
```
