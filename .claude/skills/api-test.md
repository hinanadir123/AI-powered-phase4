# API Test

Test API endpoints for the Todo AI Chatbot.

## Usage
```
/api-test [endpoint] [method]
```

## Arguments
- `endpoint` (optional): Specific endpoint to test. Default: all endpoints
- `method` (optional): HTTP method (GET/POST/PUT/DELETE). Default: all methods

## What it does
1. Runs API endpoint tests
2. Validates request/response schemas
3. Tests authentication and authorization
4. Checks error handling
5. Validates rate limiting
6. Generates API test report

## Example
```
/api-test
/api-test /api/tasks GET
/api-test /api/chat POST
```
