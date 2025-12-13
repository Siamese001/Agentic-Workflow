"""Enum types for tool_execute_observability_execution."""


class ToolType(Enum):
    """Types of observability tools."""
    TRACER = 'tracer'
    METRIC_COLLECTOR = 'metric_collector'
    LOG_ANALYZER = 'log_analyzer'
    EVENT_PROCESSOR = 'event_processor'
    PROFILER = 'profiler'

class ExecutionMode(Enum):
    """Modes of tool execution."""
    SYNCHRONOUS = 'synchronous'
    ASYNCHRONOUS = 'asynchronous'
    STREAMING = 'streaming'
    BATCH = 'batch'
