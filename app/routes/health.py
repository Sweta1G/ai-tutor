"""
Health check endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
import psutil
import os
from datetime import datetime

router = APIRouter()

class HealthStatus(BaseModel):
    """Health status response model."""
    status: str
    timestamp: datetime
    version: str
    system_info: dict

@router.get("/", response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint."""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        system_info={
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        }
    )

@router.get("/ready")
async def readiness_check():
    """Readiness check for orchestration services."""
    # Add checks for external dependencies here
    return {"status": "ready", "timestamp": datetime.utcnow()}

@router.get("/live")
async def liveness_check():
    """Liveness check for container orchestration."""
    return {"status": "alive", "timestamp": datetime.utcnow()}