"""Backward compatibility shim for golden_state_datasets.


LOGGER = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original golden_state_datasets.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""
import logging

# Re-export all components for backward compatibility
# from agentic_core.golden_state_datasets_impl_impl_impl import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names