"""
Autonomous AI Tutor Orchestrator

Main FastAPI application entry point.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import os

from .routes import orchestrator, health
from .core.config import get_settings
from .core.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Autonomous AI Tutor Orchestrator...")
    yield
    logger.info("Shutting down Autonomous AI Tutor Orchestrator...")

# Create FastAPI application
app = FastAPI(
    title="Autonomous AI Tutor Orchestrator",
    description="Intelligent middleware that orchestrates educational tools through conversational AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(orchestrator.router, prefix="/api/v1", tags=["Orchestrator"])

@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "name": "Autonomous AI Tutor Orchestrator",
        "version": "1.0.0",
        "description": "Intelligent middleware for educational tool orchestration",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )