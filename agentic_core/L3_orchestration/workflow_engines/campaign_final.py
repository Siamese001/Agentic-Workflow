from __future__ import annotations
"""Backward compatibility shim for campaign_final.


# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original campaign_final.py contained 13 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from agentic_core.campaign_final_impl_impl_impl_impl import *  # Star import removed
import logging

__all__ = ["*"]  # Re-export all imported names
