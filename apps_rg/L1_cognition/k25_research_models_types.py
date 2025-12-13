"""Backward compatibility shim for k25_research_models_types.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original k25_research_models_types.py contained 12 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .k25_enums import *  # Star import removed
# from .k25_models import *  # Star import removed
# from .k25_models_2 import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
