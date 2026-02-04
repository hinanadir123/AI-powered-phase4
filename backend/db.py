from sqlmodel import create_engine, Session
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("WARNING: DATABASE_URL environment variable is not set")
    # For development purposes, use a SQLite database
    DATABASE_URL = "sqlite:///./todo_dev.db"
    print(f"Using development database: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=True,  # Enable SQL logging for debugging
    connect_args={
        "sslmode": "require",  # Required for Neon
        "channel_binding": "require",  # Required for Neon
        "connect_timeout": 10,
    }
)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    try:
        # Import models here to avoid circular imports
        from models import User, Task
        from sqlmodel import SQLModel
        print("Creating database tables...")
        SQLModel.metadata.create_all(engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise