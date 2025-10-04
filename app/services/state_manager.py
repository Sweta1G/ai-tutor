"""
State management service for maintaining conversation context and student data.
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SessionData:
    """Session data structure."""
    session_id: str
    user_id: str
    created_at: datetime
    last_accessed: datetime
    state: Dict[str, Any]
    conversation_history: list
    student_preferences: Dict[str, Any]

class StateManager:
    """Manages conversation state and session data."""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, this would use Redis or a database
        self._sessions: Dict[str, SessionData] = {}
        self._session_timeout = timedelta(hours=24)
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_expired_sessions())
    
    async def load_session_state(self, session_id: str, orchestration_state) -> None:
        """Load existing session state into orchestration state."""
        
        session_data = self._sessions.get(session_id)
        
        if session_data:
            # Update last accessed time
            session_data.last_accessed = datetime.utcnow()
            
            # Load previous context if available
            if session_data.state:
                logger.info(f"Loaded existing session state for: {session_id}")
                
                # Add previous context to current request
                previous_tools = session_data.state.get("last_tools_used", [])
                previous_parameters = session_data.state.get("last_parameters", {})
                
                # You could use this information to inform current processing
                orchestration_state.extracted_parameters.update({
                    "previous_tools": previous_tools,
                    "previous_parameters": previous_parameters
                })
        else:
            # Create new session
            logger.info(f"Creating new session: {session_id}")
            
            session_data = SessionData(
                session_id=session_id,
                user_id=orchestration_state.request.conversation_context.user_info.user_id,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                state={},
                conversation_history=[],
                student_preferences={}
            )
            
            self._sessions[session_id] = session_data
    
    async def save_session_state(self, session_id: str, orchestration_state) -> None:
        """Save orchestration state to session storage."""
        
        session_data = self._sessions.get(session_id)
        
        if not session_data:
            logger.warning(f"No session data found for: {session_id}")
            return
        
        try:
            # Update session state
            session_data.state = {
                "last_tools_used": orchestration_state.selected_tools,
                "last_parameters": orchestration_state.extracted_parameters,
                "last_execution_results": [
                    {
                        "tool_name": result.tool_name,
                        "success": result.success,
                        "execution_time": result.execution_time
                    }
                    for result in orchestration_state.tool_results
                ],
                "execution_timestamp": datetime.utcnow().isoformat()
            }
            
            # Update conversation history
            current_message = {
                "role": "user",
                "content": orchestration_state.request.conversation_context.student_message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            session_data.conversation_history.append(current_message)
            
            # Keep only last 20 messages to prevent memory bloat
            if len(session_data.conversation_history) > 20:
                session_data.conversation_history = session_data.conversation_history[-20:]
            
            # Update student preferences based on usage patterns
            await self._update_student_preferences(session_data, orchestration_state)
            
            session_data.last_accessed = datetime.utcnow()
            
            logger.info(f"Saved session state for: {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving session state: {e}")
    
    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current session state."""
        
        session_data = self._sessions.get(session_id)
        
        if not session_data:
            return None
        
        return {
            "session_id": session_data.session_id,
            "user_id": session_data.user_id,
            "created_at": session_data.created_at.isoformat(),
            "last_accessed": session_data.last_accessed.isoformat(),
            "state": session_data.state,
            "conversation_history": session_data.conversation_history,
            "student_preferences": session_data.student_preferences
        }
    
    async def update_student_profile(
        self, 
        session_id: str, 
        profile_updates: Dict[str, Any]
    ) -> bool:
        """Update student profile information."""
        
        session_data = self._sessions.get(session_id)
        
        if not session_data:
            return False
        
        try:
            # Update student preferences
            session_data.student_preferences.update(profile_updates)
            session_data.last_accessed = datetime.utcnow()
            
            logger.info(f"Updated student profile for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating student profile: {e}")
            return False
    
    async def get_student_learning_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get learning analytics for a specific student across all sessions."""
        
        user_sessions = [
            session for session in self._sessions.values() 
            if session.user_id == user_id
        ]
        
        if not user_sessions:
            return {}
        
        # Aggregate analytics
        total_sessions = len(user_sessions)
        total_tools_used = {}
        total_execution_time = 0
        most_recent_session = max(user_sessions, key=lambda s: s.last_accessed)
        
        for session in user_sessions:
            if session.state.get("last_execution_results"):
                for result in session.state["last_execution_results"]:
                    tool_name = result["tool_name"]
                    total_tools_used[tool_name] = total_tools_used.get(tool_name, 0) + 1
                    total_execution_time += result.get("execution_time", 0)
        
        return {
            "user_id": user_id,
            "total_sessions": total_sessions,
            "tools_usage": total_tools_used,
            "total_execution_time": total_execution_time,
            "most_used_tool": max(total_tools_used, key=total_tools_used.get) if total_tools_used else None,
            "last_session": most_recent_session.last_accessed.isoformat(),
            "student_preferences": most_recent_session.student_preferences,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _update_student_preferences(
        self, 
        session_data: SessionData, 
        orchestration_state
    ) -> None:
        """Update student preferences based on usage patterns."""
        
        try:
            # Track tool preferences
            tool_usage = session_data.student_preferences.get("tool_usage", {})
            
            for tool_name in orchestration_state.selected_tools:
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
            
            session_data.student_preferences["tool_usage"] = tool_usage
            
            # Track parameter preferences
            params = orchestration_state.extracted_parameters
            
            if params.get("difficulty"):
                session_data.student_preferences["preferred_difficulty"] = params["difficulty"]
            
            if params.get("note_taking_style"):
                session_data.student_preferences["preferred_note_style"] = params["note_taking_style"]
            
            if params.get("desired_depth"):
                session_data.student_preferences["preferred_explanation_depth"] = params["desired_depth"]
            
            # Track successful interactions
            successful_tools = [
                result.tool_name for result in orchestration_state.tool_results 
                if result.success
            ]
            
            if successful_tools:
                session_data.student_preferences["recent_successful_tools"] = successful_tools
            
        except Exception as e:
            logger.error(f"Error updating student preferences: {e}")
    
    async def _cleanup_expired_sessions(self) -> None:
        """Periodically clean up expired sessions."""
        
        while True:
            try:
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session_data in self._sessions.items():
                    if current_time - session_data.last_accessed > self._session_timeout:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self._sessions[session_id]
                    logger.info(f"Cleaned up expired session: {session_id}")
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
            
            # Sleep for 1 hour before next cleanup
            await asyncio.sleep(3600)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        return len(self._sessions)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of all sessions."""
        
        total_sessions = len(self._sessions)
        unique_users = len(set(session.user_id for session in self._sessions.values()))
        
        oldest_session = None
        if self._sessions:
            oldest_session = min(
                self._sessions.values(), 
                key=lambda s: s.created_at
            ).created_at.isoformat()
        
        return {
            "total_active_sessions": total_sessions,
            "unique_users": unique_users,
            "oldest_session_created": oldest_session,
            "session_timeout_hours": self._session_timeout.total_seconds() / 3600,
            "timestamp": datetime.utcnow().isoformat()
        }