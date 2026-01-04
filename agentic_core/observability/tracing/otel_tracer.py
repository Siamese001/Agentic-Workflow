"""
OpenTelemetry Distributed Tracing Module

Provides distributed tracing with span context propagation across agent chains.
Enables end-to-end visibility of healing, orchestration, and execution flows.
"""

from __future__ import annotations
from typing import Any, Callable, Optional
from functools import wraps
import logging


class SimpleSpan:
    """Simplified span implementation for tracing."""
    
    def __init__(self, name: str, parent: Optional[SimpleSpan] = None):
        """Initialize span."""
        self.name = name
        self.parent = parent
        self.attributes = {}
        self.status = 'unset'
        self.exception = None
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set span attribute."""
        self.attributes[key] = value
    
    def record_exception(self, exc: Exception) -> None:
        """Record exception in span."""
        self.exception = exc
        self.status = 'error'
    
    def __enter__(self):
        """Enter span context."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit span context."""
        if exc_type is not None:
            self.record_exception(exc_val)
        return False


class SimpleTracer:
    """Simplified tracer for distributed tracing."""
    
    def __init__(self, name: str = 'sovereign'):
        """Initialize tracer."""
        self.name = name
        self.logger = logging.getLogger(f'{name}.tracer')
        self.current_span: Optional[SimpleSpan] = None
    
    def start_as_current_span(self, operation_name: str) -> SimpleSpan:
        """Start new span as current."""
        span = SimpleSpan(operation_name, parent=self.current_span)
        self.current_span = span
        self.logger.debug(f'Span started: {operation_name}')
        return span
    
    def get_current_span(self) -> Optional[SimpleSpan]:
        """Get current span."""
        return self.current_span


# Global tracer instance
tracer = SimpleTracer('sovereign')


def with_span(operation_name: str) -> Callable:
    """Decorator for tracing operations with spans."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with tracer.start_as_current_span(operation_name) as span:
                # Extract agent name from function qualname
                agent_name = func.__qualname__.split('.')[0] if '.' in func.__qualname__ else 'unknown'
                span.set_attribute('agent', agent_name)
                span.set_attribute('function', func.__name__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute('status', 'success')
                    return result
                except Exception as e:
                    span.set_attribute('status', 'error')
                    span.record_exception(e)
                    raise
        
        return wrapper
    return decorator
