"""
Tests for parameter extraction functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from app.services.parameter_extractor import ParameterExtractor
from app.models.schemas import ConversationContext, UserInfo, ChatMessage

class TestParameterExtractor:
    """Test cases for parameter extraction."""
    
    @pytest.mark.asyncio
    async def test_extract_note_maker_parameters(self, sample_conversation_context):
        """Test extraction of note maker parameters."""
        
        # Modify context for note maker scenario
        sample_conversation_context.student_message = "I need organized notes on photosynthesis for my biology class"
        
        extractor = ParameterExtractor()
        
        # Test with rule-based extraction (no LLM)
        parameters = await extractor.extract_parameters(sample_conversation_context)
        
        assert parameters["tool_type"] == "note_maker"
        assert "photosynthesis" in parameters.get("topic", "").lower()
        assert parameters.get("subject") in ["science", "biology", None]
        assert parameters["confidence_score"] > 0.5
        assert "reasoning" in parameters
    
    @pytest.mark.asyncio
    async def test_extract_flashcard_parameters(self, sample_conversation_context):
        """Test extraction of flashcard generator parameters."""
        
        # Modify context for flashcard scenario
        sample_conversation_context.student_message = "Can you make 5 flashcards for calculus derivatives practice?"
        
        extractor = ParameterExtractor()
        parameters = await extractor.extract_parameters(sample_conversation_context)
        
        assert parameters["tool_type"] == "flashcard_generator"
        assert parameters.get("count") == 5
        assert "derivatives" in parameters.get("topic", "").lower()
        assert parameters.get("difficulty") in ["easy", "medium", "hard"]
    
    @pytest.mark.asyncio
    async def test_extract_concept_explainer_parameters(self, sample_conversation_context):
        """Test extraction of concept explainer parameters."""
        
        # Modify context for explanation scenario
        sample_conversation_context.student_message = "I'm confused about quantum mechanics. Can you explain it?"
        
        extractor = ParameterExtractor()
        parameters = await extractor.extract_parameters(sample_conversation_context)
        
        assert parameters["tool_type"] == "concept_explainer"
        assert "quantum mechanics" in parameters.get("concept_to_explain", "").lower()
        assert parameters.get("desired_depth") in ["basic", "intermediate", "advanced", "comprehensive"]
    
    @pytest.mark.asyncio
    async def test_student_profile_adaptation(self, sample_conversation_context):
        """Test that parameters are adapted based on student profile."""
        
        # Create anxious student profile
        anxious_user = UserInfo(
            user_id="anxious_student",
            name="Anxious Student",
            grade_level="9",
            learning_style_summary="Needs encouragement and simple explanations",
            emotional_state_summary="Anxious and overwhelmed",
            mastery_level_summary="Level 2: Building foundation"
        )
        
        sample_conversation_context.user_info = anxious_user
        sample_conversation_context.student_message = "I need flashcards for advanced calculus"
        
        extractor = ParameterExtractor()
        parameters = await extractor.extract_parameters(sample_conversation_context)
        
        # Should adapt difficulty for anxious student
        assert parameters.get("difficulty") in ["easy", "medium"]  # Not hard
    
    def test_determine_tool_type(self):
        """Test tool type determination logic."""
        
        extractor = ParameterExtractor()
        
        # Test note maker keywords
        assert extractor._determine_tool_type("I need notes on biology") == "note_maker"
        assert extractor._determine_tool_type("Create an outline for chemistry") == "note_maker"
        
        # Test flashcard keywords
        assert extractor._determine_tool_type("Make flashcards for vocabulary") == "flashcard_generator"
        assert extractor._determine_tool_type("I need practice questions") == "flashcard_generator"
        
        # Test explainer keywords
        assert extractor._determine_tool_type("Explain quantum physics to me") == "concept_explainer"
        assert extractor._determine_tool_type("I'm confused about derivatives") == "concept_explainer"
    
    def test_extract_topic(self):
        """Test topic extraction logic."""
        
        extractor = ParameterExtractor()
        
        # Test direct topic mentions
        assert extractor._extract_topic("studying calculus today") == "calculus"
        assert extractor._extract_topic("help with biology homework") == "biology"
        
        # Test topic extraction patterns
        topic = extractor._extract_topic("I need help with photosynthesis")
        assert topic is not None
        
        topic = extractor._extract_topic("studying about world war 2")
        assert topic is not None