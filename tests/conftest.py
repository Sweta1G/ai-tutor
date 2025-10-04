"""
Test configuration and fixtures.
"""

import pytest
import asyncio
from typing import Generator
from unittest.mock import Mock

from app.models.schemas import UserInfo, ConversationContext, ChatMessage, OrchestrationRequest
from app.services.parameter_extractor import ParameterExtractor
from app.services.tool_manager import ToolManager
from app.services.orchestrator_service import OrchestratorService

@pytest.fixture
def sample_user_info() -> UserInfo:
    """Sample user info for testing."""
    return UserInfo(
        user_id="test_user_123",
        name="Test Student",
        grade_level="10",
        learning_style_summary="Visual learner, prefers diagrams and examples",
        emotional_state_summary="Focused and motivated",
        mastery_level_summary="Level 6: Good understanding, ready for application"
    )

@pytest.fixture
def sample_chat_history() -> list:
    """Sample chat history for testing."""
    return [
        ChatMessage(role="user", content="I need help with math"),
        ChatMessage(role="assistant", content="I'd be happy to help with math. What specific topic?"),
        ChatMessage(role="user", content="Derivatives in calculus")
    ]

@pytest.fixture
def sample_conversation_context(sample_user_info, sample_chat_history) -> ConversationContext:
    """Sample conversation context for testing."""
    return ConversationContext(
        student_message="I'm struggling with calculus derivatives and need some practice problems",
        chat_history=sample_chat_history,
        user_info=sample_user_info,
        inferred_intent="practice_request",
        extracted_entities={"topic": "derivatives", "subject": "calculus"}
    )

@pytest.fixture
def sample_orchestration_request(sample_conversation_context) -> OrchestrationRequest:
    """Sample orchestration request for testing."""
    return OrchestrationRequest(
        conversation_context=sample_conversation_context,
        session_id="test_session_123"
    )

@pytest.fixture
def parameter_extractor() -> ParameterExtractor:
    """Parameter extractor instance for testing."""
    return ParameterExtractor()

@pytest.fixture
def tool_manager() -> ToolManager:
    """Tool manager instance for testing."""
    return ToolManager()

@pytest.fixture
def orchestrator_service() -> OrchestratorService:
    """Orchestrator service instance for testing."""
    return OrchestratorService()

@pytest.fixture
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()