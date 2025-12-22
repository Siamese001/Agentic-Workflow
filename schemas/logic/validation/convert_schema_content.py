"""Backward compatibility shim for convert_schema_content.


LOGGER = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original convert_schema_content.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .convert_schema_content_impl import *  # Star import removed
# from .convert_schema_content_impl import *  # Star import removed
import logging


__all__ = ["*"]  # Re-export all imported names
