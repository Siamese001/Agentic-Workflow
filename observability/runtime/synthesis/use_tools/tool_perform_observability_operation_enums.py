"""Enum types for tool_perform_observability_operation."""

from enum import Enum

class OperationMode(Enum):
    """Modes of operation execution."""
    SYNCHRONOUS = 'synchronous'
    ASYNCHRONOUS = 'asynchronous'
    STREAMING = 'streaming'
    BATCH = 'batch'

class OperationScope(Enum):
    """Scope of observability operations."""
    SYSTEM = 'system'
    SERVICE = 'service'
    COMPONENT = 'component'
    REQUEST = 'request'
    CUSTOM = 'custom'
