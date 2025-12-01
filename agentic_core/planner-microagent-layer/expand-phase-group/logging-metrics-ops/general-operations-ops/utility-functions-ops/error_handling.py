"""
Error Handling Engine Implementation
"""

from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
import traceback


@dataclass
class ErrorInfo:
    """Information about an error that occurred"""
    error_type: str
    error_message: str
    stack_trace: str
    context: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ErrorHandling:
    """Engine for handling and managing errors during tool execution"""

    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self.error_handlers: Dict[str, Callable] = {}
        self.retry_config = {"max_retries": 3, "base_delay": 1.0}

    def add_error_handler(self, error_type: str, handler_func: Callable):
        """Add a custom error handler for specific error types"""
        self.error_handlers[error_type] = handler_func

    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle an error and return error information"""
        if context is None:
            context = {}

        error_info = ErrorInfo(
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            context=context
        )

        self.error_history.append(error_info)

        # Apply custom error handler if available
        error_type = type(error).__name__
        if error_type in self.error_handlers:
            try:
                handler_result = self.error_handlers[error_type](error, context)
                return {
                    "handled": True,
                    "error_info": error_info,
                    "handler_result": handler_result
                }
            except Exception as handler_error:
                return {
                    "handled": False,
                    "error_info": error_info,
                    "handler_error": str(handler_error)
                }

        # Default error handling
        return {
            "handled": False,
            "error_info": error_info,
            "suggestion": self._get_default_suggestion(error_type)
        }

    def _get_default_suggestion(self, error_type: str) -> str:
        """Get default suggestion for common error types"""
        suggestions = {
            "ValueError": "Check if input values are within expected ranges",
            "TypeError": "Verify that input types match expected types",
            "KeyError": "Ensure all required keys are present in input data",
            "AttributeError": "Check if objects have the expected attributes",
            "ImportError": "Verify that all required modules are installed",
            "FileNotFoundError": "Check if file paths are correct and files exist"
        }
        return suggestions.get(error_type, "Review the error details and context")

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute a function with retry logic"""
        last_error = None

        for attempt in range(self.retry_config["max_retries"]):
            try:
                result = func(*args, **kwargs)
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt + 1
                }
            except Exception as error:
                last_error = error
                if attempt < self.retry_config["max_retries"] - 1:
                    # Simple exponential backoff
                    delay = self.retry_config["base_delay"] * (2 ** attempt)
                    import time
                    time.sleep(delay)

        # All retries failed
        error_result = self.handle_error(last_error, {"attempts": self.retry_config["max_retries"]})
        return {
            "success": False,
            "error": error_result,
            "attempts": self.retry_config["max_retries"]
        }

    def get_error_history(self) -> List[ErrorInfo]:
        """Get history of errors"""
        return self.error_history.copy()

    def clear_history(self):
        """Clear error history"""
        self.error_history.clear()

    def configure_retry(self, max_retries: int, base_delay: float):
        """Configure retry settings"""
        self.retry_config = {"max_retries": max_retries, "base_delay": base_delay}
