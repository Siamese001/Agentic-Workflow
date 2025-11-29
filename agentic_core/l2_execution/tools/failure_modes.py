"""
L2 Tool Failure Modes

Defines failure mode handling for L2 execution tools.
"""

from enum import Enum
from typing import Dict, Any, Optional

class FailureMode(Enum):
    """Failure mode types for L2 tools."""
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMITED = "rate_limited"
    UNKNOWN_ERROR = "unknown_error"

class ToolFailureHandler:
    """Handles failure modes for L2 tools."""
    
    def __init__(self):
        self.failure_modes = list(FailureMode)
        self.failure_handlers = {
            FailureMode.TIMEOUT: self._handle_timeout,
            FailureMode.NETWORK_ERROR: self._handle_network_error,
            FailureMode.VALIDATION_ERROR: self._handle_validation_error,
            FailureMode.RESOURCE_EXHAUSTED: self._handle_resource_exhausted,
            FailureMode.PERMISSION_DENIED: self._handle_permission_denied,
            FailureMode.RATE_LIMITED: self._handle_rate_limited,
            FailureMode.UNKNOWN_ERROR: self._handle_unknown_error
        }
    
    def handle_failure(self, failure_mode: FailureMode, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a specific failure mode."""
        handler = self.failure_handlers.get(failure_mode, self._handle_unknown_error)
        return handler(context)
    
    def _handle_timeout(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeout failures."""
        return {
            "failure_type": "timeout",
            "retryable": True,
            "message": "Operation timed out",
            "context": context
        }
    
    def _handle_network_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle network error failures."""
        return {
            "failure_type": "network_error",
            "retryable": True,
            "message": "Network connectivity issue",
            "context": context
        }
    
    def _handle_validation_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation error failures."""
        return {
            "failure_type": "validation_error",
            "retryable": False,
            "message": "Input validation failed",
            "context": context
        }
    
    def _handle_resource_exhausted(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource exhaustion failures."""
        return {
            "failure_type": "resource_exhausted",
            "retryable": True,
            "message": "System resources exhausted",
            "context": context
        }
    
    def _handle_permission_denied(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle permission denied failures."""
        return {
            "failure_type": "permission_denied",
            "retryable": False,
            "message": "Permission denied",
            "context": context
        }
    
    def _handle_rate_limited(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rate limiting failures."""
        return {
            "failure_type": "rate_limited",
            "retryable": True,
            "message": "Rate limit exceeded",
            "context": context
        }
    
    def _handle_unknown_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown error failures."""
        return {
            "failure_type": "unknown_error",
            "retryable": False,
            "message": "Unknown error occurred",
            "context": context
        }

__all__ = ['FailureMode', 'ToolFailureHandler']
