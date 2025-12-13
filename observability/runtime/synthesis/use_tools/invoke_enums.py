"""Enum types for tool_invoke_observability_tool."""

from enum import Enum

class ToolCategory(Enum):
    """Categories of observability tools."""
    TRACING = 'tracing'
    METRICS = 'metrics'
    LOGGING = 'logging'
    MONITORING = 'monitoring'
    ANALYSIS = 'analysis'

class ToolProtocol(Enum):
    """Protocols supported by tools."""
    HTTP = 'http'
    GRPC = 'grpc'
    WEBSOCKET = 'websocket'
    NATIVE = 'native'

