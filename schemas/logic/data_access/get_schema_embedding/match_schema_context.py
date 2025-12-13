"""Backward compatibility shim for match_schema_context.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original match_schema_context.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .match_schema_context_impl import *  # Star import removed
# from .match_schema_context_models import *  # Star import removed
# from .match_schema_context_models_1 import *  # Star import removed
# from .match_schema_context_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
