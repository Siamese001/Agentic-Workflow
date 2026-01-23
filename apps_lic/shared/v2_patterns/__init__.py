"""
V2 Architecture Patterns for apps_lic.
Provides hardened state management, tracing, and persistence.
"""
from .immutable_buffer import ImmutableStagingBuffer
from .trace_registry import TraceRegistry
from .manifest_manager import ManifestManager

__all__ = ["ImmutableStagingBuffer", "TraceRegistry", "ManifestManager"]
