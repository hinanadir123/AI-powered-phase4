#!/bin/bash
# Kafka Topics Setup Script
# Creates required Kafka topics for the Todo AI Chatbot

echo "Creating Kafka topics..."

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
sleep 5

# Create task-events topic
docker exec redpanda rpk topic create task-events \
  --brokers localhost:9092 \
  --partitions 3 \
  --replicas 1 \
  --topic-config retention.ms=604800000

echo "✓ Created task-events topic"

# Create reminders topic
docker exec redpanda rpk topic create reminders \
  --brokers localhost:9092 \
  --partitions 3 \
  --replicas 1 \
  --topic-config retention.ms=604800000

echo "✓ Created reminders topic"

# Create task-updates topic
docker exec redpanda rpk topic create task-updates \
  --brokers localhost:9092 \
  --partitions 3 \
  --replicas 1 \
  --topic-config retention.ms=604800000

echo "✓ Created task-updates topic"

# Create dead letter queue topics
docker exec redpanda rpk topic create task-events-dlq \
  --brokers localhost:9092 \
  --partitions 1 \
  --replicas 1

echo "✓ Created task-events-dlq topic"

docker exec redpanda rpk topic create reminders-dlq \
  --brokers localhost:9092 \
  --partitions 1 \
  --replicas 1

echo "✓ Created reminders-dlq topic"

# List all topics
echo ""
echo "All Kafka topics:"
docker exec redpanda rpk topic list --brokers localhost:9092

echo ""
echo "✅ Kafka topics setup complete!"
echo "Access Redpanda Console at: http://localhost:8080"
