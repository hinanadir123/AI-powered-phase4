<!-- SYNC IMPACT REPORT
Version change: 2.1.0 -> 3.0.0
Modified principles: I-IX (updated for Phase III AI Chatbot specifics)
Added sections: X. MCP-First Architecture, XI. AI-Driven Interactions, XII. Statelessness Requirement
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/commands/*.md ✅ reviewed
- README.md ⚠ pending
Follow-up TODOs: None
-->

# Todo AI Chatbot - Phase 3 Constitution

## Purpose
This project extends the full-stack todo web application into an AI-powered conversational interface using MCP tools and OpenAI Agents SDK as part of Hackathon IV: The AI Revolution, Phase 3. The application provides natural language task management functionality through a chat interface, emphasizing intelligent parsing, stateless architecture, and seamless integration between AI agents and backend services.

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)
All development begins with comprehensive specifications before any code generation. Specifications must be refined iteratively until code produces correct output. The Agentic Dev Stack workflow (Spec → Plan → Tasks → Implement) must be strictly followed. Read specs before writing code. Do not guess missing behavior. If specs are unclear, stop and ask.

### II. Minimalist Implementation
Focus on the essential features only: Add, View, Update, Delete, and Mark Complete via natural language. No feature creep or additional functionality beyond the specified requirements. Embrace simplicity and YAGNI (You Aren't Gonna Need It) principles.

### III. Clean Code Standards
Code must adhere to PEP 8 guidelines (Python) and TypeScript/Next.js best practices with modular design, proper error handling for invalid inputs and edge cases, and clear separation of concerns. Functions and components should be focused and reusable where appropriate.

### IV. Modern Tech Stack (NON-NEGOTIABLE)
Use the specified technology stack exclusively:
- Frontend: OpenAI ChatKit (React/Next.js)
- Backend: FastAPI (Python), SQLModel
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth (JWT)
This ensures consistency and compatibility across the team.

### V. Persistent Storage
Implement task, conversation, and message storage using Neon Serverless PostgreSQL with proper data modeling and relationships. Data must persist across application restarts. Focus on database efficiency and proper indexing strategies.

### VI. Error Handling and Validation
Implement robust error handling for all user inputs, including validation of task titles (1-200 chars), descriptions (max 1000 chars), and proper handling of invalid task IDs. Provide clear error messages to users. Backend must return appropriate HTTP status codes. AI agent must gracefully handle ambiguous requests and tool failures.

### VII. Conversational Interface
Design an intuitive chat interface using OpenAI ChatKit, ensuring accessibility and usability. Implement proper loading states, error boundaries, and user feedback mechanisms. Display conversation history, task confirmations, and errors appropriately.

### VIII. Authentication-First Security
Implement secure user authentication using Better Auth on the frontend and JWT token verification on the backend. Every API request must include a valid JWT token in `Authorization: Bearer <token>`, otherwise return 401 Unauthorized. Backend extracts `user_id` from JWT. Never trust user_id from URL alone — always verify it matches the JWT's user_id. Users can only access their own tasks and conversations.

### IX. Multi-User Isolation
Each user should only see and modify THEIR OWN tasks and conversations. Implement proper authorization checks to ensure users cannot access or modify other users' data. Database queries must always filter by the authenticated user's ID. All API endpoints must enforce user isolation.

### X. MCP-First Architecture (NON-NEGOTIABLE)
All task operations must be exposed as MCP tools using the Official MCP SDK. The backend must integrate MCP tools as the primary interface for all data operations. This ensures standardized, interoperable, and discoverable service interfaces. All CRUD operations must go through MCP tools rather than direct database access.

### XI. AI-Driven Interactions
Implement conversational AI agent using OpenAI Agents SDK to interpret natural language and map user intents to appropriate MCP tools. The AI agent must handle multi-step tasks, tool chaining, and provide confirmation messages for all actions. Natural language processing should be robust enough to handle various ways users express their intentions.

### XII. Statelessness Requirement
Maintain a stateless backend design where all conversation and task state is persisted in the database. Any server instance must be able to process requests independently. This enables horizontal scaling and resilience. The AI agent state should be reconstructed from database records as needed.

## Non-Negotiables
- Use the specified tech stack: OpenAI ChatKit, FastAPI (Python), SQLModel, Neon Serverless PostgreSQL, Better Auth, OpenAI Agents SDK, Official MCP SDK
- Expose all task operations as MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- Implement stateless backend with all state persisted in database
- Every API request must have valid JWT → else return 401
- Never trust user_id from URL alone — always verify it matches the JWT's user_id
- Multi-user support → each user only sees & modifies THEIR OWN tasks and conversations
- Proper validation: title 1-200 chars, description max 1000 chars
- Conversational interface with loading states and error handling
- Use Qwen Code for code generation from specs
- Include comprehensive error handling for invalid inputs and unauthorized access
- All MCP tool calls via FastAPI backend
- Frontend handles login using Better Auth
- All 5 basic todo features must work via natural language for Phase III completion
- Auth must be enforced everywhere
- Data must persist in database
- Multi-user isolation must be verified
- MCP tools must be properly integrated with AI agent
- Conversations and messages must be persisted in database
- Stateless architecture must be maintained

## Hierarchy and Updates
This Constitution document represents the highest authority in project decisions, superseding all other practices and guidelines. All development activities must comply with these principles. Amendments to this Constitution require explicit documentation of changes, approval from project stakeholders, and a migration plan for existing implementations. All pull requests and code reviews must verify constitutional compliance before merging.

**Version**: 3.0.0 | **Ratified**: 2026-02-03 | **Last Amended**: 2026-02-03