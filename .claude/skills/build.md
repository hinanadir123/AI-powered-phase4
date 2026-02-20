# Build Docker Images

Build and push Docker images for the Todo AI Chatbot application.

## Usage
```
/build [component] [tag]
```

## Arguments
- `component` (optional): Component to build (backend/frontend/all). Default: all
- `tag` (optional): Image tag. Default: latest

## What it does
1. Builds Docker images for specified components
2. Tags images appropriately
3. Optionally pushes to container registry
4. Shows build summary

## Example
```
/build
/build backend v1.2.3
/build frontend latest
```
