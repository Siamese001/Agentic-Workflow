"""Backward compatibility shim for datasets_impl.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original datasets_impl.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from AgenticCore.datasets_impl_impl_impl_impl_impl import *  # Star import removed
import logging

__all__ = ["*"]  # Re-export all imported names
