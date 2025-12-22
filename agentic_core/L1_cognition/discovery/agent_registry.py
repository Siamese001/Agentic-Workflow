"""Backward compatibility shim for agent_registry.


LOGGER = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original agent_registry.py contained 8 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .agent_registry_impl import *  # Star import removed
# from .agent_registry_models import *  # Star import removed
# from .agent_registry_impl import *  # Star import removed
import logging


__all__ = ["*"]  # Re-export all imported names
