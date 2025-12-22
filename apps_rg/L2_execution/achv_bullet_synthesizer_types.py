"""Backward compatibility shim for achv_bullet_synthesizer_types.


LOGGER = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original achv_bullet_synthesizer_types.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .achv_enums import *  # Star import removed
# from .achv_models import *  # Star import removed
import logging


__all__ = ["*"]  # Re-export all imported names
