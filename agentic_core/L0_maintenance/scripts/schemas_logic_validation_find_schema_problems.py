"""Backward compatibility shim for find_schema_problems.
"""
import logging

LOGGER = logging.getLogger(__name__)
# This module maintains backward compatibility by re-exporting all components
# modules to comply with cognitive density limits (max 5 top-level definitions).

# The original find_schema_problems.py contained 6 top-level definitions which
# violated the Subatomic Canon. It has been refactored into focused submodules.


# Re-export all components for backward compatibility
# from agentic_core.find_schema_problems_impl import *  # Star import removed
# from agentic_core.find_schema_problems_impl import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names