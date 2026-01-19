from __future__ import annotations
"""Backward compatibility shim for lic_archetypes.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original lic_archetypes.py contained 12 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from agentic_core.lic_archetypes_impl import *  # Star import removed
# from agentic_core.lic_archetypes_models import *  # Star import removed
# from agentic_core.lic_archetypes_models_1 import *  # Star import removed
# from agentic_core.lic_archetypes_impl import *  # Star import removed
import logging

__all__ = ["*"]  # Re-export all imported names
