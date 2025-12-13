"""Backward compatibility shim for k25_research_models_types.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original k25_research_models_types.py contained 12 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .k25_research_models_types_enums import *
from .k25_research_models_types_models import *
from .k25_research_models_types_models_1 import *
from .k25_research_models_types_models_2 import *

__all__ = ['*']  # Re-export all imported names
