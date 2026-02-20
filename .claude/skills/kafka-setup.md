# Setup Kafka and Dapr

Setup event-driven infrastructure using Kafka (Redpanda/Strimzi) and Dapr for the Todo application.

## Usage
```
/kafka-setup
```

## What it does
Uses the kafka-dapr-engineer agent to:
1. Configure Kafka topics for task events and reminders
2. Create Dapr component YAML files (Pub/Sub, State Management, Jobs, Secrets)
3. Provide code examples for event publishing/consuming
4. Generate deployment instructions
5. Output comprehensive documentation (kafka-dapr-engineer.md)

## Example
```
/kafka-setup
```
