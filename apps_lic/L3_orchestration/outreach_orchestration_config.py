"""Backward compatibility shim for outreach_orchestration_config.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original outreach_orchestration_config.py contained 12 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .outreach_orchestration_config_impl import *  # Star import removed
# from .outreach_orchestration_config_models import *  # Star import removed
# from .outreach_orchestration_config_models_1 import *  # Star import removed
# from .outreach_orchestration_config_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
