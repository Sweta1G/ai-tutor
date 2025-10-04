"""
Main orchestration service using LangGraph for workflow management.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from ..models.schemas import (
    OrchestrationRequest, 
    OrchestrationResponse,
    ConversationContext,
    ToolExecutionResult,
    UserInfo
)
from .parameter_extractor import ParameterExtractor
from .tool_manager import ToolManager
from .state_manager import StateManager

logger = logging.getLogger(__name__)

class OrchestrationState(BaseModel):
    """State object for LangGraph workflow."""
    
    # Input data
    request: OrchestrationRequest
    session_id: str
    
    # Processing state
    extracted_parameters: Dict[str, Any] = {}
    selected_tools: List[str] = []
    tool_inputs: Dict[str, Dict[str, Any]] = {}
    tool_results: List[ToolExecutionResult] = []
    
    # Output state
    response: Optional[OrchestrationResponse] = None
    error: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

class OrchestratorService:
    """Main orchestration service using LangGraph workflows."""
    
    def __init__(self):
        self.parameter_extractor = ParameterExtractor()
        self.tool_manager = ToolManager()
        self.state_manager = StateManager()
        
        # Build the orchestration workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for orchestration."""
        
        workflow = StateGraph(OrchestrationState)
        
        # Add nodes
        workflow.add_node("extract_parameters", self._extract_parameters_node)
        workflow.add_node("select_tools", self._select_tools_node)
        workflow.add_node("prepare_tool_inputs", self._prepare_tool_inputs_node)
        workflow.add_node("execute_tools", self._execute_tools_node)
        workflow.add_node("build_response", self._build_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Define the workflow edges
        workflow.set_entry_point("extract_parameters")
        
        workflow.add_edge("extract_parameters", "select_tools")
        workflow.add_edge("select_tools", "prepare_tool_inputs")
        workflow.add_edge("prepare_tool_inputs", "execute_tools")
        workflow.add_edge("execute_tools", "build_response")
        workflow.add_edge("build_response", END)
        workflow.add_edge("handle_error", END)
        
        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "extract_parameters",
            self._check_for_errors,
            {
                "continue": "select_tools",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "execute_tools",
            self._check_execution_results,
            {
                "success": "build_response",
                "partial_success": "build_response",
                "error": "handle_error"
            }
        )
        
        return workflow.compile()
    
    async def process_request(
        self, 
        request: OrchestrationRequest, 
        session_id: str
    ) -> OrchestrationResponse:
        """
        Process an orchestration request through the LangGraph workflow.
        
        Args:
            request: The orchestration request
            session_id: Session identifier
            
        Returns:
            Orchestration response with results
        """
        
        logger.info(f"Processing orchestration request for session: {session_id}")
        
        # Initialize state
        initial_state = OrchestrationState(
            request=request,
            session_id=session_id
        )
        
        try:
            # Load existing session state
            await self.state_manager.load_session_state(session_id, initial_state)
            
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Save session state
            await self.state_manager.save_session_state(session_id, final_state)
            
            if final_state.error:
                raise Exception(final_state.error)
            
            return final_state.response
            
        except Exception as e:
            logger.error(f"Error in orchestration workflow: {e}")
            
            # Return error response
            return OrchestrationResponse(
                session_id=session_id,
                executed_tools=[],
                extracted_parameters={},
                reasoning=f"Orchestration failed: {str(e)}",
                conversation_state={}
            )
    
    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a session."""
        return await self.state_manager.get_session_state(session_id)
    
    # Workflow node implementations
    
    async def _extract_parameters_node(self, state: OrchestrationState) -> OrchestrationState:
        """Extract parameters from conversation context."""
        
        try:
            logger.info(f"Extracting parameters for session: {state.session_id}")
            
            parameters = await self.parameter_extractor.extract_parameters(
                state.request.conversation_context
            )
            
            state.extracted_parameters = parameters
            logger.info(f"Successfully extracted parameters: {list(parameters.keys())}")
            
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
            state.error = f"Parameter extraction failed: {str(e)}"
        
        return state
    
    async def _select_tools_node(self, state: OrchestrationState) -> OrchestrationState:
        """Select appropriate tools based on extracted parameters."""
        
        try:
            tool_type = state.extracted_parameters.get("tool_type")
            
            if tool_type:
                state.selected_tools = [tool_type]
                logger.info(f"Selected tool: {tool_type}")
            else:
                # Fallback: select based on conversation analysis
                message = state.request.conversation_context.student_message.lower()
                
                if any(word in message for word in ["notes", "summary", "outline"]):
                    state.selected_tools = ["note_maker"]
                elif any(word in message for word in ["flashcard", "quiz", "practice"]):
                    state.selected_tools = ["flashcard_generator"]
                else:
                    state.selected_tools = ["concept_explainer"]
                
                logger.info(f"Fallback tool selection: {state.selected_tools}")
            
        except Exception as e:
            logger.error(f"Error selecting tools: {e}")
            state.error = f"Tool selection failed: {str(e)}"
        
        return state
    
    async def _prepare_tool_inputs_node(self, state: OrchestrationState) -> OrchestrationState:
        """Prepare input parameters for selected tools."""
        
        try:
            for tool_name in state.selected_tools:
                tool_input = self._build_tool_input(
                    tool_name, 
                    state.extracted_parameters,
                    state.request.conversation_context
                )
                
                state.tool_inputs[tool_name] = tool_input
                logger.info(f"Prepared input for tool: {tool_name}")
            
        except Exception as e:
            logger.error(f"Error preparing tool inputs: {e}")
            state.error = f"Tool input preparation failed: {str(e)}"
        
        return state
    
    async def _execute_tools_node(self, state: OrchestrationState) -> OrchestrationState:
        """Execute the selected tools with prepared inputs."""
        
        results = []
        
        for tool_name in state.selected_tools:
            start_time = datetime.utcnow()
            
            try:
                tool_input = state.tool_inputs[tool_name]
                output = await self.tool_manager.execute_tool(tool_name, tool_input)
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                result = ToolExecutionResult(
                    tool_name=tool_name,
                    success=True,
                    output=output,
                    execution_time=execution_time
                )
                
                logger.info(f"Successfully executed tool: {tool_name}")
                
            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                result = ToolExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    error_message=str(e),
                    execution_time=execution_time
                )
                
                logger.error(f"Error executing tool {tool_name}: {e}")
            
            results.append(result)
        
        state.tool_results = results
        return state
    
    async def _build_response_node(self, state: OrchestrationState) -> OrchestrationState:
        """Build the final orchestration response."""
        
        try:
            reasoning = self._generate_reasoning(state)
            
            conversation_state = {
                "last_tools_used": state.selected_tools,
                "last_parameters": state.extracted_parameters,
                "execution_timestamp": datetime.utcnow().isoformat(),
                "user_id": state.request.conversation_context.user_info.user_id
            }
            
            response = OrchestrationResponse(
                session_id=state.session_id,
                executed_tools=state.tool_results,
                extracted_parameters=state.extracted_parameters,
                reasoning=reasoning,
                conversation_state=conversation_state
            )
            
            state.response = response
            logger.info(f"Built orchestration response for session: {state.session_id}")
            
        except Exception as e:
            logger.error(f"Error building response: {e}")
            state.error = f"Response building failed: {str(e)}"
        
        return state
    
    async def _handle_error_node(self, state: OrchestrationState) -> OrchestrationState:
        """Handle errors in the workflow."""
        
        logger.error(f"Handling error in workflow: {state.error}")
        
        # Create error response
        response = OrchestrationResponse(
            session_id=state.session_id,
            executed_tools=[],
            extracted_parameters=state.extracted_parameters,
            reasoning=f"Orchestration encountered an error: {state.error}",
            conversation_state={}
        )
        
        state.response = response
        return state
    
    # Helper methods
    
    def _check_for_errors(self, state: OrchestrationState) -> str:
        """Check if there are errors that should halt the workflow."""
        return "error" if state.error else "continue"
    
    def _check_execution_results(self, state: OrchestrationState) -> str:
        """Check the results of tool execution."""
        
        if not state.tool_results:
            return "error"
        
        success_count = sum(1 for result in state.tool_results if result.success)
        
        if success_count == len(state.tool_results):
            return "success"
        elif success_count > 0:
            return "partial_success"
        else:
            return "error"
    
    def _build_tool_input(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any],
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Build input for a specific tool."""
        
        # Base user info for all tools
        tool_input = {
            "user_info": context.user_info.dict()
        }
        
        if tool_name == "note_maker":
            tool_input.update({
                "chat_history": [msg.dict() for msg in context.chat_history],
                "topic": parameters.get("topic", "General Topic"),
                "subject": parameters.get("subject", "General Subject"),
                "note_taking_style": parameters.get("note_taking_style", "structured"),
                "include_examples": parameters.get("include_examples", True),
                "include_analogies": parameters.get("include_analogies", False)
            })
            
        elif tool_name == "flashcard_generator":
            tool_input.update({
                "topic": parameters.get("topic", "General Topic"),
                "count": parameters.get("count", 10),
                "difficulty": parameters.get("difficulty", "medium"),
                "include_examples": parameters.get("include_examples", True),
                "subject": parameters.get("subject", "General Subject")
            })
            
        elif tool_name == "concept_explainer":
            tool_input.update({
                "chat_history": [msg.dict() for msg in context.chat_history],
                "concept_to_explain": parameters.get("concept_to_explain", parameters.get("topic", "General Concept")),
                "current_topic": parameters.get("current_topic", parameters.get("subject", "General Topic")),
                "desired_depth": parameters.get("desired_depth", "intermediate")
            })
        
        return tool_input
    
    def _generate_reasoning(self, state: OrchestrationState) -> str:
        """Generate reasoning explanation for the orchestration process."""
        
        reasoning_parts = []
        
        # Parameter extraction reasoning
        if state.extracted_parameters.get("reasoning"):
            reasoning_parts.append(f"Parameter extraction: {state.extracted_parameters['reasoning']}")
        
        # Tool selection reasoning
        if state.selected_tools:
            reasoning_parts.append(f"Selected tools: {', '.join(state.selected_tools)}")
        
        # Execution results
        successful_tools = [r.tool_name for r in state.tool_results if r.success]
        if successful_tools:
            reasoning_parts.append(f"Successfully executed: {', '.join(successful_tools)}")
        
        failed_tools = [r.tool_name for r in state.tool_results if not r.success]
        if failed_tools:
            reasoning_parts.append(f"Failed to execute: {', '.join(failed_tools)}")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Orchestration completed"