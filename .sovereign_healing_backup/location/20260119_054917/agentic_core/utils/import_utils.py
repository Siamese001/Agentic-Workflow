"""
Import Utilities - Centralized Path/Module Conversion and Dynamic Importing

This module provides centralized utilities for converting file paths to
Python module paths and safely importing modules dynamically.

USAGE:
    from agentic_core.utils.import_utils import (
        path_to_module,
        module_to_path,
        safe_import_module,
        safe_import_class,
    )
    
    # Convert path to module
    module_path = path_to_module("agentic_core/L5_safety/validators/LocationAgent.py")
    # Returns: "agentic_core.L5_safety.validators.LocationAgent"
    
    # Safely import a module
    module = safe_import_module("agentic_core.utils.file_utils")
    
    # Safely import a class from a module
    cls = safe_import_class("agentic_core.utils.result_utils", "AgentResult")

SSOT PRINCIPLE:
    All path-to-module conversions should use this module instead of
    inline string replacements scattered across 45+ files.
"""
from __future__ import annotations
import importlib
import logging
import os
from pathlib import Path
from typing import Any, Optional, Type, Union

Logger = logging.getLogger(__name__)


def path_to_module(
    file_path: Union[str, Path],
    project_root: Optional[Path] = None
) -> str:
    """
    Convert a file path to a Python module path.
    
    Handles both Unix and Windows path separators and removes the .py extension.
    
    Args:
        file_path: Path to the Python file (absolute or relative)
        project_root: Optional project root to make path relative to
        
    Returns:
        Dot-notation module path
        
    Examples:
        >>> path_to_module("agentic_core/L5_safety/validators/LocationAgent.py")
        'agentic_core.L5_safety.validators.LocationAgent'
        
        >>> path_to_module("agentic_core\\L5_safety\\validators\\LocationAgent.py")
        'agentic_core.L5_safety.validators.LocationAgent'
        
        >>> path_to_module(Path("agentic_core/utils/file_utils.py"))
        'agentic_core.utils.file_utils'
    """
    # Convert to string if Path
    path_str = str(file_path)
    
    # If project_root provided, make path relative
    if project_root:
        try:
            path_obj = Path(path_str)
            if path_obj.is_absolute():
                path_str = str(path_obj.relative_to(project_root))
        except ValueError:
            # Path is not relative to project_root, use as-is
            pass
    
    # Remove .py extension
    if path_str.endswith(".py"):
        path_str = path_str[:-3]
    
    # Normalize path separators to forward slashes first
    path_str = path_str.replace("\\", "/")
    
    # Convert slashes to dots
    module_path = path_str.replace("/", ".")
    
    # Remove leading dots if any
    module_path = module_path.lstrip(".")
    
    return module_path


def module_to_path(
    module_path: str,
    project_root: Optional[Path] = None,
    add_py_extension: bool = True
) -> Path:
    """
    Convert a Python module path to a file path.
    
    Args:
        module_path: Dot-notation module path
        project_root: Optional project root to prepend
        add_py_extension: If True, add .py extension
        
    Returns:
        Path object representing the file location
        
    Examples:
        >>> module_to_path("agentic_core.utils.file_utils")
        Path('agentic_core/utils/file_utils.py')
        
        >>> module_to_path("agentic_core.utils.file_utils", Path("/project"))
        Path('/project/agentic_core/utils/file_utils.py')
    """
    # Convert dots to path separators
    path_str = module_path.replace(".", os.sep)
    
    # Add .py extension if requested
    if add_py_extension:
        path_str += ".py"
    
    path = Path(path_str)
    
    # Prepend project root if provided
    if project_root:
        path = project_root / path
    
    return path


