# Kafka Management

Manage Kafka topics and messages for Todo AI Chatbot.

## Usage
```
/kafka [operation] [topic]
```

## Arguments
- `operation`: Operation (create/list/describe/consume/produce/delete/reset)
- `topic` (optional): Topic name

## What it does

### create
- Creates new Kafka topic
- Configures partitions and replication
- Sets retention policies

### list
- Lists all topics
- Shows topic details
- Displays consumer groups

### describe
- Shows topic configuration
- Displays partition info
- Shows consumer lag

### consume
- Consumes messages from topic
- Filters by key or value
- Shows message metadata

### produce
- Produces test messages
- Validates message format
- Tests event flow

### delete
- Deletes topic
- Removes consumer groups
- Cleans up resources

### reset
- Resets consumer offsets
- Clears topic data
- Reprocesses messages

## Topics
- `task-events`: Task CRUD events
- `reminders`: Reminder notifications
- `task-events-dlq`: Dead letter queue
- `reminders-dlq`: Reminder DLQ

## Example
```
/kafka list
/kafka create task-events --partitions=3
/kafka describe task-events
/kafka consume task-events --follow
/kafka produce task-events --message='{"type":"created"}'
/kafka reset task-events --to-earliest
```
