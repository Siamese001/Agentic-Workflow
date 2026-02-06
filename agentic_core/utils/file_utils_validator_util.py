"""
SSOT for safe file I/O operations.

This module provides atomic write patterns and safe read operations
to prevent data corruption and handle edge cases gracefully.

SSOT Consolidation (Jan 20, 2026):
All file I/O operations should use these utilities instead of
raw open()/write() calls.
"""

import logging
import os
import shutil
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)


def ensure_directory(path: str | Path) -> bool:
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
    except OSError as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def safe_read_file(
    path: str | Path,
    encoding: str = "utf-8",
    default=None,
    errors: str = "replace",
) -> str | None:
    """
    Safely read a file with proper error handling.

    Args:
        path: Path to the file to read.
        encoding: File encoding (default: utf-8).
        default: Default value to return if file cannot be read.
        errors: Error handling strategy (default: replace).

    Returns:
        File contents as string, or default value if read fails.
    """
    try:
        return Path(path).read_text(encoding=encoding, errors=errors)
    except (OSError, UnicodeDecodeError) as e:
        logger.warning(f"Failed to read file {path}: {e}")
        return default


def safe_write_file(path: str | Path, content: str, encoding: str = "utf-8", backup: bool = True) -> bool:
    """
    Safely write a file using atomic write pattern.

    Args:
        path: Path to the file to write.
        content: Content to write to the file.
        encoding: File encoding (default: utf-8).
        backup: Whether to create backup of existing file.

    Returns:
        True if write was successful, False otherwise.
    """
    path = Path(path)

    # Create backup if requested and file exists
    if backup and path.exists():
        backup_path = path.with_suffix(f"{path.suffix}.bak")
        try:
            shutil.copy2(path, backup_path)
        except OSError as e:
            logger.warning(f"Failed to create backup of {path}: {e}")

    # Ensure parent directory exists
    ensure_directory(path.parent)

    # Write to temporary file first, then atomic rename
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    try:
        temp_path.write_text(content, encoding=encoding)
        temp_path.replace(path)
        return True
    except OSError as e:
        logger.error(f"Failed to write file {path}: {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        return False


def safe_append_file(path: str | Path, content: str, encoding: str = "utf-8") -> bool:
    """
    Safely append content to a file.

    Args:
        path: Path to the file to append to.
        content: Content to append.
        encoding: File encoding (default: utf-8).

    Returns:
        True if append was successful, False otherwise.
    """
    try:
        path = Path(path)
        ensure_directory(path.parent)
        with open(path, "a", encoding=encoding) as f:
            f.write(content)
        return True
    except OSError as e:
        logger.error(f"Failed to append to file {path}: {e}")
        return False


def safe_delete_file(path: str | Path, backup: bool = True) -> bool:
    """
    Safely delete a file with optional backup.

    Args:
        path: Path to the file to delete.
        backup: Whether to create backup before deletion.

    Returns:
        True if deletion was successful, False otherwise.
    """
    path = Path(path)

    if not path.exists():
        return True

    # Create backup if requested
    if backup:
        backup_path = path.with_suffix(f"{path.suffix}.bak")
        try:
            shutil.copy2(path, backup_path)
        except OSError as e:
            logger.warning(f"Failed to create backup of {path}: {e}")

    try:
        path.unlink()
        return True
    except OSError as e:
        logger.error(f"Failed to delete file {path}: {e}")
        return False


def safe_move_file(src: str | Path, dst: str | Path, backup: bool = True) -> bool:
    """
    Safely move a file with optional backup of destination.

    Args:
        src: Source file path.
        dst: Destination file path.
        backup: Whether to backup existing destination file.

    Returns:
        True if move was successful, False otherwise.
    """
    src, dst = Path(src), Path(dst)

    if not src.exists():
        logger.error(f"Source file {src} does not exist")
        return False

    # Create backup of destination if it exists
    if backup and dst.exists():
        backup_path = dst.with_suffix(f"{dst.suffix}.bak")
        try:
            shutil.copy2(dst, backup_path)
        except OSError as e:
            logger.warning(f"Failed to create backup of {dst}: {e}")

    # Ensure destination directory exists
    ensure_directory(dst.parent)

    try:
        shutil.move(str(src), str(dst))
        return True
    except OSError as e:
        logger.error(f"Failed to move file {src} to {dst}: {e}")
        return False


def get_file_size(path: str | Path) -> int:
    """
    Get file size in bytes.

    Args:
        path: Path to the file.

    Returns:
        File size in bytes, or -1 if file doesn't exist.
    """
    try:
        return Path(path).stat().st_size
    except OSError:
        return -1


def is_file_empty(path: str | Path) -> bool:
    """
    Check if file is empty.

    Args:
        path: Path to the file.

    Returns:
        True if file is empty or doesn't exist, False otherwise.
    """
    return get_file_size(path) <= 0


def create_temp_file(prefix: str = "temp", suffix: str = ".tmp", dir: str | Path = None) -> Path:
    """
    Create a temporary file.

    Args:
        prefix: File name prefix.
        suffix: File name suffix.
        dir: Directory for temporary file (default: system temp).

    Returns:
        Path to the created temporary file.
    """
    import tempfile

    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=dir)
    os.close(fd)  # Close file descriptor, we'll manage the file ourselves
    return Path(path)
