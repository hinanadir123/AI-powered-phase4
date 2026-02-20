# Integration Test

Run integration tests for the Todo AI Chatbot.

## Usage
```
/integration-test [suite]
```

## Arguments
- `suite` (optional): Test suite to run (e2e/api/database/kafka/all). Default: all

## What it does
1. **e2e**: End-to-end user workflow tests
2. **api**: API integration tests
3. **database**: Database integration tests
4. **kafka**: Event-driven integration tests
5. **all**: Complete integration test suite

Includes:
- User authentication flow
- Task CRUD operations
- AI chat functionality
- Event publishing/consuming
- Database transactions

## Example
```
/integration-test
/integration-test e2e
/integration-test kafka
```
