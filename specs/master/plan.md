# Implementation Plan: Phase II - Full-Stack Todo Application

**Branch**: `phase2-web` | **Date**: 2026-01-28 | **Spec**: [specs/master/spec.md]
**Input**: Feature specification from `/specs/master/spec.md`

## Summary

Implementation of a full-stack web application with Next.js frontend and FastAPI backend, featuring user authentication, task CRUD operations, and secure multi-user isolation. The application will use Neon Serverless PostgreSQL for persistence and Better Auth for authentication, with JWT verification on the backend to ensure secure access control.

## Technical Context

**Language/Version**: Python 3.12, TypeScript 5.3, JavaScript ES2022
**Primary Dependencies**: Next.js 16+ (App Router), FastAPI 0.115+, SQLModel 0.0.22, Neon PostgreSQL, Better Auth
**Storage**: Neon Serverless PostgreSQL with SQLModel ORM
**Testing**: pytest for backend, Jest/React Testing Library for frontend (future)
**Target Platform**: Web application (client-server architecture)
**Project Type**: Full-stack web application with separate frontend and backend
**Performance Goals**: Sub-second API response times, responsive UI with loading states
**Constraints**: JWT authentication required for all API endpoints, user isolation enforcement, 1-200 character limit for task titles
**Scale/Scope**: Multi-user support with individual task isolation, horizontal scaling via Neon Serverless

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Spec-Driven Development: Following established specs and contracts
- ✅ Minimalist Implementation: Focusing only on required CRUD functionality
- ✅ Clean Code Standards: Using established patterns for Next.js and FastAPI
- ✅ Modern Tech Stack: Using specified technologies (Next.js, FastAPI, SQLModel, etc.)
- ✅ Persistent Storage: Implementing with Neon PostgreSQL as required
- ✅ Error Handling and Validation: Following spec requirements for validation
- ✅ Web-First Interface: Building responsive web interface with Next.js App Router
- ✅ Authentication-First Security: Implementing JWT verification and auth checks
- ✅ Multi-User Isolation: Enforcing user isolation at the API level

## Project Structure

### Documentation (this feature)

```text
specs/master/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI application entry point
├── db.py                # Database connection and session management
├── models.py            # SQLModel database models
├── schemas.py           # Pydantic request/response schemas
├── dependencies.py      # JWT authentication dependencies
├── routes/
│   ├── __init__.py
│   └── tasks.py         # Task API routes
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables

frontend/
├── app/
│   ├── layout.tsx       # Root layout with AuthProvider
│   ├── page.tsx         # Main dashboard page
│   ├── login/
│   │   └── page.tsx     # Login page
│   └── signup/
│       └── page.tsx     # Signup page
├── components/
│   ├── TaskList.tsx     # Task list component
│   ├── TaskFormModal.tsx # Task creation/editing modal
│   ├── AddTaskButton.tsx # Floating add task button
│   └── EmptyState.tsx   # Empty state component
├── context/
│   └── AuthContext.tsx  # Authentication context
├── lib/
│   └── api.ts           # API client for backend communication
├── package.json         # Node.js dependencies
└── .env.local           # Frontend environment variables
```

**Structure Decision**: Web application with separate frontend and backend services following the specified architecture. Backend uses FastAPI with SQLModel for API and database operations, while frontend uses Next.js with App Router for the user interface.

## Phase 0: Outline & Research

1. **Tech Stack Confirmation**
   - Task: "Confirm Next.js, FastAPI, SQLModel, Neon PostgreSQL implementation approach"
   - Task: "Validate Better Auth and JWT token verification requirements"

2. **Security Requirements Analysis**
   - Task: "Research JWT verification patterns in FastAPI"
   - Task: "Validate user isolation implementation strategies"

## Phase 1: Design & Contracts

1. **Data Model Implementation**
   - Task: "Implement User and Task models with SQLModel following data-model.md"
   - Task: "Define relationships and constraints per specifications"

2. **API Contract Implementation**
   - Task: "Create API endpoints matching task-api-contract.md specifications"
   - Task: "Implement JWT authentication middleware"

