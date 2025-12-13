# -*- coding: utf-8 -*-
"""
pytest configuration and fixtures

This file provides essential configuration and utilities for the Agentic-Workflow system.
It includes comprehensive setup, testing configurations, and helper functions.

Key Components:
- Configuration management
- Test fixtures and utilities
- Common helper functions
- System initialization

Author: Agentic-Workflow Team
Version: 1.0.0
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configuration constants
DEFAULT_CONFIG = {
    "debug": False,
    "log_level": "INFO",
    "timeout": 30,
}

def get_config() -> Dict[str, Any]:
    """Get default configuration."""
    return DEFAULT_CONFIG.copy()

def setup_environment() -> None:
    """Setup the environment with required configurations."""
    os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))

# Initialize on import
setup_environment()

__all__ = [
    "get_config",
    "setup_environment",
    "PROJECT_ROOT",
    "DEFAULT_CONFIG",
]
