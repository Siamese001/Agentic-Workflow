"""
L2 Tool Timeouts

Defines timeout handling for L2 execution tools.
"""

import time
from typing import Dict, Any, Optional, Callable
from threading import Thread
from concurrent.futures import TimeoutError as FutureTimeoutError

class ToolTimeout:
    """Handles timeout functionality for L2 tools."""
    
    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        self.timeout_handlers = {}
    
    def set_timeout(self, tool_name: str, timeout_seconds: int):
        """Set timeout for a specific tool."""
        self.timeout_handlers[tool_name] = timeout_seconds
    
    def execute_with_timeout(self, tool_name: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute a function with timeout protection."""
        timeout = self.timeout_handlers.get(tool_name, self.default_timeout)
        
        result = {"status": "running", "start_time": time.time()}
        
        try:
            # Execute function with timeout
            result_container = {}
            exception_container = {}
            
            def target():
                try:
                    result_container["value"] = func(*args, **kwargs)
                except Exception as e:
                    exception_container["exception"] = e
            
            thread = Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout)
            
            if thread.is_alive():
                result.update({
                    "status": "timeout",
                    "timeout_seconds": timeout,
                    "message": f"Tool {tool_name} timed out after {timeout} seconds"
                })
            else:
                if exception_container:
                    result.update({
                        "status": "error",
                        "error": str(exception_container["exception"])
                    })
                else:
                    result.update({
                        "status": "completed",
                        "result": result_container["value"],
                        "execution_time": time.time() - result["start_time"]
                    })
        
        except Exception as e:
            result.update({
                "status": "error",
                "error": str(e)
            })
        
        return result
    
    def get_timeout_config(self) -> Dict[str, int]:
        """Get timeout configuration for all tools."""
        return self.timeout_handlers.copy()

# Global timeout handler
timeout_handler = ToolTimeout()

__all__ = ['ToolTimeout', 'timeout_handler']
