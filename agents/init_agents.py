"""
Agent Components Initialization
This module initializes all the agent-generated components for Step 2
Task: Initialize advanced feature components
"""
from fastapi import FastAPI
from agents.api_tasks_advanced import router as advanced_tasks_router
from agents.api_endpoints import router as advanced_endpoints_router


def register_advanced_features(app: FastAPI, user_id_prefix: str = "/api/{user_id}"):
    """
    Register all advanced feature API routes with the main application
    """
    # Register advanced tasks endpoints
    app.include_router(advanced_tasks_router, prefix=f"{user_id_prefix}")

    # Register advanced endpoints
    app.include_router(advanced_endpoints_router, prefix=f"{user_id_prefix}")

    print("Registered advanced feature endpoints")

    return app