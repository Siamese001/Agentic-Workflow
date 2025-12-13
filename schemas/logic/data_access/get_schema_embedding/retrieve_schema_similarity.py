"""Backward compatibility shim for retrieve_schema_similarity.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original retrieve_schema_similarity.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .retrieve_schema_similarity_enums import *
from .retrieve_schema_similarity_models import *
from .retrieve_schema_similarity_impl import *

__all__ = ['*']  # Re-export all imported names
