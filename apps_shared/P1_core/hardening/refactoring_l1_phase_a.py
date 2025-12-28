"""Backward compatibility shim for refactoring_l1_phase_a.


LOGGER = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original refactoring_l1_phase_a.py contained 10 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
import logging

__all__ = ["*"]  # Re-export all imported names
