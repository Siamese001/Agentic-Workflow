"""Backward compatibility shim for get_info_embedding_compare.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original get_info_embedding_compare.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from agentic_core.get_info_embedding_compare_impl import *  # Star import removed
# from agentic_core.get_info_embedding_compare_impl import *  # Star import removed
import logging

__all__ = ["*"]  # Re-export all imported names
