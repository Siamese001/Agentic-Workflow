"""
SSOT for safe file I/O operations.

This module provides atomic write patterns and safe read operations
to prevent data corruption and handle edge cases gracefully.

SSOT Consolidation (Jan 20, 2026):
All file I/O operations should use these utilities instead of
raw open()/write() calls.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Union, Any
import logging

# Configure logger
logger = logging.getLogger(__name__)


def ensure_directory(path: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: The directory path to ensure exists.
        
    Returns:
        True if directory exists or was created successfully, False otherwise.
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def safe_read_file(path: Union[str, Path], encoding: str = "utf-8") -> Optional[str]:
    """
    Safely read a file's content.
    
    Args:
        path: The file path to read.
        encoding: The file encoding (default: utf-8).
        
    Returns:
        The file content as a string, or None if file doesn't exist or cannot be read.
    """
    try:
        p = Path(path)
        if not p.exists():
            return None
        return p.read_text(encoding=encoding)
    except UnicodeDecodeError as e:
        logger.warning(f"Unicode decode error reading {path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")
        return None


def safe_write_file(
    path: Union[str, Path], 
    content: str, 
    encoding: str = "utf-8",
    make_dirs: bool = True
) -> bool:
    """
    Safely write content to a file using an atomic write pattern.
    
    Uses write-to-temp-then-rename pattern for atomicity.
    
    Args:
        path: The target file path.
        content: The content to write.
        encoding: The file encoding (default: utf-8).
        make_dirs: If True, create parent directories if they don't exist.
        
    Returns:
        True if write succeeded, False otherwise.
    """
    target_path = Path(path)
    temp_path = None
    
    try:
        if make_dirs:
            ensure_directory(target_path.parent)
            
        # Write to a temp file first
        temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
        temp_path.write_text(content, encoding=encoding)
        
        # Atomic replace (POSIX compliant, usually safe on Windows too)
        # On Windows, os.replace allows overwriting
        os.replace(temp_path, target_path)
        return True
    except Exception as e:
        logger.error(f"Failed to write file {path}: {e}")
        # Cleanup temp file if it exists
        if temp_path is not None and temp_path.exists():
            try:
                os.remove(temp_path)
            except Exception:
                pass
        return False


def safe_delete_file(path: Union[str, Path]) -> bool:
    """
    Safely delete a file if it exists.
    
    Args:
        path: The file path to delete.
        
    Returns:
        True if file was deleted or didn't exist, False on error.
    """
    try:
        p = Path(path)
        if p.exists():
            p.unlink()
        return True
    except Exception as e:
        logger.error(f"Failed to delete file {path}: {e}")
        return False


def safe_copy_file(
    src: Union[str, Path], 
    dst: Union[str, Path],
    make_dirs: bool = True
) -> bool:
    """
    Safely copy a file from source to destination.
    
    Args:
        src: Source file path.
        dst: Destination file path.
        make_dirs: If True, create parent directories if they don't exist.
        
    Returns:
        True if copy succeeded, False otherwise.
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            logger.error(f"Source file does not exist: {src}")
            return False
            
        if make_dirs:
            ensure_directory(dst_path.parent)
            
        shutil.copy2(src_path, dst_path)
        return True
    except Exception as e:
        logger.error(f"Failed to copy {src} to {dst}: {e}")
        return False


def safe_move_file(
    src: Union[str, Path], 
    dst: Union[str, Path],
    make_dirs: bool = True
) -> bool:
    """
    Safely move a file from source to destination.
    
    Args:
        src: Source file path.
        dst: Destination file path.
        make_dirs: If True, create parent directories if they don't exist.
        
    Returns:
        True if move succeeded, False otherwise.
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            logger.error(f"Source file does not exist: {src}")
            return False
            
        if make_dirs:
            ensure_directory(dst_path.parent)
            
        shutil.move(str(src_path), str(dst_path))
        return True
    except Exception as e:
        logger.error(f"Failed to move {src} to {dst}: {e}")
        return False


__all__ = [
    "ensure_directory",
    "safe_read_file",
    "safe_write_file",
    "safe_delete_file",
    "safe_copy_file",
    "safe_move_file",
]
