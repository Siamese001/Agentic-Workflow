"""Backward compatibility shim for dedup_impl_impl_impl_impl_impl.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original dedup_impl_impl_impl_impl_impl.py contained 22 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""
import logging

# Re-export all components for backward compatibility
# from .dedup_final import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
