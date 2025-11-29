"""
Shared invalidation tools for resume and outreach engines.

Generic invalidation capabilities for temporal data management
across engines without violating separation of concerns.
"""

from .invalidation_executor import InvalidationExecutor

__all__ = ["InvalidationExecutor"]
