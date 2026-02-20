from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database and create tables
    # For Dapr integration, we still initialize the DB for compatibility
    # but most state management will be handled by Dapr State Store

    # Import here to avoid circular imports during startup
    try:
        from db import create_db_and_tables
        create_db_and_tables()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        print("Make sure your DATABASE_URL is correctly set in the .env file")

    # Initialize Dapr event integration
    try:
        from event_publisher import task_event_integration
        print("Dapr event integration initialized")
    except Exception as e:
        print(f"Warning: Could not initialize Dapr event integration: {e}")

    yield

app = FastAPI(lifespan=lifespan, title="Todo Backend API with Dapr Integration", version="2.0.0")

# Add CORS middleware with proper configuration for credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Traceparent"],
)

# Include the task and auth routes
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router

app.include_router(tasks_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {
        "message": "Todo Backend API with Dapr Integration is running!",
        "features": [
            "Event-driven architecture with Kafka",
            "Dapr State Management",
            "Task Reminders and Recurring Tasks",
            "Advanced search, filter, and sort capabilities"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "dapr_integration": "active"}

@app.get("/dapr/subscribe")
def dapr_subscribe():
    """
    Dapr subscription endpoint - tells Dapr which topics this service wants to subscribe to
    """
    subscriptions = [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/dapr/reminders",
            "metadata": {
                "consumerGroup": "todo-api-reminders"
            },
            "deadLetterTopic": "reminders-dlq"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-updates",
            "route": "/dapr/task-updates",
            "metadata": {
                "consumerGroup": "todo-api-task-updates"
            },
            "deadLetterTopic": "task-updates-dlq"
        }
    ]
    return subscriptions

@app.post("/dapr/reminders")
async def handle_reminders(cloud_event: dict):
    """
    Handle reminder events from Dapr Pub/Sub
    """
    print(f"Received reminder event: {cloud_event.get('type', 'unknown')}")
    # Process reminder notification logic
    return {"status": "processed"}

@app.post("/dapr/task-updates")
async def handle_task_updates(cloud_event: dict):
    """
    Handle task update events from Dapr Pub/Sub
    """
    print(f"Received task update event: {cloud_event.get('type', 'unknown')}")
    # Process task update notification logic
    return {"status": "processed"}