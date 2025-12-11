"""Deprecated Utils Mapper - Maps calls to removed utility functions.

This module provides mapping from calls to removed utility functions to the new,
canonical utility classes, ensuring backward compatibility.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime
from enum import Enum
import warnings

logger = logging.getLogger(__name__)


class UtilityCategory(Enum):
    """Categories of utility functions."""
    STRING = "string"
    DATE = "date"
    MATH = "math"
    COLLECTION = "collection"
    VALIDATION = "validation"
    ENCODING = "encoding"
    FILE = "file"
    NETWORK = "network"
    CUSTOM = "custom"


@dataclass
class UtilityMapping:
    """Mapping from old utility to new utility."""
    old_module: str
    old_function: str
    new_module: str
    new_class: Optional[str]
    new_function: str
    category: UtilityCategory
    deprecation_version: str
    migration_notes: Optional[str] = None


@dataclass
class MapperConfig:
    """Configuration for utility mapper."""
    warn_on_deprecated: bool = True
    log_mappings: bool = True
    cache_mappings: bool = True
    auto_import: bool = True


class DeprecatedUtilsMapper:
    """Mapper for deprecated utility functions."""
    
    def __init__(self, config: Optional[MapperConfig] = None):
        self.config = config or MapperConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._mappings: Dict[str, UtilityMapping] = {}
        self._function_cache: Dict[str, Callable] = {}
        self._initialize_mappings()
    
    def map_function(self, old_module: str, old_function: str, 
                    *args, **kwargs) -> Any:
        """Map and execute a deprecated utility function.
        
        Args:
            old_module: Old module name
            old_function: Old function name
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result
        """
        key = f"{old_module}.{old_function}"
        
        # Get mapping
        mapping = self._mappings.get(key)
        if not mapping:
            raise AttributeError(f"No mapping found for {key}")
        
        # Log mapping if enabled
        if self.config.log_mappings:
            self.logger.info(f"Mapping deprecated function: {key} -> {mapping.new_module}.{mapping.new_function}")
        
        # Warn if enabled
        if self.config.warn_on_deprecated:
            warnings.warn(
                f"{key} is deprecated since version {mapping.deprecation_version}. "
                f"Use {mapping.new_module}.{mapping.new_function} instead.",
                DeprecationWarning,
                stacklevel=2
            )
        
        # Get new function
        new_function = self._get_new_function(mapping)
        
        # Execute new function
        return new_function(*args, **kwargs)
    
    def get_mapping(self, old_module: str, old_function: str) -> Optional[UtilityMapping]:
        """Get mapping for deprecated function.
        
        Args:
            old_module: Old module name
            old_function: Old function name
            
        Returns:
            Optional[UtilityMapping]: Function mapping
        """
        key = f"{old_module}.{old_function}"
        return self._mappings.get(key)
    
    def list_mappings(self, category: Optional[UtilityCategory] = None) -> List[UtilityMapping]:
        """List all mappings.
        
        Args:
            category: Optional filter by category
            
        Returns:
            List[UtilityMapping]: Function mappings
        """
        mappings = list(self._mappings.values())
        
        if category:
            mappings = [m for m in mappings if m.category == category]
        
        return mappings
    
    def add_mapping(self, mapping: UtilityMapping) -> None:
        """Add a new utility mapping.
        
        Args:
            mapping: Utility mapping to add
        """
        key = f"{mapping.old_module}.{mapping.old_function}"
        self._mappings[key] = mapping
        
        # Clear cache if enabled
        if self.config.cache_mappings:
            self._function_cache.clear()
        
        self.logger.info(f"Added mapping: {key}")
    
    def _get_new_function(self, mapping: UtilityMapping) -> Callable:
        """Get the new function implementation.
        
        Args:
            mapping: Utility mapping
            
        Returns:
            Callable: New function
        """
        key = f"{mapping.old_module}.{mapping.old_function}"
        
        # Check cache
        if self.config.cache_mappings and key in self._function_cache:
            return self._function_cache[key]
        
        # Import and get function
        if self.config.auto_import:
            try:
                # Import module
                module = __import__(mapping.new_module, fromlist=[mapping.new_class or mapping.new_function])
                
                # Get class or function
                if mapping.new_class:
                    new_class = getattr(module, mapping.new_class)
                    new_function = getattr(new_class, mapping.new_function)
                else:
                    new_function = getattr(module, mapping.new_function)
                
                # Cache if enabled
                if self.config.cache_mappings:
                    self._function_cache[key] = new_function
                
                return new_function
                
            except (ImportError, AttributeError) as e:
                self.logger.error(f"Failed to import {mapping.new_module}.{mapping.new_function}: {e}")
                raise
        
        # Return mock function if auto-import disabled
        return self._create_mock_function(mapping)
    
    def _create_mock_function(self, mapping: UtilityMapping) -> Callable:
        """Create a mock function for mapping.
        
        Args:
            mapping: Utility mapping
            
        Returns:
            Callable: Mock function
        """
        def mock_function(*args, **kwargs):
            self.logger.warning(f"Mock function called for {mapping.old_module}.{mapping.old_function}")
            return {"mock": True, "original_args": args, "original_kwargs": kwargs}
        
        return mock_function
    
    def _initialize_mappings(self) -> None:
        """Initialize common utility mappings."""
        
        # String utilities
        self.add_mapping(UtilityMapping(
            old_module="old_string_util",
            old_function="camel_to_snake",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="camel_to_snake",
            category=UtilityCategory.STRING,
            deprecation_version="1.0",
            migration_notes="Use TextUtils.camel_to_snake() instead"
        ))
        
        self.add_mapping(UtilityMapping(
            old_module="old_string_util",
            old_function="snake_to_camel",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="snake_to_camel",
            category=UtilityCategory.STRING,
            deprecation_version="1.0"
        ))
        
        self.add_mapping(UtilityMapping(
            old_module="old_string_util",
            old_function="truncate_text",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="truncate",
            category=UtilityCategory.STRING,
            deprecation_version="1.0"
        ))
        
        # Date utilities
        self.add_mapping(UtilityMapping(
            old_module="old_date_util",
            old_function="parse_iso_date",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="parse_iso_datetime",
            category=UtilityCategory.DATE,
            deprecation_version="1.0"
        ))
        
        self.add_mapping(UtilityMapping(
            old_module="old_date_util",
            old_function="format_duration",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="format_duration",
            category=UtilityCategory.DATE,
            deprecation_version="1.0"
        ))
        
        # Math utilities
        self.add_mapping(UtilityMapping(
            old_module="old_math_util",
            old_function="clamp",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="clamp_value",
            category=UtilityCategory.MATH,
            deprecation_version="1.0"
        ))
        
        self.add_mapping(UtilityMapping(
            old_module="old_math_util",
            old_function="lerp",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="lerp",
            category=UtilityCategory.MATH,
            deprecation_version="1.0"
        ))
        
        # Collection utilities
        self.add_mapping(UtilityMapping(
            old_module="old_collection_util",
            old_function="flatten_list",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="flatten",
            category=UtilityCategory.COLLECTION,
            deprecation_version="1.0"
        ))
        
        self.add_mapping(UtilityMapping(
            old_module="old_collection_util",
            old_function="chunk_list",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="chunk",
            category=UtilityCategory.COLLECTION,
            deprecation_version="1.0"
        ))
        
        # Validation utilities
        self.add_mapping(UtilityMapping(
            old_module="old_validation_util",
            old_function="is_email",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="is_valid_email",
            category=UtilityCategory.VALIDATION,
            deprecation_version="1.0"
        ))
        
        self.add_mapping(UtilityMapping(
            old_module="old_validation_util",
            old_function="is_url",
            new_module="agentic_workflow.runtime.shared",
            new_class="TextUtils",
            new_function="is_valid_url",
            category=UtilityCategory.VALIDATION,
            deprecation_version="1.0"
        ))


# Global mapper instance
_global_mapper = DeprecatedUtilsMapper()


def __getattr__(name: str) -> Callable:
    """Get attribute for deprecated utility modules.
    
    Args:
        name: Attribute name
        
    Returns:
        Callable: Wrapped function
    """
    # Check if it's a deprecated module
    if name.startswith("old_"):
        def module_wrapper(function_name: str):
            def function_wrapper(*args, **kwargs):
                return _global_mapper.map_function(name, function_name, *args, **kwargs)
            return function_wrapper
        
        return module_wrapper
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Factory function for easy instantiation
def create_deprecated_utils_mapper(
    warn_on_deprecated: bool = True,
    log_mappings: bool = True,
    **kwargs
) -> DeprecatedUtilsMapper:
    """Create a configured deprecated utils mapper."""
    config = MapperConfig(
        warn_on_deprecated=warn_on_deprecated,
        log_mappings=log_mappings,
        **kwargs
    )
    return DeprecatedUtilsMapper(config)


# Convenience functions for common deprecated utilities

# Old string util functions
def camel_to_snake(text: str) -> str:
    """Deprecated: Use TextUtils.camel_to_snake instead."""
    return _global_mapper.map_function("old_string_util", "camel_to_snake", text)


def snake_to_camel(text: str) -> str:
    """Deprecated: Use TextUtils.snake_to_camel instead."""
    return _global_mapper.map_function("old_string_util", "snake_to_camel", text)


def truncate_text(text: str, max_length: int) -> str:
    """Deprecated: Use TextUtils.truncate instead."""
    return _global_mapper.map_function("old_string_util", "truncate_text", text, max_length)


# Old date util functions
def parse_iso_date(date_string: str) -> datetime:
    """Deprecated: Use TextUtils.parse_iso_datetime instead."""
    return _global_mapper.map_function("old_date_util", "parse_iso_date", date_string)


def format_duration(seconds: float) -> str:
    """Deprecated: Use TextUtils.format_duration instead."""
    return _global_mapper.map_function("old_date_util", "format_duration", seconds)


# Old math util functions
def clamp(value: float, min_val: float, max_val: float) -> float:
    """Deprecated: Use TextUtils.clamp_value instead."""
    return _global_mapper.map_function("old_math_util", "clamp", value, min_val, max_val)


def lerp(start: float, end: float, t: float) -> float:
    """Deprecated: Use TextUtils.lerp instead."""
    return _global_mapper.map_function("old_math_util", "lerp", start, end, t)


# Old collection util functions
def flatten_list(nested_list: List[Any]) -> List[Any]:
    """Deprecated: Use TextUtils.flatten instead."""
    return _global_mapper.map_function("old_collection_util", "flatten_list", nested_list)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Deprecated: Use TextUtils.chunk instead."""
    return _global_mapper.map_function("old_collection_util", "chunk_list", lst, chunk_size)


# Old validation util functions
def is_email(email: str) -> bool:
    """Deprecated: Use TextUtils.is_valid_email instead."""
    return _global_mapper.map_function("old_validation_util", "is_email", email)


def is_url(url: str) -> bool:
    """Deprecated: Use TextUtils.is_valid_url instead."""
    return _global_mapper.map_function("old_validation_util", "is_url", url)
