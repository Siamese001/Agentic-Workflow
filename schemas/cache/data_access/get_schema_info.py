"""Backward compatibility shim for get_schema_info.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original get_schema_info.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .get_schema_info_types import *  # Star import removed
# from .get_schema_info_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
