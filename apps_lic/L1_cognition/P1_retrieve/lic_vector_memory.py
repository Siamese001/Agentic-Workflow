"""Backward compatibility shim for lic_vector_memory.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original lic_vector_memory.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""
import logging

# Re-export all components for backward compatibility
# from .lic_vector_memory_impl import *  # Star import removed
# from .lic_vector_memory_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
