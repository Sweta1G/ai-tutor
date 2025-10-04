"""
Demo script to showcase the Autonomous AI Tutor Orchestrator functionality.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from app.models.schemas import (
    UserInfo, 
    ChatMessage, 
    ConversationContext, 
    OrchestrationRequest,
    TeachingStyle
)
from app.services.orchestrator_service import OrchestratorService

async def create_demo_scenarios():
    """Create demonstration scenarios."""
    
    # Sample student profiles
    students = {
        "alice": UserInfo(
            user_id="alice_123",
            name="Alice Johnson",
            grade_level="10",
            learning_style_summary="Visual learner, prefers structured notes and diagrams",
            emotional_state_summary="Focused and motivated to learn",
            mastery_level_summary="Level 6: Good understanding, ready for application"
        ),
        "bob": UserInfo(
            user_id="bob_456",
            name="Bob Smith",
            grade_level="9",
            learning_style_summary="Kinesthetic learner, learns best through practice",
            emotional_state_summary="Anxious about upcoming test",
            mastery_level_summary="Level 3: Building foundational knowledge"
        ),
        "charlie": UserInfo(
            user_id="charlie_789",
            name="Charlie Wilson",
            grade_level="11",
            learning_style_summary="Analytical learner, enjoys detailed explanations",
            emotional_state_summary="Curious and engaged in learning",
            mastery_level_summary="Level 8: Advanced understanding, ready for complex topics"
        )
    }
    
    # Demo scenarios
    scenarios = [
        {
            "name": "Note Making Request",
            "student": students["alice"],
            "message": "I'm studying photosynthesis in biology and need organized notes for my exam next week",
            "chat_history": [
                ChatMessage(role="user", content="Hi, I need help with biology"),
                ChatMessage(role="assistant", content="I'd be happy to help with biology! What specific topic are you working on?")
            ]
        },
        {
            "name": "Flashcard Generation Request",
            "student": students["bob"],
            "message": "Can you make 10 flashcards for calculus derivatives? I need practice problems",
            "chat_history": [
                ChatMessage(role="user", content="I'm struggling with calculus"),
                ChatMessage(role="assistant", content="Calculus can be challenging. What specific area would you like to focus on?"),
                ChatMessage(role="user", content="Derivatives are really confusing me")
            ]
        },
        {
            "name": "Concept Explanation Request",
            "student": students["charlie"],
            "message": "I'm confused about quantum mechanics and wave-particle duality. Can you explain it in detail?",
            "chat_history": [
                ChatMessage(role="user", content="I'm taking advanced physics this semester"),
                ChatMessage(role="assistant", content="That's exciting! Advanced physics opens up many fascinating concepts. What are you currently studying?")
            ]
        }
    ]
    
    return scenarios

async def run_demo_scenario(orchestrator: OrchestratorService, scenario: Dict[str, Any], scenario_num: int):
    """Run a single demo scenario."""
    
    print(f"\n{'='*60}")
    print(f"DEMO SCENARIO {scenario_num}: {scenario['name']}")
    print(f"{'='*60}")
    
    # Create conversation context
    context = ConversationContext(
        student_message=scenario["message"],
        chat_history=scenario["chat_history"],
        user_info=scenario["student"]
    )
    
    # Create orchestration request
    request = OrchestrationRequest(
        conversation_context=context,
        preferred_teaching_style=TeachingStyle.VISUAL,
        session_id=f"demo_session_{scenario_num}"
    )
    
    print(f"\nStudent: {scenario['student'].name} (Grade {scenario['student'].grade_level})")
    print(f"Learning Style: {scenario['student'].learning_style_summary}")
    print(f"Emotional State: {scenario['student'].emotional_state_summary}")
    print(f"Mastery Level: {scenario['student'].mastery_level_summary}")
    print(f"\nStudent Message: '{scenario['message']}'")
    
    try:
        # Process the request
        print(f"\n🤖 Processing orchestration request...")
        
        start_time = datetime.now()
        response = await orchestrator.process_request(request, request.session_id)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"\n✅ Orchestration completed in {processing_time:.2f} seconds")
        print(f"\n📊 RESULTS:")
        print(f"Session ID: {response.session_id}")
        
        # Display extracted parameters
        print(f"\n🔍 Extracted Parameters:")
        for key, value in response.extracted_parameters.items():
            if key not in ["timestamp", "extraction_method"]:
                print(f"  • {key}: {value}")
        
        # Display executed tools
        print(f"\n🛠️ Executed Tools:")
        for tool_result in response.executed_tools:
            status = "✅ Success" if tool_result.success else "❌ Failed"
            print(f"  • {tool_result.tool_name}: {status} ({tool_result.execution_time:.2f}s)")
            
            if tool_result.success and tool_result.output:
                # Display key output information
                output = tool_result.output
                if tool_result.tool_name == "note_maker":
                    print(f"    - Generated notes: '{output.get('title', 'N/A')}'")
                    print(f"    - Note sections: {len(output.get('note_sections', []))}")
                    print(f"    - Key concepts: {len(output.get('key_concepts', []))}")
                
                elif tool_result.tool_name == "flashcard_generator":
                    print(f"    - Generated flashcards: {len(output.get('flashcards', []))}")
                    print(f"    - Difficulty: {output.get('difficulty', 'N/A')}")
                    print(f"    - Topic: {output.get('topic', 'N/A')}")
                
                elif tool_result.tool_name == "concept_explainer":
                    print(f"    - Explanation provided for concept")
                    print(f"    - Examples: {len(output.get('examples', []))}")
                    print(f"    - Related concepts: {len(output.get('related_concepts', []))}")
            
            elif not tool_result.success:
                print(f"    - Error: {tool_result.error_message}")
        
        # Display reasoning
        print(f"\n💭 System Reasoning:")
        print(f"  {response.reasoning}")
        
        # Display conversation state
        if response.conversation_state:
            print(f"\n💾 Updated Conversation State:")
            for key, value in response.conversation_state.items():
                if key != "execution_timestamp":
                    print(f"  • {key}: {value}")
        
    except Exception as e:
        print(f"\n❌ Error processing scenario: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main demo function."""
    
    print("🚀 AUTONOMOUS AI TUTOR ORCHESTRATOR DEMO")
    print("="*60)
    print("This demo showcases intelligent parameter extraction and tool orchestration")
    print("for educational AI tutoring systems.\n")
    
    # Initialize orchestrator
    print("🔧 Initializing orchestrator service...")
    orchestrator = OrchestratorService()
    
    # Create demo scenarios
    print("📝 Creating demo scenarios...")
    scenarios = await create_demo_scenarios()
    
    # Run each scenario
    for i, scenario in enumerate(scenarios, 1):
        await run_demo_scenario(orchestrator, scenario, i)
        
        # Add pause between scenarios
        if i < len(scenarios):
            print(f"\n⏸️  Pausing for 2 seconds before next scenario...")
            await asyncio.sleep(2)
    
    print(f"\n{'='*60}")
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("• Intelligent parameter extraction from natural conversation")
    print("• Automatic tool selection based on educational intent")
    print("• Student profile adaptation for personalized responses")
    print("• Multi-tool orchestration with proper error handling")
    print("• Session state management and conversation tracking")
    print("• Comprehensive reasoning and result presentation")
    
    print(f"\n📚 Educational Tools Integrated:")
    print("• Note Maker - Structured note generation")
    print("• Flashcard Generator - Adaptive practice cards")
    print("• Concept Explainer - Detailed explanations with examples")
    
    print(f"\n🎯 Architecture Components:")
    print("• Context Analysis Engine - Parses conversation intent")
    print("• Parameter Extraction System - Maps chat to tool parameters")
    print("• Tool Orchestration Layer - Manages multi-tool execution")
    print("• State Management - Maintains conversation context")
    print("• LangGraph Workflow - Orchestrates the entire process")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())