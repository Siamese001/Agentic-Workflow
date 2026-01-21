from __future__ import annotations

import logging

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from typing import Any

_logger = logging.getLogger(__name__)
"\npytest configuration and fixtures\n\nThis file provides essential configuration and utilities for the Agentic-Workflow system.\nIt includes comprehensive setup, testing configurations, and helper functions.\n\nKey Components:\n- Configuration management\n- Test fixtures and utilities\n- Common helper functions\n- System initialization\n\nAuthor: Agentic-Workflow Team\nVersion: 1.0.0\n"
import os
import sys
from pathlib import Path

project_root: Any = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
default_config: Any = {"debug": False, "log_level": "INFO", "timeout": 30}


def get_config() -> dict[str, Any]:
    """Get default configuration."""
    return DEFAULT_CONFIG.copy()


def setup_environment() -> None:
    """Setup the environment with required configurations."""
    os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))


setup_environment()
__all__ = ["get_config", "setup_environment", "PROJECT_ROOT", "DEFAULT_CONFIG"]
