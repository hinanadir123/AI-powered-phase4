# Phase 3: Todo AI Chatbot

## Objective

The goal of Phase 3 is to add an AI-powered chatbot to the existing Todo application.
Users will manage their tasks using natural language instead of buttons.
The chatbot will be able to create, list, update, complete, and delete tasks.
The system will use a stateless chat API backed by a database for conversation history.
AI decision-making will be handled using the OpenAI Agents SDK.
All task operations will be executed through MCP tools.

## Architecture Overview

The system will use a single stateless chat API endpoint.
Each chat request will load conversation history from the database.
The AI agent will analyze the user message and decide which action to take.
Task-related actions will be executed through MCP tools.
All application state will be stored in the database, not in server memory.
The frontend will communicate only with the chat API.

## Agent Responsibilities
The AI agent will interpret the user's natural language messages.
It will identify the user's intent such as creating, listing, updating, completing, or deleting tasks.
The agent will select the appropriate MCP tool based on the intent.
It will never directly access the database.
The agent will confirm actions with clear and friendly responses.
The agent will handle errors gracefully when tasks are not found or inputs are unclear.

## MCP Tools
- add_task
- list_tasks
- update_task
- complete_task
- delete_task
