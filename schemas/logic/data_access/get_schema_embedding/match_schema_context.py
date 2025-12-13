"""Backward compatibility shim for match_schema_context.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original match_schema_context.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .match_schema_context_impl import *
from .match_schema_context_models import *
from .match_schema_context_models_1 import *
from .match_schema_context_impl import *

__all__ = ['*']  # Re-export all imported names
