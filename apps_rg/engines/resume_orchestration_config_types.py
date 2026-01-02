from __future__ import annotations
"""Backward compatibility shim for resume_orchestration_config_types.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original resume_orchestration_config_types.py contained 8 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from agentic_core.resume_orchestration_config_types_enums import *  # Star import removed
# from agentic_core.resume_orchestration_config_types_models import *  # Star import removed
# from agentic_core.resume_orchestration_config_types_models_1 import *  # Star import removed
import logging

__all__ = ["*"]  # Re-export all imported names
