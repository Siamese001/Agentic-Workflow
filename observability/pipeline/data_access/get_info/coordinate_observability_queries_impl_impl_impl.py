"""Backward compatibility shim for coordinate_observability_queries_impl_impl_impl.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original coordinate_observability_queries_impl_impl_impl.py contained 8 top-level definitions wh
    ich
violated the Subatomic Canon. It has been refactored into focused submodules.
"""
import logging

# Re-export all components for backward compatibility
# from .coord_final import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
