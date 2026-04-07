"""
File System Utilities - Canonical implementations for common file operations.

This module provides pure, stateless utilities for file system operations
that are commonly duplicated across the codebase.
"""

import hashlib
import os
from pathlib import Path
from typing import Generator

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)


def get_python_files_fast(
    root_dir: Path, exclude_dirs: list[str] | None = None, exclude_patterns: list[str] | None = None,
) -> Generator[Path, None, None]:
    """
    Fast Python file discovery with configurable filtering.

    Args:
        root_dir: Root directory to search
        exclude_dirs: Directory names to exclude (default: ['__pycache__', '.git', 'venv', 'env'])
        exclude_patterns: File patterns to exclude (default: ['*.pyc', '*.pyo'])

    Yields:
        Path objects for Python files found
    """
    if exclude_dirs is None:
        exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

    if exclude_patterns is None:
        exclude_patterns = ["*.pyc", "*.pyo", "*.pyd"]

    for root, dirs, files in os.walk(root_dir):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file

                # Check exclude patterns
                if not any(file_path.match(pattern) for pattern in exclude_patterns):
                    yield file_path


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Calculate hash of file content.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (default: 'sha256')

    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.new(algorithm)

    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    # guardian: allow-silent-swallow - acceptable exception handling
    except OSError:
        return ""


def get_canonical_path(path: Path) -> Path:
    """
    Get canonical path with forward slashes and resolved components.

    Args:
        path: Path to normalize

    Returns:
        Canonical Path object
    """
    # Resolve to absolute path, then convert to forward slashes
    resolved = path.resolve()
    return Path(str(resolved).replace("\\", "/"))


def remove_duplicate_suffix_path(
    duplicate_path: Path, problematic_suffixes: list[str],
) -> tuple[Path, str | None]:
    """
    Get the canonical path by removing duplicate suffix.

    Args:
        duplicate_path: Path with potential duplicate suffix
        problematic_suffixes: List of suffixes to remove

    Returns:
        Tuple of (canonical_path, matched_suffix)
    """
    stem = duplicate_path.stem
    for suffix in problematic_suffixes:
        if stem.endswith(suffix):
            canonical_stem = stem[: -len(suffix)]
            canonical_path = duplicate_path.parent / f"{canonical_stem}.py"
            return (canonical_path, suffix)
    return (duplicate_path, None)
