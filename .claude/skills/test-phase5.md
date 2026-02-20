# Test Phase 5

Run comprehensive tests for Phase 5 Todo AI Chatbot.

## Usage
```
/test-phase5 [test-type]
```

## Arguments
- `test-type` (optional): Test type (all/unit/integration/e2e/load/kafka/dapr). Default: all

## What it does

### unit
- Runs unit tests for backend and frontend
- Tests individual components
- Validates business logic

### integration
- Tests API endpoints
- Validates database operations
- Tests Dapr integration

### e2e
- End-to-end user flows
- Tests recurring tasks
- Validates reminders
- Tests search and filters

### load
- Performance testing
- Stress testing
- Scalability validation

### kafka
- Tests event publishing
- Validates event consumption
- Tests dead letter queues
- Validates message ordering

### dapr
- Tests Pub/Sub components
- Validates State Store
- Tests Jobs API
- Validates Secret Store

## Test Coverage
- ✅ Recurring tasks creation
- ✅ Reminder scheduling
- ✅ Priority and tags
- ✅ Search functionality
- ✅ Filter and sort
- ✅ Event publishing
- ✅ Event consumption
- ✅ Dapr components
- ✅ Error handling
- ✅ Performance

## Example
```
/test-phase5
/test-phase5 integration
/test-phase5 kafka
/test-phase5 e2e
```
