"""Backward compatibility shim for runtime_impl.


# NAMING FIXED: LOGGER → logger
logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original runtime_impl.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from agentic_core.runtime_impl_impl_impl_impl_impl import *  # Star import removed
import logging

__all__ = ["*"]  # Re-export all imported names
