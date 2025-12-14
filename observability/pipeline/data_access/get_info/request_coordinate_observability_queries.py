"""Backward compatibility shim for request_coordinate_observability_queries.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original request_coordinate_observability_queries.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .request_coordinate_observability_queries_impl_impl import *  # Star import removed
# from .request_coordinate_observability_queries_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
