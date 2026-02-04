---
id: 1
title: Update Constitution
stage: constitution
date: 2026-02-03
surface: agent
model: Qwen
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["constitution", "todo-chatbot", "phase3"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

```
---
description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent templates stay in sync.
handoffs: 
  - label: Build Specification
    agent: sp.specify
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`. This file is a TEMPLATE containing placeholder tokens in square brackets (e.g. `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`). Your job is to (a) collect/derive concrete values, (b) fill the template precisely, and (c) propagate any amendments across dependent artifacts.

Follow this execution flow:

1. Load the existing constitution template at `.specify/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If user input (conversation) supplies a value, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `.specify/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `.specify/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `.specify/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `.specify/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `.specify/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - New version and bump rationale.
   - Any files flagged for manual follow-up.
   - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.specify/memory/constitution.md` file.

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record) using agent‑native tools when possible.

1) Determine Stage
   - Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate Title and Determine Routing:
   - Generate Title: 3–7 words (slug for filename)
   - Route is automatically determined by stage:
     - `constitution` → `history/prompts/constitution/`
     - Feature stages → `history/prompts/<feature-name>/` (spec, plan, tasks, red, green, refactor, explainer, misc)
     - `general` → `history/prompts/general/`

3) Create and Fill PHR (Shell first; fallback agent‑native)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Open the file and fill remaining placeholders (YAML + body), embedding full PROMPT_TEXT (verbatim) and concise RESPONSE_TEXT.
   - If the script fails:
     - Read `.specify/templates/phr-template.prompt.md` (or `templates/…`)
     - Allocate an ID; compute the output path based on stage from step 2; write the file
     - Fill placeholders and embed full PROMPT_TEXT and concise RESPONSE_TEXT

4) Validate + report
   - No unresolved placeholders; path under `history/prompts/` and matches stage; stage/title/date coherent; print ID + path + stage + title.
   - On failure: warn, don't block. Skip only for `/sp.phr`.

/sp.constitution # Phase III Specification Constitution – Todo AI Chatbot

**Project:** Todo AI Chatbot  
**Phase:** III – AI-Powered Conversational Todo Manager  
**Objective:** Implement a natural language AI chatbot that manages todos via MCP tools, integrating ChatKit UI, FastAPI backend, AI agents, and database persistence.

---

## 1. Project Overview
- Extend existing Todo Console and Web apps (Phase I & II)  
- Provide full conversational interface to manage tasks  
- Stateless backend using MCP tools for task operations  
- Persist conversations, messages, and task states in database  
- Use OpenAI Agents SDK to parse user messages and call MCP tools  
- Deploy frontend via ChatKit with domain allowlist  

---

## 2. Technology Stack

| Component          | Technology                               |
|-------------------|-----------------------------------------|
| Frontend          | OpenAI ChatKit (React/Next.js)          |
| Backend           | Python FastAPI                           |
| AI Framework      | OpenAI Agents SDK                        |
| MCP Server        | Official MCP SDK                         |
| ORM               | SQLModel                                 |
| Database          | Neon Serverless PostgreSQL               |
| Authentication    | Better Auth                              |

---

## 3. Spec Breakdown

### Spec 1: MCP Tools & Backend Integration
**Objective:** Build MCP server exposing task operations as tools and integrate with FastAPI backend.  

**Components & Tasks:**
- MCP server setup using Official MCP SDK  
- Implement the following tools:
  - `add_task(user_id, title, description)`  
  - `list_tasks(user_id, status)`  
  - `complete_task(user_id, task_id)`  
  - `delete_task(user_id, task_id)`  
  - `update_task(user_id, task_id, title?, description?)`  
- Create FastAPI chat endpoint: `POST /api/{user_id}/chat`  
- Stateless backend design; all state persisted in database  
- Unit tests for all MCP tools  

**Deliverables:**
- MCP server fully functional  
- CRUD operations tested via FastAPI  
- Stateless request cycle verified  

---

### Spec 2: AI Agent Logic
**Objective:** Implement conversational AI agent using OpenAI Agents SDK to interact with MCP tools.  

**Components & Tasks:**
- Parse natural language user messages  
- Map user intents to MCP tools (add/list/complete/delete/update)  
- Handle multi-step tasks and tool chaining  
- Confirmation messages for all actions  
- Error handling for invalid or missing tasks  
- Persist conversation messages in database  

**Deliverables:**
- Working AI agent interpreting NL commands  
- Demonstration of all task operations via chat  
- Stateless request cycle maintained  

---

### Spec 3: Frontend & ChatKit Integration
**Objective:** Build a user-friendly web interface for AI chatbot using ChatKit.  

**Components & Tasks:**
- Integrate ChatKit UI with FastAPI backend  
- Display conversation history, task confirmations, and errors  
- Session handling for new/existing conversations  
- Domain allowlist configuration for ChatKit deployment  
- Pass environment variables (`NEXT_PUBLIC_OPENAI_DOMAIN_KEY`)  

**Deliverables:**
- Functional web frontend connected to backend  
- Messages and tasks displayed dynamically  
- Domain security & deployment ready  

---

### Spec 4: Database & Deployment
**Objective:** Implement database persistence, authentication, and deploy full stack.  

**Components & Tasks:**
- SQLModel database models: Task, Conversation, Message  
- Migration scripts for Neon Serverless PostgreSQL  
- Better Auth integration for user sessions  
- Full stack deployment configuration (frontend + backend)  
- Testing and validation of end-to-end functionality  

**Deliverables:**
- Database ready with migrations  
- Authentication functional  
- Production-ready deployment  
- README with setup and usage instructions  

---

## 4. Conversation & Tool Behavior

| User Intent                | MCP Tool         | Notes                                       |
|-----------------------------|----------------|--------------------------------------------|
| Add a task                  | add_task        | Parse title & optional description         |
| List tasks                  | list_tasks      | Support `all`, `pending`, `completed`     |
| Complete a task             | complete_task   | Requires task_id                            |
| Delete a task               | delete_task     | Fetch task first if ambiguous              |
| Update task title/desc      | update_task     | Update optional fields                     |
| Confirmation                | N/A             | Always provide friendly confirmation       |
| Error handling              | N/A             | Gracefully handle missing tasks/errors    |

---

## 5. Stateless Architecture Benefits
- Any server instance can process requests independently  
- Conversation and task state stored in DB for resilience  
- Horizontal scaling possible  
- Tool chaining supported via AI agent  

---

## 6. Deliverables Summary
- `/frontend` → ChatKit-based UI  
- `/backend` → FastAPI + OpenAI Agents SDK + MCP  
- `/specs` → Specification files for agent and MCP tools  
- Database migration scripts  
- Fully working chatbot managing tasks via natural language  
- Deployed frontend with allowlisted domain  
- Documentation and setup instructions
```

## Response snapshot

I have successfully updated the project constitution for the Todo AI Chatbot project. Here's the summary:

**New Version**: 3.0.0 (incremented from 2.1.0)
**Bump Rationale**: Major update to reflect Phase III requirements with new AI chatbot functionality, MCP tools integration, and stateless architecture requirements.

**Key Changes Made**:
1. Updated the project purpose to reflect the AI-powered conversational interface
2. Modified existing principles (I-IX) to align with Phase III requirements
3. Added three new principles:
   - X. MCP-First Architecture: All operations must be exposed as MCP tools
   - XI. AI-Driven Interactions: Using OpenAI Agents SDK for natural language processing
   - XII. Statelessness Requirement: Maintaining stateless backend design
4. Updated the tech stack to include OpenAI ChatKit, OpenAI Agents SDK, and MCP SDK
5. Revised non-negotiables to include MCP tool integration and AI agent requirements

**Files Flagged for Manual Follow-up**:
- README.md: Needs to be updated to reflect the new Phase III features and architecture

**Suggested Commit Message**: 
`docs: amend constitution to v3.0.0 (Phase III AI Chatbot requirements + MCP integration)`

The updated constitution now properly reflects the requirements for the Todo AI Chatbot project, emphasizing the conversational interface, MCP-first architecture, AI-driven interactions, and stateless design principles.

## Outcome

- ✅ Impact: Updated constitution to reflect Phase III requirements for Todo AI Chatbot
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: /sp.specify to implement feature specification based on updated constitution
- 🧠 Reflection: Successfully transformed the constitution from Phase II web app to Phase III AI chatbot with MCP integration

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin implementing feature specifications based on the updated constitution