## Detailed Step-by-Step Plan

### Phase 1: Backend Implementation

#### Step 1.1: Database Layer Setup
- Description: Set up database connection using SQLModel and Neon PostgreSQL
- Reference specs: @specs/master/data-model.md
- Files to create/edit: `backend/db.py`
- Complexity: Medium
- Dependencies: None
- Test command: `python -c "from db import engine; print('DB connected')"`

#### Step 1.2: Data Models
- Description: Create User and Task models with proper relationships
- Reference specs: @specs/master/data-model.md
- Files to create/edit: `backend/models.py`
- Complexity: Medium
- Dependencies: Step 1.1
- Test command: `python -c "from models import User, Task; print('Models loaded')"`

#### Step 1.3: API Request/Response Schemas
- Description: Define Pydantic schemas for API validation
- Reference specs: @specs/master/contracts/task-api-contract.md
- Files to create/edit: `backend/schemas.py`
- Complexity: Easy
- Dependencies: Step 1.2
- Test command: `python -c "from schemas import TaskCreate; print('Schemas loaded')"`

#### Step 1.4: Authentication Dependencies
- Description: Implement JWT verification and user extraction
- Reference specs: @specs/master/contracts/task-api-contract.md
- Files to create/edit: `backend/dependencies.py`
- Complexity: Hard
- Dependencies: Step 1.3
- Test command: `python -c "from dependencies import verify_token; print('Auth deps loaded')"`

#### Step 1.5: Task API Routes
- Description: Implement all required task endpoints with auth checks
- Reference specs: @specs/master/contracts/task-api-contract.md
- Files to create/edit: `backend/routes/tasks.py`
- Complexity: Hard
- Dependencies: Steps 1.1-1.4
- Test command: `python -c "from routes.tasks import router; print('Routes loaded')"`

#### Step 1.6: Main Application
- Description: Create FastAPI app with routes and startup configuration
- Reference specs: @specs/master/contracts/task-api-contract.md
- Files to create/edit: `backend/main.py`
- Complexity: Medium
- Dependencies: Steps 1.1-1.5
- Test command: `uvicorn main:app --reload`

### Phase 2: Frontend Integration

#### Step 2.1: API Client Setup
- Description: Create API client to communicate with backend
- Reference specs: @specs/master/contracts/task-api-contract.md
- Files to create/edit: `frontend/lib/api.ts`
- Complexity: Medium
- Dependencies: Backend running
- Test command: `npm run dev` and test API calls

#### Step 2.2: Frontend Authentication Integration
- Description: Update frontend to send JWT tokens with API requests
- Reference specs: @specs/master/contracts/task-api-contract.md
- Files to create/edit: `frontend/lib/api.ts`, `frontend/context/AuthContext.tsx`
- Complexity: Medium
- Dependencies: Step 2.1
- Test command: Test login/logout flow with API calls

#### Step 2.3: Task CRUD Components Update
- Description: Connect existing components to backend API
- Reference specs: @specs/master/contracts/task-api-contract.md
- Files to create/edit: `frontend/components/TaskList.tsx`, `frontend/components/TaskFormModal.tsx`
- Complexity: Hard
- Dependencies: Step 2.2
- Test command: Test full CRUD flow in browser

### Phase 3: Testing and Integration

#### Step 3.1: End-to-End Testing
- Description: Test complete user flow from signup to task management
- Reference specs: @specs/master/spec.md
- Files to create/edit: Various frontend/backend files as needed
- Complexity: Medium
- Dependencies: All previous steps
- Test command: Manual testing of signup → login → CRUD operations

#### Step 3.2: Error Handling and Validation
- Description: Implement proper error handling and validation feedback
- Reference specs: @specs/master/spec.md
- Files to create/edit: Various frontend/backend files
- Complexity: Medium
- Dependencies: Step 3.1
- Test command: Test error conditions and validation

## Next Action Recommendation

Start with **Step 1.1: Database Layer Setup** as it's the foundation for all backend functionality. This step has no dependencies and will establish the database connection that the rest of the backend will rely on. Once the database layer is confirmed working, proceed to Step 1.2 for data models.
