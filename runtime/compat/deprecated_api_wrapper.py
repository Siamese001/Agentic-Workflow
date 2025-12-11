"""Deprecated API Wrapper - Shim for external API calls with deprecated function names.

This module provides shims and wrappers for external API calls that used
deprecated function names, ensuring backward compatibility.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime
from enum import Enum
import warnings

logger = logging.getLogger(__name__)


class DeprecationLevel(Enum):
    """Levels of deprecation."""
    WARNING = "warning"
    ERROR = "error"
    SILENT = "silent"


@dataclass
class DeprecatedFunction:
    """Definition of a deprecated function."""
    old_name: str
    new_name: str
    deprecation_version: str
    removal_version: Optional[str] = None
    alternative: Optional[str] = None
    migration_guide: Optional[str] = None


@dataclass
class APIWrapperConfig:
    """Configuration for API wrapper."""
    deprecation_level: DeprecationLevel = DeprecationLevel.WARNING
    log_deprecations: bool = True
    raise_on_error: bool = False
    include_stack_trace: bool = False


class DeprecatedAPIWrapper:
    """Wrapper for deprecated API functions."""
    
    def __init__(self, config: Optional[APIWrapperConfig] = None):
        self.config = config or APIWrapperConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._deprecated_functions: Dict[str, DeprecatedFunction] = {}
        self._function_mappings: Dict[str, Callable] = {}
        self._initialize_deprecated_functions()
    
    def register_deprecated_function(self, old_name: str, new_name: str,
                                   new_function: Callable, **kwargs) -> None:
        """Register a deprecated function mapping.
        
        Args:
            old_name: Deprecated function name
            new_name: New function name
            new_function: New function implementation
            **kwargs: Additional deprecation info
        """
        deprecated_func = DeprecatedFunction(
            old_name=old_name,
            new_name=new_name,
            **kwargs
        )
        
        self._deprecated_functions[old_name] = deprecated_func
        self._function_mappings[old_name] = new_function
        
        self.logger.info(f"Registered deprecated function: {old_name} -> {new_name}")
    
    def wrap_function_call(self, function_name: str, *args, **kwargs) -> Any:
        """Wrap a function call with deprecation handling.
        
        Args:
            function_name: Name of function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result
        """
        # Check if function is deprecated
        if function_name in self._deprecated_functions:
            self._handle_deprecation(function_name)
            
            # Get new function
            new_function = self._function_mappings.get(function_name)
            if new_function:
                return new_function(*args, **kwargs)
        
        # Function not found or not mapped
        raise AttributeError(f"Function '{function_name}' not found")
    
    def get_deprecation_info(self, function_name: str) -> Optional[DeprecatedFunction]:
        """Get deprecation information for a function.
        
        Args:
            function_name: Function name
            
        Returns:
            Optional[DeprecatedFunction]: Deprecation info
        """
        return self._deprecated_functions.get(function_name)
    
    def list_deprecated_functions(self) -> List[DeprecatedFunction]:
        """List all deprecated functions.
        
        Returns:
            List[DeprecatedFunction]: Deprecated functions
        """
        return list(self._deprecated_functions.values())
    
    def _handle_deprecation(self, function_name: str) -> None:
        """Handle deprecation for a function call.
        
        Args:
            function_name: Deprecated function name
        """
        deprecated_func = self._deprecated_functions[function_name]
        
        # Create deprecation message
        message = f"Function '{function_name}' is deprecated"
        
        if deprecated_func.new_name:
            message += f". Use '{deprecated_func.new_name}' instead"
        
        if deprecated_func.alternative:
            message += f". Alternative: {deprecated_func.alternative}"
        
        if deprecated_func.removal_version:
            message += f". Will be removed in version {deprecated_func.removal_version}"
        
        # Handle based on deprecation level
        if self.config.deprecation_level == DeprecationLevel.WARNING:
            if self.config.log_deprecations:
                self.logger.warning(message)
            warnings.warn(message, DeprecationWarning, stacklevel=2)
        
        elif self.config.deprecation_level == DeprecationLevel.ERROR:
            if self.config.raise_on_error:
                raise DeprecationError(message)
            else:
                self.logger.error(message)
        
        elif self.config.deprecation_level == DeprecationLevel.SILENT:
            if self.config.log_deprecations:
                self.logger.debug(message)
    
    def _initialize_deprecated_functions(self) -> None:
        """Initialize common deprecated functions."""
        # Example deprecated functions
        
        def new_process_data(data: Any, options: Optional[Dict] = None) -> Any:
            """New implementation of process_data."""
            return {"processed": True, "data": data, "options": options}
        
        def new_execute_query(query: str, params: Optional[Dict] = None) -> List[Dict]:
            """New implementation of execute_query."""
            return [{"query": query, "params": params, "results": []}]
        
        def new_validate_input(input_data: Any, schema: Optional[Dict] = None) -> bool:
            """New implementation of validate_input."""
            return True
        
        def new_connect_to_service(service_url: str, **kwargs) -> Dict[str, Any]:
            """New implementation of connect_to_service."""
            return {"connected": True, "url": service_url}
        
        def new_parse_config(config_path: str) -> Dict[str, Any]:
            """New implementation of parse_config."""
            return {"config": {}, "path": config_path}
        
        # Register deprecated functions
        self.register_deprecated_function(
            "process_data",
            "process_data_v2",
            new_process_data,
            deprecation_version="1.0",
            removal_version="2.0",
            alternative="Use the new process_data_v2 function with enhanced options"
        )
        
        self.register_deprecated_function(
            "execute_query",
            "execute_query_v2",
            new_execute_query,
            deprecation_version="1.0",
            removal_version="2.0"
        )
        
        self.register_deprecated_function(
            "validate_input",
            "validate_input_v2",
            new_validate_input,
            deprecation_version="1.0"
        )
        
        self.register_deprecated_function(
            "connect_to_service",
            "connect_to_service_v2",
            new_connect_to_service,
            deprecation_version="1.0",
            alternative="Use the ServiceClient class instead"
        )
        
        self.register_deprecated_function(
            "parse_config",
            "load_config",
            new_parse_config,
            deprecation_version="1.0",
            migration_guide="See migration guide chapter 3"
        )


class DeprecationError(DeprecationWarning):
    """Error raised for deprecated function calls in error mode."""
    pass


# Global wrapper instance
_global_wrapper = DeprecatedAPIWrapper()


def __getattr__(name: str) -> Callable:
    """Get attribute for deprecated functions.
    
    Args:
        name: Attribute name
        
    Returns:
        Callable: Wrapped function
    """
    if name in _global_wrapper._function_mappings:
        def wrapped_function(*args, **kwargs):
            return _global_wrapper.wrap_function_call(name, *args, **kwargs)
        return wrapped_function
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Factory function for easy instantiation
def create_deprecated_api_wrapper(
    deprecation_level: str = "warning",
    log_deprecations: bool = True,
    **kwargs
) -> DeprecatedAPIWrapper:
    """Create a configured deprecated API wrapper."""
    config = APIWrapperConfig(
        deprecation_level=DeprecationLevel(deprecation_level),
        log_deprecations=log_deprecations,
        **kwargs
    )
    return DeprecatedAPIWrapper(config)


# Convenience function for direct usage
def call_deprecated_function(function_name: str, *args, **kwargs) -> Any:
    """Call a deprecated function with proper handling.
    
    Args:
        function_name: Deprecated function name
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Any: Function result
    """
    return _global_wrapper.wrap_function_call(function_name, *args, **kwargs)


# Convenience functions for common deprecated APIs
def process_data(data: Any, options: Optional[Dict] = None) -> Any:
    """Deprecated: Use process_data_v2 instead."""
    return call_deprecated_function("process_data", data, options)


def execute_query(query: str, params: Optional[Dict] = None) -> List[Dict]:
    """Deprecated: Use execute_query_v2 instead."""
    return call_deprecated_function("execute_query", query, params)


def validate_input(input_data: Any, schema: Optional[Dict] = None) -> bool:
    """Deprecated: Use validate_input_v2 instead."""
    return call_deprecated_function("validate_input", input_data, schema)


def connect_to_service(service_url: str, **kwargs) -> Dict[str, Any]:
    """Deprecated: Use connect_to_service_v2 or ServiceClient instead."""
    return call_deprecated_function("connect_to_service", service_url, **kwargs)


def parse_config(config_path: str) -> Dict[str, Any]:
    """Deprecated: Use load_config instead."""
    return call_deprecated_function("parse_config", config_path)
