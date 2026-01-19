"""
Safe File Operations Utilities - Centralized File I/O with Error Handling

This module provides centralized utilities for safe file operations,
eliminating repeated try/except blocks across 447+ files.

USAGE:
    from agentic_core.utils.file_utils import (
        safe_read_file,
        safe_write_file,
        safe_read_json,
        safe_write_json,
    )
    
    # Read file safely
    content = safe_read_file(Path("config.txt"))
    if content is None:
        print("File not found or unreadable")
    
    # Write file atomically
    success = safe_write_file(Path("output.txt"), "content", atomic=True)
    
    # Read JSON safely
    data = safe_read_json(Path("config.json"), default={})
    
    # Write JSON atomically
    safe_write_json(Path("output.json"), {"key": "value"})

FEATURES:
    - UTF-8 encoding by default with configurable error handling
    - Atomic writes (write to .tmp, then rename) to prevent corruption
    - Consistent error logging
    - Default values for missing/corrupt files
    - Cross-platform path handling
"""
from __future__ import annotations
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Optional, Union

Logger = logging.getLogger(__name__)


def safe_read_file(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    errors: str = "replace",
    default: Optional[str] = None
) -> Optional[str]:
    """
    Safely read a file with proper encoding and error handling.
    
    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)
        errors: How to handle encoding errors (default: replace)
        default: Value to return if file cannot be read (default: None)
        
    Returns:
        File contents as string, or default value if file cannot be read
        
    Example:
        content = safe_read_file(Path("config.txt"))
        if content is None:
            print("Could not read file")
    """
    path = Path(file_path)
    
    if not path.exists():
        Logger.debug(f"[FILE] File not found: {path}")
        return default
    
    try:
        return path.read_text(encoding=encoding, errors=errors)
    except PermissionError as e:
        Logger.warning(f"[FILE] Permission denied reading {path}: {e}")
        return default
    except UnicodeDecodeError as e:
        Logger.warning(f"[FILE] Encoding error reading {path}: {e}")
        return default
    except OSError as e:
        Logger.error(f"[FILE] OS error reading {path}: {e}")
        return default
    except Exception as e:
        Logger.error(f"[FILE] Unexpected error reading {path}: {e}")
        return default


def safe_write_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    atomic: bool = True,
    create_dirs: bool = True
) -> bool:
    """
    Safely write content to a file with optional atomic write.
    
    Atomic writes work by writing to a temporary file first, then
    renaming it to the target path. This prevents partial writes
    from corrupting the file if the process is interrupted.
    
    Args:
        file_path: Path to write to
        content: String content to write
        encoding: File encoding (default: utf-8)
        atomic: If True, use atomic write (write to .tmp, then rename)
        create_dirs: If True, create parent directories if needed
        
    Returns:
        True if write succeeded, False otherwise
        
    Example:
        success = safe_write_file(Path("output.txt"), "Hello, World!")
        if not success:
            print("Write failed")
    """
    path = Path(file_path)
    
    try:
        # Create parent directories if needed
        if create_dirs and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        if atomic:
            # Write to temporary file first
            tmp_path = path.with_suffix(path.suffix + ".tmp")
            try:
                tmp_path.write_text(content, encoding=encoding)
                # Atomic rename (on most filesystems)
                tmp_path.replace(path)
                return True
            except Exception as e:
                # Clean up temp file on failure
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except Exception:
                        pass
                raise e
        else:
            # Direct write
            path.write_text(content, encoding=encoding)
            return True
            
    except PermissionError as e:
        Logger.warning(f"[FILE] Permission denied writing {path}: {e}")
        return False
    except OSError as e:
        Logger.error(f"[FILE] OS error writing {path}: {e}")
        return False
    except Exception as e:
        Logger.error(f"[FILE] Unexpected error writing {path}: {e}")
        return False


def safe_read_json(
    file_path: Union[str, Path],
    default: Any = None,
    encoding: str = "utf-8"
) -> Any:
    """
    Safely read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        default: Value to return if file cannot be read or parsed
        encoding: File encoding (default: utf-8)
        
    Returns:
        Parsed JSON data, or default value if file cannot be read/parsed
        
    Example:
        config = safe_read_json(Path("config.json"), default={})
        agents = safe_read_json(Path("agents.json"), default=[])
    """
    path = Path(file_path)
    
    if not path.exists():
        Logger.debug(f"[JSON] File not found: {path}")
        return default
    
    try:
        content = path.read_text(encoding=encoding)
        return json.loads(content)
    except json.JSONDecodeError as e:
        Logger.warning(f"[JSON] Parse error in {path}: {e}")
        return default
    except PermissionError as e:
        Logger.warning(f"[JSON] Permission denied reading {path}: {e}")
        return default
    except UnicodeDecodeError as e:
        Logger.warning(f"[JSON] Encoding error reading {path}: {e}")
        return default
    except Exception as e:
        Logger.error(f"[JSON] Unexpected error reading {path}: {e}")
        return default


def safe_write_json(
    file_path: Union[str, Path],
    data: Any,
    indent: int = 2,
    encoding: str = "utf-8",
    atomic: bool = True,
    create_dirs: bool = True,
    ensure_ascii: bool = False
) -> bool:
    """
    Safely write data to a JSON file with optional atomic write.
    
    Args:
        file_path: Path to write to
        data: Data to serialize as JSON
        indent: JSON indentation level (default: 2)
        encoding: File encoding (default: utf-8)
        atomic: If True, use atomic write
        create_dirs: If True, create parent directories if needed
        ensure_ascii: If True, escape non-ASCII characters
        
    Returns:
        True if write succeeded, False otherwise
        
    Example:
        success = safe_write_json(Path("config.json"), {"key": "value"})
    """
    try:
        content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        return safe_write_file(
            file_path,
            content,
            encoding=encoding,
            atomic=atomic,
            create_dirs=create_dirs
        )
    except TypeError as e:
        Logger.error(f"[JSON] Serialization error for {file_path}: {e}")
        return False
    except Exception as e:
        Logger.error(f"[JSON] Unexpected error writing {file_path}: {e}")
        return False


def safe_read_lines(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    errors: str = "replace",
    strip: bool = True,
    skip_empty: bool = False
) -> list:
    """
    Safely read a file and return lines as a list.
    
    Args:
        file_path: Path to the file
        encoding: File encoding (default: utf-8)
        errors: How to handle encoding errors
        strip: If True, strip whitespace from each line
        skip_empty: If True, skip empty lines
        
    Returns:
        List of lines, or empty list if file cannot be read
    """
    content = safe_read_file(file_path, encoding=encoding, errors=errors)
    if content is None:
        return []
    
    lines = content.splitlines()
    
    if strip:
        lines = [line.strip() for line in lines]
    
    if skip_empty:
        lines = [line for line in lines if line]
    
    return lines


def file_exists(file_path: Union[str, Path]) -> bool:
    """
    Check if a file exists.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file exists, False otherwise
    """
    return Path(file_path).exists()


def ensure_directory(dir_path: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        dir_path: Path to the directory
        
    Returns:
        True if directory exists or was created, False on error
    """
    path = Path(dir_path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        Logger.error(f"[FILE] Failed to create directory {path}: {e}")
        return False


__all__ = [
    "safe_read_file",
    "safe_write_file",
    "safe_read_json",
    "safe_write_json",
    "safe_read_lines",
    "file_exists",
    "ensure_directory",
]
