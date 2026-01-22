from __future__ import annotations

"""
Scan Guard - Audit Utility for rglob/glob Usage

Phase 4 Performance Hardening: This module provides utilities to track and
discourage expensive rglob/glob calls, guiding developers toward the
high-performance ssot_discovery or file_cache modules.

Usage:

    # Instead of: path.rglob("*.py")
    # Use: guarded_rglob(path, "*.py")  # Logs warning + suggests FileCache

    # Better yet, use FileCache directly:
    from agentic_core.utils.file_cache import FileCache, get_python_files
    cache = FileCache.get_instance(project_root)
    files = cache.get_python_files()

Author: Cascade
Date: January 19, 2026
Phase: 4 - Performance Hardening (rglob Elimination)

Updated: January 20, 2026
- Added FileCache reference (os.walk with directory pruning)
- Added backup directory blocking
"""


import functools
import logging
import warnings
from collections.abc import Iterator
from pathlib import Path

Logger = logging.getLogger(__name__)


# Dangerous directories that should never be scanned directly
DANGEROUS_DIRECTORIES = {
    ".sovereign_healing_backup",
    "healing_backups",
    ".git",
    "__pycache__",
    "node_modules",
}


def guarded_rglob(path: Path, pattern: str, caller: str | None = None) -> Iterator[Path]:
    """
    Audit utility to track and discourage expensive rglob calls.

    Logs a DeprecationWarning suggesting FileCache before executing the scan.
    Use this as a drop-in replacement for path.rglob() during migration.

    Args:
        path: The path to scan
        pattern: The glob pattern (e.g., "*.py")
        caller: Optional caller identifier for logging

    Returns:
        Iterator of matching Path objects (same as rglob)

    Example:
        # Instead of: path.rglob("*.py")
        files = list(guarded_rglob(path, "*.py"))
    """
    caller_info = f" (caller: {caller})" if caller else ""
    path_str = str(path)

    # Block scanning of dangerous directories (CRITICAL: Prevents hangs)
    for dangerous in DANGEROUS_DIRECTORIES:
        if dangerous in path_str:
            warnings.warn(
                f"BLOCKED: Dangerous directory scan attempted: {path}. "
                "This can cause infinite loops or extreme I/O. Use FileCache instead.",
                RuntimeWarning,
                stacklevel=2,
            )
            Logger.error(f"[SCAN_GUARD] BLOCKED: Dangerous directory scan: {path}")
            # Fail-safe: Return empty iterator instead of allowing scan
            return iter([])

    warnings.warn(
        f"Expensive rglob('{pattern}') detected at {path}{caller_info}. "
        "Please refactor to use agentic_core.utils.file_cache.FileCache "
        "for better performance (uses os.walk with directory pruning).",
        DeprecationWarning,
        stacklevel=2,
    )

    Logger.warning(
        f"[SCAN_GUARD] rglob('{pattern}') called on {path}{caller_info}. "
        "Consider migrating to FileCache."
    )

    return path.rglob(pattern)


def guarded_glob(path: Path, pattern: str, caller: str | None = None) -> Iterator[Path]:
    """
    Audit utility to track and discourage expensive glob calls.

    Logs a DeprecationWarning suggesting FileCache before executing the scan.
    Use this as a drop-in replacement for path.glob() during migration.

    Args:
        path: The path to scan
        pattern: The glob pattern (e.g., "*.py")
        caller: Optional caller identifier for logging

    Returns:
        Iterator of matching Path objects (same as glob)
    """
    caller_info = f" (caller: {caller})" if caller else ""

    warnings.warn(
        f"Expensive glob('{pattern}') detected at {path}{caller_info}. "
        "Please refactor to use agentic_core.utils.ssot_discovery for better performance.",
        DeprecationWarning,
        stacklevel=2,
    )

    Logger.warning(
        f"[SCAN_GUARD] glob('{pattern}') called on {path}{caller_info}. "
        "Consider migrating to ssot_discovery."
    )

    return path.glob(pattern)


def deprecate_rglob(func):
    """
    Decorator to mark functions that use rglob as deprecated.

    Usage:
        @deprecate_rglob
        def my_function_with_rglob():
            return path.rglob("*.py")
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"Function {func.__name__} uses rglob which is deprecated. "
            "Please refactor to use agentic_core.utils.ssot_discovery.",
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper


def count_rglob_calls_in_file(file_path: Path) -> int:
    """
    Count the number of rglob/glob calls in a Python file.

    Useful for auditing and tracking migration progress.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        Count of rglob/glob calls found
    """
    import re

    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0

    # Count .rglob( and .glob( calls
    rglob_pattern = r"\.rglob\s*\("
    glob_pattern = r"\.glob\s*\("

    rglob_count = len(re.findall(rglob_pattern, content))
    glob_count = len(re.findall(glob_pattern, content))

    return rglob_count + glob_count


def audit_rglob_usage(project_root: Path) -> dict:
    """
    Audit all rglob/glob usage in the project.

    Returns a report of files with rglob/glob calls and their counts.

    Args:
        project_root: Root directory of the project

    Returns:
        Dict with audit results
    """
    from agentic_core.utils.ssot_discovery import get_python_files

    files = get_python_files(project_root)

    offenders = []
    total_calls = 0

    for file_path in files:
        count = count_rglob_calls_in_file(file_path)
        if count > 0:
            offenders.append({"file": str(file_path.relative_to(project_root)), "count": count})
            total_calls += count

    # Sort by count descending
    offenders.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total_files_scanned": len(files),
        "files_with_rglob": len(offenders),
        "total_rglob_calls": total_calls,
        "top_offenders": offenders[:20],  # Top 20
        "all_offenders": offenders,
    }


__all__ = [
    "guarded_rglob",
    "guarded_glob",
    "deprecate_rglob",
    "count_rglob_calls_in_file",
    "audit_rglob_usage",
]
