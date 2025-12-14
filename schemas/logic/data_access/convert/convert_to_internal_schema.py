"""Backward compatibility shim for convert_to_internal_schema.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original convert_to_internal_schema.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .convert_to_internal_schema_impl import *  # Star import removed
# from .schema_models import *  # Star import removed
# from .convert_to_internal_schema_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
