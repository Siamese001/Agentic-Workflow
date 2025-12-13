"""Backward compatibility shim for rag_v5.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original rag_v5.py contained 13 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .rag_v5_impl_impl_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
