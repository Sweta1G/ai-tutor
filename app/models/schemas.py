"""
Educational tool schemas and data models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum

# Enums for validation
class TeachingStyle(str, Enum):
    DIRECT = "direct"
    SOCRATIC = "socratic"
    VISUAL = "visual"
    FLIPPED_CLASSROOM = "flipped_classroom"

class EmotionalState(str, Enum):
    FOCUSED = "focused"
    ANXIOUS = "anxious"
    CONFUSED = "confused"
    TIRED = "tired"

class NoteTakingStyle(str, Enum):
    OUTLINE = "outline"
    BULLET_POINTS = "bullet_points"
    NARRATIVE = "narrative"
    STRUCTURED = "structured"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class DesiredDepth(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    COMPREHENSIVE = "comprehensive"

# Base models
class UserInfo(BaseModel):
    """Student profile information."""
    user_id: str = Field(..., description="Unique identifier for the student")
    name: str = Field(..., description="Student's full name")
    grade_level: str = Field(..., description="Student's current grade level")
    learning_style_summary: str = Field(..., description="Summary of student's preferred learning style")
    emotional_state_summary: str = Field(..., description="Current emotional state of the student")
    mastery_level_summary: str = Field(..., description="Current mastery level description")

class ChatMessage(BaseModel):
    """Chat message structure."""
    role: Literal["user", "assistant"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")

# Tool input schemas
class NoteMakerInput(BaseModel):
    """Input schema for Note Maker tool."""
    user_info: UserInfo
    chat_history: List[ChatMessage] = Field(..., description="Recent conversation history to provide context")
    topic: str = Field(..., description="The main topic for note generation")
    subject: str = Field(..., description="Academic subject area")
    note_taking_style: NoteTakingStyle = Field(..., description="Preferred format for the notes")
    include_examples: bool = Field(True, description="Whether to include examples in the notes")
    include_analogies: bool = Field(False, description="Whether to include analogies in the notes")

class FlashcardGeneratorInput(BaseModel):
    """Input schema for Flashcard Generator tool."""
    user_info: UserInfo
    topic: str = Field(..., description="The topic for flashcard generation")
    count: int = Field(..., ge=1, le=20, description="Number of flashcards to generate")
    difficulty: Difficulty = Field(..., description="Difficulty level of the flashcards")
    include_examples: bool = Field(True, description="Whether to include examples in flashcards")
    subject: str = Field(..., description="Academic subject area")

class ConceptExplainerInput(BaseModel):
    """Input schema for Concept Explainer tool."""
    user_info: UserInfo
    chat_history: List[ChatMessage] = Field(..., description="Recent conversation history for context")
    concept_to_explain: str = Field(..., description="The specific concept to explain")
    current_topic: str = Field(..., description="Broader topic context")
    desired_depth: DesiredDepth = Field(..., description="Level of detail for the explanation")

# Tool output schemas
class NoteSection(BaseModel):
    """Note section structure."""
    title: str
    content: str
    key_points: List[str]
    examples: List[str]
    analogies: List[str]

class NoteMakerOutput(BaseModel):
    """Output schema for Note Maker tool."""
    topic: str
    title: str
    summary: str
    note_sections: List[NoteSection]
    key_concepts: List[str]
    connections_to_prior_learning: List[str]
    visual_elements: List[Dict[str, Any]]
    practice_suggestions: List[str]
    source_references: List[str]
    note_taking_style: str

class Flashcard(BaseModel):
    """Individual flashcard structure."""
    title: str
    question: str
    answer: str
    example: Optional[str] = None

class FlashcardGeneratorOutput(BaseModel):
    """Output schema for Flashcard Generator tool."""
    flashcards: List[Flashcard]
    topic: str
    adaptation_details: str
    difficulty: str

class ConceptExplainerOutput(BaseModel):
    """Output schema for Concept Explainer tool."""
    explanation: str
    examples: List[str]
    related_concepts: List[str]
    visual_aids: List[str]
    practice_questions: List[str]
    source_references: List[str]

# Orchestrator schemas
class ConversationContext(BaseModel):
    """Context extracted from conversation."""
    student_message: str = Field(..., description="The student's current message")
    chat_history: List[ChatMessage] = Field(default=[], description="Previous conversation messages")
    user_info: UserInfo = Field(..., description="Student profile information")
    inferred_intent: Optional[str] = Field(None, description="Inferred educational intent")
    extracted_entities: Dict[str, Any] = Field(default={}, description="Extracted entities from conversation")

class OrchestrationRequest(BaseModel):
    """Request for tool orchestration."""
    conversation_context: ConversationContext
    preferred_teaching_style: Optional[TeachingStyle] = Field(None, description="Preferred teaching approach")
    session_id: Optional[str] = Field(None, description="Session identifier for state management")

class ToolExecutionResult(BaseModel):
    """Result of tool execution."""
    tool_name: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float

class OrchestrationResponse(BaseModel):
    """Response from orchestration system."""
    session_id: str
    executed_tools: List[ToolExecutionResult]
    extracted_parameters: Dict[str, Any]
    reasoning: str = Field(..., description="Explanation of tool selection and parameter extraction")
    conversation_state: Dict[str, Any] = Field(default={}, description="Updated conversation state")