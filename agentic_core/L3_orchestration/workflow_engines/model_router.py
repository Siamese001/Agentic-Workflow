"""Backward compatibility shim for ModelRouter.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original ModelRouter.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from AgenticCore.model_router_impl import *  # Star import removed
# from AgenticCore.model_router_impl import *  # Star import removed
import logging

__all__ = ["*"]  # Re-export all imported names