def safe_import_module(
    module_path: str,
    suppress_errors: bool = False
) -> Optional[Any]:
    """
    Safely import a module by its dot-notation path.
    
    Args:
        module_path: Dot-notation module path (e.g., "agentic_core.utils.file_utils")
        suppress_errors: If True, don't log errors (useful for optional imports)
        
    Returns:
        The imported module, or None if import failed
        
    Example:
        module = safe_import_module("agentic_core.utils.file_utils")
        if module:
            content = module.safe_read_file(path)
    """
    try:
        return importlib.import_module(module_path)
    except ImportError as e:
        if not suppress_errors:
            Logger.debug(f"[IMPORT] Failed to import {module_path}: {e}")
        return None
    except Exception as e:
        if not suppress_errors:
            Logger.warning(f"[IMPORT] Unexpected error importing {module_path}: {e}")
        return None


def safe_import_class(
    module_path: str,
    class_name: str,
    suppress_errors: bool = False
) -> Optional[Type]:
    """
    Safely import a class from a module.
    
    Args:
        module_path: Dot-notation module path
        class_name: Name of the class to import
        suppress_errors: If True, don't log errors
        
    Returns:
        The class, or None if import failed
        
    Example:
        AgentResult = safe_import_class("agentic_core.utils.result_utils", "AgentResult")
        if AgentResult:
            result = AgentResult(agent_name="Test")
    """
    module = safe_import_module(module_path, suppress_errors=suppress_errors)
    if module is None:
        return None
    
    try:
        cls = getattr(module, class_name)
        return cls
    except AttributeError:
        if not suppress_errors:
            Logger.debug(f"[IMPORT] Class {class_name} not found in {module_path}")
        return None


def safe_import_function(
    module_path: str,
    function_name: str,
    suppress_errors: bool = False
) -> Optional[Any]:
    """
    Safely import a function from a module.
    
    Args:
        module_path: Dot-notation module path
        function_name: Name of the function to import
        suppress_errors: If True, don't log errors
        
    Returns:
        The function, or None if import failed
        
    Example:
        normalize = safe_import_function("agentic_core.utils.result_utils", "normalize_agent_result")
        if normalize:
            result = normalize("Agent", raw_result)
    """
    module = safe_import_module(module_path, suppress_errors=suppress_errors)
    if module is None:
        return None
    
    try:
        func = getattr(module, function_name)
        if callable(func):
            return func
        if not suppress_errors:
            Logger.debug(f"[IMPORT] {function_name} in {module_path} is not callable")
        return None
    except AttributeError:
        if not suppress_errors:
            Logger.debug(f"[IMPORT] Function {function_name} not found in {module_path}")
        return None


def get_module_from_file(
    file_path: Union[str, Path],
    project_root: Optional[Path] = None,
    suppress_errors: bool = False
) -> Optional[Any]:
    """
    Import a module from its file path.
    
    Convenience function that combines path_to_module and safe_import_module.
    
    Args:
        file_path: Path to the Python file
        project_root: Optional project root for relative path calculation
        suppress_errors: If True, don't log errors
        
    Returns:
        The imported module, or None if import failed
        
    Example:
        module = get_module_from_file("agentic_core/utils/file_utils.py")
    """
    module_path = path_to_module(file_path, project_root)
    return safe_import_module(module_path, suppress_errors=suppress_errors)


def get_class_from_file(
    file_path: Union[str, Path],
    class_name: str,
    project_root: Optional[Path] = None,
    suppress_errors: bool = False
) -> Optional[Type]:
    """
    Import a class from a file path.
    
    Convenience function that combines path_to_module and safe_import_class.
    
    Args:
        file_path: Path to the Python file
        class_name: Name of the class to import
        project_root: Optional project root for relative path calculation
        suppress_errors: If True, don't log errors
        
    Returns:
        The class, or None if import failed
        
    Example:
        LocationAgent = get_class_from_file(
            "agentic_core/L5_safety/validators/LocationAgent.py",
            "LocationAgent"
        )
    """
    module_path = path_to_module(file_path, project_root)
    return safe_import_class(module_path, class_name, suppress_errors=suppress_errors)


__all__ = [
    "path_to_module",
    "module_to_path",
    "safe_import_module",
    "safe_import_class",
    "safe_import_function",
    "get_module_from_file",
    "get_class_from_file",
]
