"""
Logging configuration for the Autonomous AI Tutor Orchestrator.
"""

import logging
import logging.config
from typing import Dict, Any
import os

def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "mode": "a"
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            }
        }
    }
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    logging.config.dictConfig(config)