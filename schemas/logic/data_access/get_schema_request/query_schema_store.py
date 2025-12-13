"""Backward compatibility shim for query_schema_store.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original query_schema_store.py contained 10 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .query_schema_store_impl import *
from .query_schema_store_models import *
from .query_schema_store_models_1 import *
from .query_schema_store_impl import *

__all__ = ['*']  # Re-export all imported names
