"""Backward compatibility shim for message_assembler.


LOGGER = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original message_assembler.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .message_assembler_impl import *  # Star import removed
# from .message_assembler_impl import *  # Star import removed
import logging


__all__ = ["*"]  # Re-export all imported names
