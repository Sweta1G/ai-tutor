"""
Simplified demo script that showcases core functionality without complex state management.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

from app.models.schemas import (
    UserInfo, 
    ChatMessage, 
    ConversationContext
)
from app.services.parameter_extractor import ParameterExtractor
from app.services.tool_manager import ToolManager

async def demonstrate_parameter_extraction():
    """Demonstrate intelligent parameter extraction."""
    
    print("🧠 PARAMETER EXTRACTION DEMONSTRATION")
    print("="*60)
    
    # Initialize parameter extractor
    extractor = ParameterExtractor()
    
    # Create test scenarios
    scenarios = [
        {
            "name": "Note Making Request",
            "student": UserInfo(
                user_id="alice_123",
                name="Alice Johnson",
                grade_level="10",
                learning_style_summary="Visual learner, prefers structured notes",
                emotional_state_summary="Focused and motivated",
                mastery_level_summary="Level 6: Good understanding"
            ),
            "message": "I'm studying photosynthesis in biology and need organized notes for my exam",
            "chat_history": []
        },
        {
            "name": "Flashcard Generation Request",
            "student": UserInfo(
                user_id="bob_456",
                name="Bob Smith",
                grade_level="9",
                learning_style_summary="Kinesthetic learner, learns through practice",
                emotional_state_summary="Anxious about upcoming test",
                mastery_level_summary="Level 3: Building foundational knowledge"
            ),
            "message": "Can you make 10 flashcards for calculus derivatives? I need practice problems",
            "chat_history": [
                ChatMessage(role="user", content="I'm struggling with calculus"),
                ChatMessage(role="assistant", content="What specific area would you like to focus on?")
            ]
        },
        {
            "name": "Concept Explanation Request",
            "student": UserInfo(
                user_id="charlie_789",
                name="Charlie Wilson",
                grade_level="11",
                learning_style_summary="Analytical learner, enjoys detailed explanations",
                emotional_state_summary="Curious and engaged",
                mastery_level_summary="Level 8: Advanced understanding"
            ),
            "message": "I'm confused about quantum mechanics. Can you explain wave-particle duality?",
            "chat_history": []
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- SCENARIO {i}: {scenario['name']} ---")
        print(f"Student: {scenario['student'].name}")
        print(f"Message: '{scenario['message']}'")
        
        # Create conversation context
        context = ConversationContext(
            student_message=scenario["message"],
            chat_history=scenario["chat_history"],
            user_info=scenario["student"]
        )
        
        # Extract parameters
        start_time = datetime.now()
        parameters = await extractor.extract_parameters(context)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"\n⏱️  Processing time: {processing_time:.3f} seconds")
        print(f"🎯 Identified tool: {parameters.get('tool_type', 'N/A')}")
        print(f"📚 Topic: {parameters.get('topic', 'N/A')}")
        print(f"🎓 Subject: {parameters.get('subject', 'N/A')}")
        
        if parameters.get('difficulty'):
            print(f"📊 Difficulty: {parameters['difficulty']}")
        if parameters.get('count'):
            print(f"🔢 Count: {parameters['count']}")
        if parameters.get('note_taking_style'):
            print(f"📝 Note style: {parameters['note_taking_style']}")
        if parameters.get('desired_depth'):
            print(f"🔍 Depth: {parameters['desired_depth']}")
        
        print(f"🎯 Confidence: {parameters.get('confidence_score', 0):.2f}")
        print(f"💭 Reasoning: {parameters.get('reasoning', 'N/A')}")

async def demonstrate_tool_execution():
    """Demonstrate tool execution with extracted parameters."""
    
    print(f"\n\n🛠️ TOOL EXECUTION DEMONSTRATION")
    print("="*60)
    
    # Initialize tool manager
    tool_manager = ToolManager()
    
    # Test scenarios with pre-extracted parameters
    test_cases = [
        {
            "tool_name": "note_maker",
            "input_data": {
                "user_info": {
                    "user_id": "test_user",
                    "name": "Test Student",
                    "grade_level": "10",
                    "learning_style_summary": "Visual learner",
                    "emotional_state_summary": "Focused",
                    "mastery_level_summary": "Level 6"
                },
                "chat_history": [],
                "topic": "photosynthesis",
                "subject": "biology",
                "note_taking_style": "structured",
                "include_examples": True,
                "include_analogies": False
            }
        },
        {
            "tool_name": "flashcard_generator",
            "input_data": {
                "user_info": {
                    "user_id": "test_user",
                    "name": "Test Student",
                    "grade_level": "9",
                    "learning_style_summary": "Kinesthetic learner",
                    "emotional_state_summary": "Anxious",
                    "mastery_level_summary": "Level 3"
                },
                "topic": "derivatives",
                "count": 8,  # Reduced from 10 due to anxiety adaptation
                "difficulty": "easy",  # Reduced due to anxiety and low mastery
                "include_examples": True,
                "subject": "calculus"
            }
        },
        {
            "tool_name": "concept_explainer",
            "input_data": {
                "user_info": {
                    "user_id": "test_user",
                    "name": "Test Student",
                    "grade_level": "11",
                    "learning_style_summary": "Analytical learner",
                    "emotional_state_summary": "Curious",
                    "mastery_level_summary": "Level 8"
                },
                "chat_history": [],
                "concept_to_explain": "wave-particle duality",
                "current_topic": "quantum mechanics",
                "desired_depth": "advanced"  # High mastery level allows advanced depth
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        tool_name = test_case["tool_name"]
        input_data = test_case["input_data"]
        
        print(f"\n--- TEST CASE {i}: {tool_name.replace('_', ' ').title()} ---")
        
        try:
            # Validate input first
            is_valid, errors = await tool_manager.validate_tool_input(tool_name, input_data)
            print(f"✅ Input validation: {'PASSED' if is_valid else 'FAILED'}")
            
            if not is_valid:
                print(f"❌ Validation errors: {errors}")
                continue
            
            # Execute tool
            start_time = datetime.now()
            result = await tool_manager.execute_tool(tool_name, input_data)
            end_time = datetime.now()
            
            execution_time = (end_time - start_time).total_seconds()
            
            print(f"⏱️  Execution time: {execution_time:.3f} seconds")
            print(f"✅ Tool executed successfully")
            
            # Display key results
            if tool_name == "note_maker":
                print(f"📄 Generated: '{result.get('title', 'N/A')}'")
                print(f"📚 Sections: {len(result.get('note_sections', []))}")
                print(f"🔑 Key concepts: {len(result.get('key_concepts', []))}")
                
            elif tool_name == "flashcard_generator":
                flashcards = result.get('flashcards', [])
                print(f"🃏 Generated: {len(flashcards)} flashcards")
                print(f"📊 Difficulty: {result.get('difficulty', 'N/A')}")
                if flashcards:
                    print(f"📝 Sample question: '{flashcards[0].get('question', 'N/A')}'")
                    
            elif tool_name == "concept_explainer":
                print(f"📖 Explanation provided for concept")
                print(f"💡 Examples: {len(result.get('examples', []))}")
                print(f"🔗 Related concepts: {len(result.get('related_concepts', []))}")
                print(f"❓ Practice questions: {len(result.get('practice_questions', []))}")
            
        except Exception as e:
            print(f"❌ Tool execution failed: {str(e)}")

async def demonstrate_student_adaptation():
    """Demonstrate how the system adapts to different student profiles."""
    
    print(f"\n\n🎭 STUDENT ADAPTATION DEMONSTRATION")
    print("="*60)
    
    extractor = ParameterExtractor()
    
    # Same request from different student profiles
    base_message = "I need flashcards for advanced calculus"
    
    student_profiles = [
        {
            "name": "Confident Advanced Student",
            "profile": UserInfo(
                user_id="advanced_student",
                name="Advanced Student",
                grade_level="12",
                learning_style_summary="Self-directed learner",
                emotional_state_summary="Confident and eager to learn",
                mastery_level_summary="Level 9: Advanced understanding"
            ),
            "expected_adaptations": ["Higher difficulty", "More complex content"]
        },
        {
            "name": "Anxious Beginner Student",
            "profile": UserInfo(
                user_id="anxious_student",
                name="Anxious Student",
                grade_level="9",
                learning_style_summary="Needs encouragement and support",
                emotional_state_summary="Anxious and overwhelmed by math",
                mastery_level_summary="Level 2: Building foundation"
            ),
            "expected_adaptations": ["Lower difficulty", "More scaffolding", "Fewer items"]
        },
        {
            "name": "Confused Mid-Level Student",
            "profile": UserInfo(
                user_id="confused_student",
                name="Confused Student",
                grade_level="10",
                learning_style_summary="Visual learner",
                emotional_state_summary="Confused about recent topics",
                mastery_level_summary="Level 5: Developing competence"
            ),
            "expected_adaptations": ["Medium difficulty", "More examples"]
        }
    ]
    
    for profile_info in student_profiles:
        print(f"\n--- {profile_info['name'].upper()} ---")
        print(f"Emotional State: {profile_info['profile'].emotional_state_summary}")
        print(f"Mastery Level: {profile_info['profile'].mastery_level_summary}")
        
        context = ConversationContext(
            student_message=base_message,
            chat_history=[],
            user_info=profile_info["profile"]
        )
        
        parameters = await extractor.extract_parameters(context)
        
        print(f"📊 Adapted difficulty: {parameters.get('difficulty', 'N/A')}")
        print(f"🔢 Suggested count: {parameters.get('count', 'N/A')}")
        print(f"🎯 Tool type: {parameters.get('tool_type', 'N/A')}")
        print(f"💭 Adaptation reasoning: {parameters.get('reasoning', 'N/A')}")

async def main():
    """Main demo function."""
    
    print("🚀 AUTONOMOUS AI TUTOR ORCHESTRATOR - CORE FUNCTIONALITY DEMO")
    print("="*80)
    print("This demo showcases the core intelligence of the orchestration system:")
    print("• Intelligent parameter extraction from natural conversation")
    print("• Automatic tool selection based on educational intent")  
    print("• Student profile adaptation for personalized responses")
    print("• Educational tool execution with proper validation")
    print("="*80)
    
    try:
        # Run demonstrations
        await demonstrate_parameter_extraction()
        await demonstrate_tool_execution()
        await demonstrate_student_adaptation()
        
        print(f"\n\n{'='*80}")
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        print(f"\n🎯 Key Achievements Demonstrated:")
        print("• ✅ Intelligent conversation analysis and intent recognition")
        print("• ✅ Context-aware parameter extraction with confidence scoring")
        print("• ✅ Automatic tool selection based on educational needs")
        print("• ✅ Student profile adaptation for personalized learning")
        print("• ✅ Schema validation and error handling")
        print("• ✅ Simulated educational tool execution")
        
        print(f"\n🏗️ Architecture Components Showcased:")
        print("• 🧠 Context Analysis Engine - Parses educational intent")
        print("• 🔍 Parameter Extraction System - Maps conversation to tool inputs")
        print("• 🛠️ Tool Orchestration Layer - Manages educational tool execution")
        print("• 🎭 Student Adaptation - Personalizes based on emotional state & mastery")
        print("• ✅ Schema Validation - Ensures proper tool input formatting")
        
        print(f"\n📚 Educational Tools Integrated:")
        print("• 📝 Note Maker - Generates structured educational notes")
        print("• 🃏 Flashcard Generator - Creates adaptive practice cards")
        print("• 📖 Concept Explainer - Provides detailed explanations with examples")
        
        print(f"\n🚀 Ready for Production Integration:")
        print("• Replace simulated tools with real educational API calls")
        print("• Add OpenAI API key for enhanced LLM-based parameter extraction")
        print("• Scale to 80+ educational tools using the same architecture")
        print("• Deploy with FastAPI for production-ready REST API")
        
    except Exception as e:
        print(f"\n❌ Demo encountered an error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())