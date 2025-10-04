# Autonomous AI Tutor Orchestrator

## Project Overview
This project implements an intelligent middleware orchestrator that autonomously connects a conversational AI tutor to multiple educational tools by extracting required parameters from chat context and managing complex tool interactions.

## Technology Stack
- Backend: Python with FastAPI
- Agent Framework: LangGraph and LangChain
- Database: PostgreSQL (optional for persistent storage)
- Additional: Pydantic for data validation

## Core Components
1. Context Analysis Engine - Parse conversation and identify educational intent
2. Parameter Extraction System - Map conversational elements to tool parameters
3. Tool Orchestration Layer - Manage API calls to educational tools
4. State Management - Maintain conversation context and student state
5. Schema Validation - Ensure API requests meet tool specifications

## Progress Tracking
- [x] Project structure created
- [x] Core dependencies defined
- [x] FastAPI application setup
- [x] LangGraph workflow implementation
- [x] Educational tool integrations
- [x] Parameter extraction system
- [x] State management
- [x] Testing and validation
- [x] **FULLY IMPLEMENTED AND WORKING**

## Demo Instructions
- Run `python simple_demo.py` for core functionality demonstration
- Run `python -m uvicorn app.main:app --reload` for REST API server
- Access API documentation at http://localhost:8000/docs when server is running