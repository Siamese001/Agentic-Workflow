"""Logger Version Shim - Ensures old logging calls redirect to new structured logging.

This module provides a shim that redirects old logging calls to the new
structured logging system, maintaining backward compatibility.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime
from enum import Enum
import sys

logger = logging.getLogger(__name__)


class LegacyLogLevel(Enum):
    """Legacy log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class StructuredLogLevel(Enum):
    """New structured log levels."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


@dataclass
class LogEntry:
    """Structured log entry."""
    level: StructuredLogLevel
    message: str
    timestamp: datetime
    logger_name: str
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class ShimConfig:
    """Configuration for logger shim."""
    preserve_format: bool = True
    add_context: bool = True
    convert_levels: bool = True
    capture_stack: bool = False


class LegacyLogger:
    """Legacy logger interface."""
    
    def __init__(self, name: str, shim: 'LoggerVersionShim'):
        self.name = name
        self.shim = shim
        self._handlers = []
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self.shim.log(self.name, LegacyLogLevel.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self.shim.log(self.name, LegacyLogLevel.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self.shim.log(self.name, LegacyLogLevel.WARNING, message, *args, **kwargs)
    
    def warn(self, message: str, *args, **kwargs) -> None:
        """Log warning message (alias)."""
        self.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self.shim.log(self.name, LegacyLogLevel.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self.shim.log(self.name, LegacyLogLevel.CRITICAL, message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        kwargs["exc_info"] = True
        self.error(message, *args, **kwargs)
    
    def log(self, level: int, message: str, *args, **kwargs) -> None:
        """Log at specific level."""
        # Map numeric level to enum
        level_mapping = {
            logging.DEBUG: LegacyLogLevel.DEBUG,
            logging.INFO: LegacyLogLevel.INFO,
            logging.WARNING: LegacyLogLevel.WARNING,
            logging.ERROR: LegacyLogLevel.ERROR,
            logging.CRITICAL: LegacyLogLevel.CRITICAL
        }
        
        legacy_level = level_mapping.get(level, LegacyLogLevel.INFO)
        self.shim.log(self.name, legacy_level, message, *args, **kwargs)
    
    def addHandler(self, handler) -> None:
        """Add handler (for compatibility)."""
        self._handlers.append(handler)
    
    def removeHandler(self, handler) -> None:
        """Remove handler (for compatibility)."""
        if handler in self._handlers:
            self._handlers.remove(handler)


class LoggerVersionShim:
    """Shim for redirecting legacy logging to structured logging."""
    
    def __init__(self, config: Optional[ShimConfig] = None):
        self.config = config or ShimConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._legacy_loggers: Dict[str, LegacyLogger] = {}
        self._structured_handler = None
        self._initialize_shim()
    
    def get_logger(self, name: str) -> LegacyLogger:
        """Get legacy logger shim.
        
        Args:
            name: Logger name
            
        Returns:
            LegacyLogger: Shim logger
        """
        if name not in self._legacy_loggers:
            self._legacy_loggers[name] = LegacyLogger(name, self)
        
        return self._legacy_loggers[name]
    
    def log(self, logger_name: str, level: LegacyLogLevel,
            message: str, *args, **kwargs) -> None:
        """Log message using structured logger.
        
        Args:
            logger_name: Logger name
            level: Legacy log level
            message: Log message
            *args: Message arguments
            **kwargs: Additional logging context
        """
        # Format message if args provided
        if args:
            try:
                formatted_message = message % args
            except (TypeError, ValueError):
                formatted_message = message + " " + str(args)
        else:
            formatted_message = message
        
        # Convert level
        if self.config.convert_levels:
            structured_level = self._convert_log_level(level)
        else:
            structured_level = StructuredLogLevel(level.value)
        
        # Create log entry
        log_entry = LogEntry(
            level=structured_level,
            message=formatted_message,
            timestamp=datetime.utcnow(),
            logger_name=logger_name
        )
        
        # Add context if enabled
        if self.config.add_context:
            log_entry.context.update(self._extract_context(kwargs))
        
        # Add stack info if enabled
        if self.config.capture_stack:
            log_entry.context["stack_info"] = self._get_stack_info()
        
        # Send to structured logger
        self._send_to_structured_logger(log_entry)
    
    def configure_structured_handler(self, handler: Callable) -> None:
        """Configure the structured logging handler.
        
        Args:
            handler: Structured logging handler
        """
        self._structured_handler = handler
        self.logger.info("Configured structured logging handler")
    
    def _initialize_shim(self) -> None:
        """Initialize the logging shim."""
        # Replace standard logging module's getLogger
        original_getLogger = logging.getLogger
        
        def shim_getLogger(name=None):
            if name is None:
                name = root_logger.name if root_logger else "root"
            return self.get_logger(name)
        
        # Monkey patch for backward compatibility
        logging.getLogger = shim_getLogger
        
        # Keep reference to original
        self._original_getLogger = original_getLogger
        
        self.logger.info("Initialized logging version shim")
    
    def _convert_log_level(self, legacy_level: LegacyLogLevel) -> StructuredLogLevel:
        """Convert legacy log level to structured level.
        
        Args:
            legacy_level: Legacy log level
            
        Returns:
            StructuredLogLevel: Structured log level
        """
        level_mapping = {
            LegacyLogLevel.DEBUG: StructuredLogLevel.DEBUG,
            LegacyLogLevel.INFO: StructuredLogLevel.INFO,
            LegacyLogLevel.WARNING: StructuredLogLevel.WARN,
            LegacyLogLevel.ERROR: StructuredLogLevel.ERROR,
            LegacyLogLevel.CRITICAL: StructuredLogLevel.FATAL
        }
        
        return level_mapping.get(legacy_level, StructuredLogLevel.INFO)
    
    def _extract_context(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context from logging kwargs.
        
        Args:
            kwargs: Logging keyword arguments
            
        Returns:
            Dict: Extracted context
        """
        context = {}
        
        # Extract common logging kwargs
        for key in ["exc_info", "stack_info", "extra"]:
            if key in kwargs:
                context[key] = kwargs[key]
        
        # Extract user-defined context
        if "extra" in kwargs and isinstance(kwargs["extra"], dict):
            for key, value in kwargs["extra"].items():
                if key not in context:
                    context[key] = value
        
        return context
    
    def _get_stack_info(self) -> Optional[Dict[str, Any]]:
        """Get stack information.
        
        Returns:
            Optional[Dict]: Stack information
        """
        import traceback
        
        try:
            stack = traceback.extract_stack()
            # Filter out shim-related frames
            filtered_stack = [frame for frame in stack if "shim" not in frame.filename]
            
            if filtered_stack:
                last_frame = filtered_stack[-2] if len(filtered_stack) > 1 else filtered_stack[-1]
                return {
                    "filename": last_frame.filename,
                    "line_number": last_frame.lineno,
                    "function": last_frame.name,
                    "line": last_frame.line
                }
        except Exception:
            pass
        
        return None
    
    def _send_to_structured_logger(self, log_entry: LogEntry) -> None:
        """Send log entry to structured logger.
        
        Args:
            log_entry: Log entry to send
        """
        if self._structured_handler:
            try:
                self._structured_handler(log_entry)
            except Exception as e:
                # Fallback to standard logging
                self.logger.error(f"Failed to send to structured logger: {e}")
                self._fallback_logging(log_entry)
        else:
            # Fallback to standard logging
            self._fallback_logging(log_entry)
    
    def _fallback_logging(self, log_entry: LogEntry) -> None:
        """Fallback to standard Python logging.
        
        Args:
            log_entry: Log entry to log
        """
        # Get standard logger
        std_logger = self._original_getLogger(log_entry.logger_name)
        
        # Map to standard levels
        level_mapping = {
            StructuredLogLevel.TRACE: logging.DEBUG,
            StructuredLogLevel.DEBUG: logging.DEBUG,
            StructuredLogLevel.INFO: logging.INFO,
            StructuredLogLevel.WARN: logging.WARNING,
            StructuredLogLevel.ERROR: logging.ERROR,
            StructuredLogLevel.FATAL: logging.CRITICAL
        }
        
        std_level = level_mapping.get(log_entry.level, logging.INFO)
        
        # Log with context
        if log_entry.context:
            std_logger.log(std_level, log_entry.message, extra=log_entry.context)
        else:
            std_logger.log(std_level, log_entry.message)


# Global shim instance
_global_shim = LoggerVersionShim()


def configure_logging_shim(
    preserve_format: bool = True,
    add_context: bool = True,
    **kwargs
) -> LoggerVersionShim:
    """Configure the global logging shim.
    
    Args:
        preserve_format: Whether to preserve message formatting
        add_context: Whether to add context information
        **kwargs: Additional configuration
        
    Returns:
        LoggerVersionShim: Configured shim
    """
    config = ShimConfig(
        preserve_format=preserve_format,
        add_context=add_context,
        **kwargs
    )
    
    global _global_shim
    _global_shim = LoggerVersionShim(config)
    
    return _global_shim


def get_legacy_logger(name: str) -> LegacyLogger:
    """Get legacy logger shim.
    
    Args:
        name: Logger name
        
    Returns:
        LegacyLogger: Shim logger
    """
    return _global_shim.get_logger(name)


# Convenience function for structured logging handler
def set_structured_logging_handler(handler: Callable) -> None:
    """Set the structured logging handler.
    
    Args:
        handler: Structured logging handler function
    """
    _global_shim.configure_structured_handler(handler)
