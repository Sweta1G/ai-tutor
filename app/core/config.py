"""
Configuration management for the Autonomous AI Tutor Orchestrator.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql://localhost/tutor_orchestrator"
    redis_url: str = "redis://localhost:6379"
    
    # API Keys
    openai_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    
    # Educational Tools URLs
    note_maker_api_url: str = "http://localhost:8001/api/v1/note-maker"
    flashcard_api_url: str = "http://localhost:8002/api/v1/flashcard-generator"
    concept_explainer_api_url: str = "http://localhost:8003/api/v1/concept-explainer"
    
    # Application
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    log_level: str = "INFO"
    
    # Security
    secret_key: str = "development-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings