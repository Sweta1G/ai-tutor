"""
Main orchestration endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
import uuid
from datetime import datetime

from ..models.schemas import (
    OrchestrationRequest, 
    OrchestrationResponse,
    ConversationContext,
    ToolExecutionResult
)
from ..services.orchestrator_service import OrchestratorService
from ..services.parameter_extractor import ParameterExtractor
from ..services.tool_manager import ToolManager

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency injection
def get_orchestrator_service() -> OrchestratorService:
    """Get orchestrator service instance."""
    return OrchestratorService()

def get_parameter_extractor() -> ParameterExtractor:
    """Get parameter extractor instance."""
    return ParameterExtractor()

def get_tool_manager() -> ToolManager:
    """Get tool manager instance."""
    return ToolManager()

@router.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_tools(
    request: OrchestrationRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service)
) -> OrchestrationResponse:
    """
    Main orchestration endpoint that processes conversational context
    and executes appropriate educational tools.
    """
    try:
        logger.info(f"Processing orchestration request for user: {request.conversation_context.user_info.user_id}")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process the request through the orchestrator
        result = await orchestrator.process_request(request, session_id)
        
        logger.info(f"Successfully processed orchestration request: {session_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing orchestration request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

@router.post("/extract-parameters")
async def extract_parameters(
    context: ConversationContext,
    extractor: ParameterExtractor = Depends(get_parameter_extractor)
) -> Dict[str, Any]:
    """
    Extract parameters from conversational context for testing purposes.
    """
    try:
        logger.info(f"Extracting parameters for user: {context.user_info.user_id}")
        
        parameters = await extractor.extract_parameters(context)
        
        return {
            "extracted_parameters": parameters,
            "timestamp": datetime.utcnow(),
            "user_id": context.user_info.user_id
        }
        
    except Exception as e:
        logger.error(f"Error extracting parameters: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parameter extraction failed: {str(e)}")

@router.get("/tools")
async def list_available_tools(
    tool_manager: ToolManager = Depends(get_tool_manager)
) -> Dict[str, Any]:
    """
    List all available educational tools and their schemas.
    """
    try:
        tools = await tool_manager.get_available_tools()
        return {
            "tools": tools,
            "count": len(tools),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@router.post("/validate-tool-input")
async def validate_tool_input(
    tool_name: str,
    input_data: Dict[str, Any],
    tool_manager: ToolManager = Depends(get_tool_manager)
) -> Dict[str, Any]:
    """
    Validate input data against a specific tool's schema.
    """
    try:
        is_valid, errors = await tool_manager.validate_tool_input(tool_name, input_data)
        
        return {
            "tool_name": tool_name,
            "is_valid": is_valid,
            "errors": errors,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error validating tool input: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.get("/session/{session_id}/state")
async def get_session_state(
    session_id: str,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service)
) -> Dict[str, Any]:
    """
    Get the current state of a conversation session.
    """
    try:
        state = await orchestrator.get_session_state(session_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return {
            "session_id": session_id,
            "state": state,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session state: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session state: {str(e)}")