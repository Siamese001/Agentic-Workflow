"""Backward compatibility shim for load_schema_planning.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original load_schema_planning.py contained 12 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .load_schema_planning_enums import *
from .load_schema_planning_models import *
from .load_schema_planning_models_1 import *
from .load_schema_planning_impl import *

__all__ = ['*']  # Re-export all imported names
