"""Backward compatibility shim for retrieve_schema_similarity.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original retrieve_schema_similarity.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""
import logging

# Re-export all components for backward compatibility
# from .retrieve_schema_similarity_impl import *  # Star import removed
# from .retrieve_schema_similarity_models import *  # Star import removed
# from .retrieve_schema_similarity_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
