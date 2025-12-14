"""

logger = logging.getLogger(__name__)
Agentic Workflow - Main package entry point.

This package provides a unified interface to all agentic workflow components,
including runtime logic, shared utilities, and agent frameworks.
"""

__version__ = "1.0.0"

# Import key components for easy access
from . import runtime
from . import shared
import logging

__all__ = ["runtime", "shared"]
