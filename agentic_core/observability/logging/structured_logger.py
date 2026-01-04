"""
Structured JSON Logging Module

Provides structured logging with trace ID correlation across agent chains.
Replaces scattered print() statements with queryable JSON logs.
"""

from __future__ import annotations
import json
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional
import logging


# Context variable for trace ID propagation
trace_id_var: ContextVar[str] = ContextVar('trace_id', default='')


class StructuredLogger:
    """Structured JSON logger with trace ID correlation."""
    
    def __init__(self, name: str = 'sovereign'):
        """Initialize structured logger."""
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove default handlers
        self.logger.handlers.clear()
        
        # Add JSON handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def _get_trace_id(self) -> str:
        """Get current trace ID or generate new one."""
        trace_id = trace_id_var.get()
        if not trace_id:
            trace_id = str(uuid.uuid4())
            trace_id_var.set(trace_id)
        return trace_id
    
    def _build_record(
        self,
        level: str,
        message: str,
        agent: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Build structured log record."""
        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'agent': agent,
            'trace_id': self._get_trace_id(),
            'message': message,
        }
        record.update(kwargs)
        return record
    
    def debug(self, message: str, agent: str, **kwargs):
        """Log debug message."""
        record = self._build_record('DEBUG', message, agent, **kwargs)
        self.logger.debug(json.dumps(record))
    
    def info(self, message: str, agent: str, **kwargs):
        """Log info message."""
        record = self._build_record('INFO', message, agent, **kwargs)
        self.logger.info(json.dumps(record))
    
    def warning(self, message: str, agent: str, **kwargs):
        """Log warning message."""
        record = self._build_record('WARNING', message, agent, **kwargs)
        self.logger.warning(json.dumps(record))
    
    def error(self, message: str, agent: str, **kwargs):
        """Log error message."""
        record = self._build_record('ERROR', message, agent, **kwargs)
        self.logger.error(json.dumps(record))
    
    def critical(self, message: str, agent: str, **kwargs):
        """Log critical message."""
        record = self._build_record('CRITICAL', message, agent, **kwargs)
        self.logger.critical(json.dumps(record))


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        return record.getMessage()


def get_structured_logger() -> StructuredLogger:
    """Get global structured logger instance."""
    return StructuredLogger('sovereign')


def set_trace_id(trace_id: str) -> None:
    """Set trace ID for current context."""
    trace_id_var.set(trace_id)


def get_trace_id() -> str:
    """Get current trace ID."""
    return trace_id_var.get()


def new_trace_context() -> str:
    """Create new trace context and return trace ID."""
    trace_id = str(uuid.uuid4())
    trace_id_var.set(trace_id)
    return trace_id


# Global logger instance
structured_log = get_structured_logger()
