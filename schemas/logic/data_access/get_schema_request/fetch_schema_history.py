"""Backward compatibility shim for fetch_schema_history.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original fetch_schema_history.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .fetch_schema_history_enums import *
from .fetch_schema_history_models import *
from .fetch_schema_history_models_1 import *
from .fetch_schema_history_impl import *

__all__ = ['*']  # Re-export all imported names
