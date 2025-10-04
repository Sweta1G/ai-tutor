"""
Parameter extraction service using LangChain for intelligent conversation analysis.
"""

import logging
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from ..models.schemas import ConversationContext, UserInfo, ChatMessage
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class ExtractedParameters(BaseModel):
    """Structured parameters extracted from conversation."""
    tool_type: str = Field(description="Type of educational tool needed")
    topic: Optional[str] = Field(description="Main topic or subject")
    subject: Optional[str] = Field(description="Academic subject area")
    difficulty: Optional[str] = Field(description="Inferred difficulty level")
    count: Optional[int] = Field(description="Number of items to generate")
    note_taking_style: Optional[str] = Field(description="Preferred note format")
    desired_depth: Optional[str] = Field(description="Level of explanation detail")
    concept_to_explain: Optional[str] = Field(description="Specific concept needing explanation")
    include_examples: Optional[bool] = Field(description="Whether to include examples")
    include_analogies: Optional[bool] = Field(description="Whether to include analogies")
    confidence_score: float = Field(description="Confidence in parameter extraction (0-1)")
    reasoning: str = Field(description="Explanation of parameter extraction logic")

class ParameterExtractor:
    """Intelligent parameter extraction from conversational context."""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = None
        self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the language model."""
        try:
            if self.settings.openai_api_key:
                self.llm = ChatOpenAI(
                    openai_api_key=self.settings.openai_api_key,
                    model="gpt-3.5-turbo",
                    temperature=0.1
                )
                logger.info("Initialized OpenAI language model")
            else:
                logger.warning("No OpenAI API key provided, using rule-based extraction only")
        except Exception as e:
            logger.error(f"Failed to initialize language model: {e}")
            
    async def extract_parameters(self, context: ConversationContext) -> Dict[str, Any]:
        """
        Extract parameters from conversational context using hybrid approach.
        
        Args:
            context: The conversation context containing student message and history
            
        Returns:
            Dictionary of extracted parameters
        """
        try:
            # Use LLM-based extraction if available, otherwise fall back to rule-based
            if self.llm:
                return await self._extract_with_llm(context)
            else:
                return await self._extract_with_rules(context)
                
        except Exception as e:
            logger.error(f"Error in parameter extraction: {e}")
            # Fallback to rule-based extraction
            return await self._extract_with_rules(context)
    
    async def _extract_with_llm(self, context: ConversationContext) -> Dict[str, Any]:
        """Extract parameters using language model."""
        
        # Create parser for structured output
        parser = PydanticOutputParser(pydantic_object=ExtractedParameters)
        
        # Build the prompt template
        template = """
        You are an intelligent parameter extraction system for an AI tutoring platform.
        Your job is to analyze student conversations and extract the parameters needed to call educational tools.
        
        Available tools:
        1. Note Maker - Creates structured notes (needs: topic, subject, note_taking_style)
        2. Flashcard Generator - Creates practice flashcards (needs: topic, subject, difficulty, count)
        3. Concept Explainer - Explains concepts in detail (needs: concept_to_explain, current_topic, desired_depth)
        
        Student Profile:
        - Name: {student_name}
        - Grade Level: {grade_level}
        - Learning Style: {learning_style}
        - Emotional State: {emotional_state}
        - Mastery Level: {mastery_level}
        
        Conversation History:
        {chat_history}
        
        Current Student Message: "{student_message}"
        
        Based on the conversation, extract parameters for the most appropriate educational tool.
        Consider the student's emotional state and mastery level when inferring difficulty and depth.
        
        {format_instructions}
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Format chat history
        history_text = "\n".join([
            f"{msg.role}: {msg.content}" 
            for msg in context.chat_history[-5:]  # Last 5 messages for context
        ])
        
        # Create the formatted prompt
        formatted_prompt = prompt.format(
            student_name=context.user_info.name,
            grade_level=context.user_info.grade_level,
            learning_style=context.user_info.learning_style_summary,
            emotional_state=context.user_info.emotional_state_summary,
            mastery_level=context.user_info.mastery_level_summary,
            chat_history=history_text,
            student_message=context.student_message,
            format_instructions=parser.get_format_instructions()
        )
        
        # Get LLM response
        messages = [
            SystemMessage(content="You are an expert educational parameter extractor."),
            HumanMessage(content=formatted_prompt)
        ]
        
        response = await self.llm.agenerate([messages])
        content = response.generations[0][0].text
        
        # Parse the response
        try:
            extracted = parser.parse(content)
            return self._convert_to_dict(extracted, context)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # Fallback to rule-based extraction
            return await self._extract_with_rules(context)
    
    async def _extract_with_rules(self, context: ConversationContext) -> Dict[str, Any]:
        """Extract parameters using rule-based approach."""
        
        message = context.student_message.lower()
        parameters = {
            "extraction_method": "rule_based",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Determine tool type based on keywords
        tool_type = self._determine_tool_type(message)
        parameters["tool_type"] = tool_type
        
        # Extract common parameters
        parameters["topic"] = self._extract_topic(message)
        parameters["subject"] = self._extract_subject(message, context)
        
        # Tool-specific parameter extraction
        if tool_type == "note_maker":
            parameters.update(self._extract_note_maker_params(message, context))
        elif tool_type == "flashcard_generator":
            parameters.update(self._extract_flashcard_params(message, context))
        elif tool_type == "concept_explainer":
            parameters.update(self._extract_explainer_params(message, context))
        
        # Adapt based on student profile
        parameters = self._adapt_for_student_profile(parameters, context.user_info)
        
        parameters["confidence_score"] = self._calculate_confidence(parameters)
        parameters["reasoning"] = self._generate_reasoning(parameters, message)
        
        return parameters
    
    def _determine_tool_type(self, message: str) -> str:
        """Determine which tool is needed based on message content."""
        
        note_keywords = ["notes", "note", "summary", "outline", "organize", "structured"]
        flashcard_keywords = ["flashcard", "quiz", "practice", "test", "review", "memorize"]
        explainer_keywords = ["explain", "understand", "confused", "what is", "how does", "concept"]
        
        note_score = sum(1 for keyword in note_keywords if keyword in message)
        flashcard_score = sum(1 for keyword in flashcard_keywords if keyword in message)
        explainer_score = sum(1 for keyword in explainer_keywords if keyword in message)
        
        if note_score >= flashcard_score and note_score >= explainer_score:
            return "note_maker"
        elif flashcard_score >= explainer_score:
            return "flashcard_generator"
        else:
            return "concept_explainer"
    
    def _extract_topic(self, message: str) -> Optional[str]:
        """Extract the main topic from the message."""
        
        # Common academic topics
        topics = [
            "calculus", "algebra", "geometry", "trigonometry", "statistics",
            "physics", "chemistry", "biology", "anatomy", "genetics",
            "history", "literature", "writing", "grammar", "vocabulary",
            "programming", "computer science", "algorithms", "data structures",
            "economics", "psychology", "sociology", "philosophy"
        ]
        
        for topic in topics:
            if topic in message:
                return topic
        
        # Try to extract topic after "about", "on", "with"
        patterns = [
            r"about\s+([a-zA-Z\s]+)",
            r"on\s+([a-zA-Z\s]+)",
            r"with\s+([a-zA-Z\s]+)",
            r"studying\s+([a-zA-Z\s]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                topic = match.group(1).strip()
                if len(topic.split()) <= 3:  # Reasonable topic length
                    return topic
        
        return None
    
    def _extract_subject(self, message: str, context: ConversationContext) -> Optional[str]:
        """Extract the academic subject."""
        
        subjects = {
            "math": ["math", "calculus", "algebra", "geometry", "trigonometry", "statistics"],
            "science": ["physics", "chemistry", "biology", "science"],
            "english": ["english", "literature", "writing", "grammar"],
            "history": ["history", "social studies"],
            "computer science": ["programming", "computer", "coding", "algorithms"]
        }
        
        for subject, keywords in subjects.items():
            if any(keyword in message for keyword in keywords):
                return subject
        
        return None
    
    def _extract_note_maker_params(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Extract parameters specific to note maker."""
        
        params = {}
        
        # Note taking style
        if any(word in message for word in ["outline", "bullet", "points"]):
            params["note_taking_style"] = "outline"
        elif "narrative" in message:
            params["note_taking_style"] = "narrative"
        else:
            params["note_taking_style"] = "structured"  # Default
        
        # Examples and analogies
        params["include_examples"] = "example" in message or "examples" in message
        params["include_analogies"] = "analogy" in message or "analogies" in message
        
        return params
    
    def _extract_flashcard_params(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Extract parameters specific to flashcard generator."""
        
        params = {}
        
        # Extract count
        count_match = re.search(r'(\d+)', message)
        if count_match:
            count = int(count_match.group(1))
            params["count"] = min(max(count, 1), 20)  # Clamp between 1-20
        else:
            params["count"] = 10  # Default
        
        # Determine difficulty
        if any(word in message for word in ["easy", "basic", "simple"]):
            params["difficulty"] = "easy"
        elif any(word in message for word in ["hard", "difficult", "advanced", "challenging"]):
            params["difficulty"] = "hard"
        else:
            params["difficulty"] = "medium"  # Default
        
        params["include_examples"] = True  # Default for flashcards
        
        return params
    
    def _extract_explainer_params(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Extract parameters specific to concept explainer."""
        
        params = {}
        
        # Extract concept to explain
        concept_patterns = [
            r"explain\s+([a-zA-Z\s]+)",
            r"what is\s+([a-zA-Z\s]+)",
            r"understand\s+([a-zA-Z\s]+)",
            r"confused about\s+([a-zA-Z\s]+)"
        ]
        
        for pattern in concept_patterns:
            match = re.search(pattern, message)
            if match:
                concept = match.group(1).strip()
                if len(concept.split()) <= 4:  # Reasonable concept length
                    params["concept_to_explain"] = concept
                    break
        
        # Determine desired depth
        if any(word in message for word in ["basic", "simple", "overview"]):
            params["desired_depth"] = "basic"
        elif any(word in message for word in ["detailed", "comprehensive", "thorough"]):
            params["desired_depth"] = "comprehensive"
        elif any(word in message for word in ["advanced", "deep"]):
            params["desired_depth"] = "advanced"
        else:
            params["desired_depth"] = "intermediate"  # Default
        
        # Set current topic same as concept if not extracted separately
        if not params.get("current_topic") and params.get("concept_to_explain"):
            params["current_topic"] = params["concept_to_explain"]
        
        return params
    
    def _adapt_for_student_profile(self, parameters: Dict[str, Any], user_info: UserInfo) -> Dict[str, Any]:
        """Adapt parameters based on student profile."""
        
        # Adjust difficulty based on emotional state
        emotional_state = user_info.emotional_state_summary.lower()
        
        if "anxious" in emotional_state or "confused" in emotional_state:
            if parameters.get("difficulty") == "hard":
                parameters["difficulty"] = "medium"
            elif parameters.get("difficulty") == "medium":
                parameters["difficulty"] = "easy"
            
            if parameters.get("desired_depth") == "comprehensive":
                parameters["desired_depth"] = "intermediate"
            elif parameters.get("desired_depth") == "advanced":
                parameters["desired_depth"] = "basic"
        
        # Adjust based on mastery level
        mastery = user_info.mastery_level_summary.lower()
        if "level 1" in mastery or "level 2" in mastery or "level 3" in mastery:
            parameters["difficulty"] = "easy"
            parameters["desired_depth"] = "basic"
        elif "level 8" in mastery or "level 9" in mastery or "level 10" in mastery:
            if parameters.get("difficulty") == "easy":
                parameters["difficulty"] = "medium"
            parameters["desired_depth"] = "advanced"
        
        return parameters
    
    def _calculate_confidence(self, parameters: Dict[str, Any]) -> float:
        """Calculate confidence score for parameter extraction."""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on extracted parameters
        if parameters.get("topic"):
            confidence += 0.2
        if parameters.get("tool_type"):
            confidence += 0.2
        if parameters.get("subject"):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_reasoning(self, parameters: Dict[str, Any], message: str) -> str:
        """Generate explanation of parameter extraction reasoning."""
        
        reasoning_parts = []
        
        tool_type = parameters.get("tool_type", "unknown")
        reasoning_parts.append(f"Identified '{tool_type}' as the most appropriate tool")
        
        if parameters.get("topic"):
            reasoning_parts.append(f"Extracted topic: '{parameters['topic']}'")
        
        if parameters.get("difficulty"):
            reasoning_parts.append(f"Inferred difficulty level: '{parameters['difficulty']}'")
        
        if parameters.get("emotional_state_adaptation"):
            reasoning_parts.append("Adapted parameters based on student's emotional state")
        
        return ". ".join(reasoning_parts) + "."
    
    def _convert_to_dict(self, extracted: ExtractedParameters, context: ConversationContext) -> Dict[str, Any]:
        """Convert structured extraction to dictionary format."""
        
        result = extracted.dict()
        result["extraction_method"] = "llm_based"
        result["timestamp"] = datetime.utcnow().isoformat()
        result["user_id"] = context.user_info.user_id
        
        return result