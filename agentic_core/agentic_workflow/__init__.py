"""
Agentic Workflow - Main package entry point.

This package provides a unified interface to all agentic workflow components,
including runtime logic, shared utilities, and agent frameworks.
"""
import logging

LOGGER = logging.getLogger(__name__)

__version__ = "1.0.0"

# Import key components for easy access
# These imports make submodules/subpackages accessible directly under the
# 'agentic_workflow' namespace (e.g., agentic_workflow.runtime).
# They are also listed in __all__ for 'from agentic_workflow import *' usage.
from . import runtime, shared

__all__ = ["runtime", "shared"]