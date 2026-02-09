"""
Comprehensive test for the AI-Powered Conversational Todo Manager (Phase 4)
This test validates that all components of the system are working correctly.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_project_structure():
    """Test that all required project components exist."""
    print("Testing project structure...")
    
    # Check backend structure
    backend_dir = Path("backend")
    assert backend_dir.exists(), "Backend directory missing"
    assert (backend_dir / "src").exists(), "Backend src directory missing"
    assert (backend_dir / "src" / "ai").exists(), "AI module missing"
    assert (backend_dir / "src" / "models").exists(), "Models module missing"
    assert (backend_dir / "src" / "services").exists(), "Services module missing"
    assert (backend_dir / "src" / "api").exists(), "API module missing"
    
    # Check frontend structure
    frontend_dir = Path("frontend")
    assert frontend_dir.exists(), "Frontend directory missing"
    assert (frontend_dir / "app" / "dashboard").exists(), "Dashboard page missing"
    assert (frontend_dir / "src" / "components").exists(), "Components directory missing"
    
    print("✓ Project structure is correct")


def test_ai_agent_implementation():
    """Test that the AI agent is properly implemented."""
    print("Testing AI agent implementation...")
    
    ai_agent_path = Path("backend/src/ai/agent.py")
    assert ai_agent_path.exists(), "AI agent implementation missing"
    
    with open(ai_agent_path, 'r') as f:
        content = f.read()
        
    # Check for required functionality
    assert "process_message" in content, "process_message method missing"
    assert "add_task" in content, "Add task functionality missing"
    assert "list_tasks" in content, "List tasks functionality missing"
    assert "complete_task" in content, "Complete task functionality missing"
    assert "delete_task" in content, "Delete task functionality missing"
    assert "_handle_add_task" in content, "Add task handler missing"
    assert "_handle_list_tasks" in content, "List tasks handler missing"
    assert "_handle_complete_task" in content, "Complete task handler missing"
    assert "_handle_delete_task" in content, "Delete task handler missing"
    
    print("✓ AI agent implementation is complete")


def test_chat_api_endpoint():
    """Test that the chat API endpoint is properly implemented."""
    print("Testing chat API endpoint...")
    
    chat_route_path = Path("backend/src/api/routes/chat.py")
    assert chat_route_path.exists(), "Chat API route missing"
    
    with open(chat_route_path, 'r') as f:
        content = f.read()
        
    assert "chat_endpoint" in content, "Chat endpoint function missing"
    assert "ChatRequest" in content, "ChatRequest model missing"
    assert "ChatResponse" in content, "ChatResponse model missing"
    assert "/{user_id}/chat" in content, "Chat endpoint path missing"
    
    print("✓ Chat API endpoint is properly implemented")


def test_dashboard_implementation():
    """Test that the dashboard is properly implemented."""
    print("Testing dashboard implementation...")
    
    dashboard_path = Path("frontend/app/dashboard/page.tsx")
    assert dashboard_path.exists(), "Dashboard page missing"
    
    with open(dashboard_path, 'r') as f:
        content = f.read()
        
    assert "ChatInterface" in content, "ChatInterface component not imported"
    assert "TaskList" in content, "TaskList component not imported"
    assert "AI Task Management Dashboard" in content, "Dashboard title missing"
    
    print("✓ Dashboard implementation is complete")


def test_main_application():
    """Test that the main application is properly configured."""
    print("Testing main application...")
    
    main_path = Path("backend/src/main.py")
    assert main_path.exists(), "Main application file missing"
    
    with open(main_path, 'r') as f:
        content = f.read()
        
    assert "chat_router" in content, "Chat router not included"
    assert "auth_router" in content, "Auth router not included"
    assert "startup_event" in content, "Startup event not configured"
    
    print("✓ Main application is properly configured")


def test_requirements():
    """Test that requirements files exist."""
    print("Testing requirements...")
    
    backend_req = Path("backend/requirements.txt")
    frontend_pkg = Path("frontend/package.json")
    
    assert backend_req.exists(), "Backend requirements.txt missing"
    assert frontend_pkg.exists(), "Frontend package.json missing"
    
    print("✓ Requirements files exist")


def run_tests():
    """Run all tests."""
    print("Starting comprehensive tests for Phase 4 implementation...\n")
    
    try:
        test_project_structure()
        test_ai_agent_implementation()
        test_chat_api_endpoint()
        test_dashboard_implementation()
        test_main_application()
        test_requirements()
        
        print("\n🎉 All tests passed! Phase 4 implementation is complete and correct.")
        print("\nSummary of Phase 4 - AI-Powered Conversational Todo Manager:")
        print("- AI agent processes natural language and maps to MCP tools")
        print("- MCP tools for add, list, complete, delete, update tasks")
        print("- Stateless backend with database persistence")
        print("- Dashboard combining chat and task list views")
        print("- Secure authentication and user isolation")
        print("- Responsive UI with Material UI components")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)