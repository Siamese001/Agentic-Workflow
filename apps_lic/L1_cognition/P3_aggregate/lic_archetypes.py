"""Backward compatibility shim for lic_archetypes.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original lic_archetypes.py contained 12 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .lic_archetypes_enums import *
from .lic_archetypes_models import *
from .lic_archetypes_models_1 import *
from .lic_archetypes_impl import *

__all__ = ['*']  # Re-export all imported names
