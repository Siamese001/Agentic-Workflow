"""Backward compatibility shim for rg_creative_brief.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original rg_creative_brief.py contained 18 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .rg_creative_brief_enums import *
from .rg_creative_brief_models import *
from .rg_creative_brief_models_1 import *
from .brief_models_2 import *
from .rg_creative_brief_impl import *

__all__ = ['*']  # Re-export all imported names
