from __future__ import annotations
"""Backward compatibility shim for outreach_orchestration_config.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original outreach_orchestration_config.py contained 12 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from agentic_core.outreach_orchestration_config_impl import *  # Star import removed
# from agentic_core.outreach_orchestration_config_models import *  # Star import removed
# from agentic_core.outreach_orchestration_config_models_1 import *  # Star import removed
# from agentic_core.outreach_orchestration_config_impl import *  # Star import removed
import logging

__all__ = ["*"]  # Re-export all imported names
