"""
V2 Architecture Patterns for apps_lic.
Provides hardened state management, tracing, and persistence.
"""

from .immutable_buffer import ImmutableStagingBuffer
from .manifest_manager import ManifestManager
from .trace_registry import TraceRegistry

__all__ = ["ImmutableStagingBuffer", "TraceRegistry", "ManifestManager"]
