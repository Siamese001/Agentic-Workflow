"""Backward compatibility shim for query_schema_store.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original query_schema_store.py contained 10 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .query_schema_store_impl import *  # Star import removed
# from .query_schema_store_models import *  # Star import removed
# from .query_schema_store_models_1 import *  # Star import removed
# from .query_schema_store_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
