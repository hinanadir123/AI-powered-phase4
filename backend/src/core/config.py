from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    database_url: str = "sqlite:///./todo_app.db"
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Better Auth settings
    better_auth_secret: str = "your-better-auth-secret"
    
    # OpenAI settings
    openai_api_key: str = ""
    
    # MCP settings
    mcp_server_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"


settings = Settings()