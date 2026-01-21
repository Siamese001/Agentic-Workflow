"""
SSOT Discovery Module - Phase 1 Foundation + Phase 4 Performance Hardening

High-performance, centralized file discovery utility that excludes backup bloat
and focuses on active code. This replaces scattered rglob/glob usage across the codebase.

Key Features:
- Excludes .sovereign_healing_backup/ (10k+ files) and archives/
- Excludes __pycache__, .git, and other non-essential directories
- Optional test file inclusion
- Layer-specific file discovery
- FileCache for persistent caching (Phase 4)
- LRU cache for in-memory caching

Usage:
    from agentic_core.utils.ssot_discovery import get_python_files, get_files_by_layer, FileCache

    # Get all active Python files
    files = get_python_files(project_root)

    # Get files for a specific layer
    l3_files = get_files_by_layer(project_root, "L3")

    # Use persistent file cache
    cache = FileCache(project_root / ".file_cache.json")
    files = cache.get_files() if cache.is_valid() else get_python_files(project_root)

Author: Cascade
Date: January 19, 2026
Phase: 1 - Foundation & Zero-Loss Protocols
Phase 4 Enhancement: FileCache for persistent caching
"""

from __future__ import annotations

import json
import logging
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


# =============================================================================
# Phase 4: FileCache - Persistent File Discovery Cache
# =============================================================================


class FileCache:
    """
    Performance Hardening: Caches the repository file map to prevent
    repeated scanning of 10k+ backup files.

    Saves a JSON manifest of Python files to avoid repeated disk I/O.
    The cache auto-expires after a configurable time period.

    Usage:
        cache = FileCache(project_root / ".file_cache.json")

        if cache.is_valid():
            files = cache.get_files()
        else:
            files = get_python_files(project_root)
            cache.update([str(f) for f in files])
    """

    DEFAULT_EXPIRY_SECONDS = 300  # 5 minutes

    def __init__(self, cache_path: Path, expiry_seconds: int = DEFAULT_EXPIRY_SECONDS):
        """
        Initialize the file cache.

        Args:
            cache_path: Path to the JSON cache file
            expiry_seconds: Cache expiry time in seconds (default: 300)
        """
        self.cache_path = Path(cache_path)
        self.expiry_seconds = expiry_seconds
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        """Load cache from disk if it exists."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, encoding="utf-8") as f:
                    data = json.load(f)
                    Logger.debug(
                        f"[FILE_CACHE] Loaded {len(data.get('files', []))} files from cache"
                    )
                    return data
            except (OSError, json.JSONDecodeError) as e:
                Logger.warning(f"[FILE_CACHE] Failed to load cache: {e}")
                return {"timestamp": 0, "files": []}
        return {"timestamp": 0, "files": []}

    def is_valid(self, expiry_seconds: int | None = None) -> bool:
        """
        Check if the cache is still valid (not expired).

        Args:
            expiry_seconds: Override default expiry time

        Returns:
            True if cache is valid and not expired
        """
        expiry = expiry_seconds or self.expiry_seconds
        cache_time = self._data.get("timestamp", 0)
        is_valid = (time.time() - cache_time) < expiry

        if not is_valid:
            Logger.debug(f"[FILE_CACHE] Cache expired (age: {time.time() - cache_time:.0f}s)")

        return is_valid

    def update(self, files: list[str]) -> None:
        """
        Update the cache with a new file list.

        Args:
            files: List of file paths as strings
        """
        self._data = {"timestamp": time.time(), "files": files, "count": len(files)}

        try:
            # Ensure parent directory exists
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)

            Logger.debug(f"[FILE_CACHE] Updated cache with {len(files)} files")
        except OSError as e:
            Logger.warning(f"[FILE_CACHE] Failed to write cache: {e}")

    def get_files(self) -> list[Path]:
        """
        Get the cached file list as Path objects.

        Returns:
            List of Path objects from the cache
        """
        return [Path(f) for f in self._data.get("files", [])]

    def invalidate(self) -> None:
        """
        Invalidate the cache by setting timestamp to 0.

        Call this when the repository structure changes.
        """
        self._data["timestamp"] = 0

        # Also delete the cache file
        if self.cache_path.exists():
            try:
                self.cache_path.unlink()
                Logger.debug("[FILE_CACHE] Cache file deleted")
            except OSError as e:
                Logger.warning(f"[FILE_CACHE] Failed to delete cache file: {e}")

        Logger.debug("[FILE_CACHE] Cache invalidated")

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats (age, count, valid)
        """
        cache_time = self._data.get("timestamp", 0)
        age = time.time() - cache_time if cache_time > 0 else -1

        return {
            "valid": self.is_valid(),
            "age_seconds": age,
            "file_count": len(self._data.get("files", [])),
            "cache_path": str(self.cache_path),
            "expiry_seconds": self.expiry_seconds,
        }

    def get_timestamp(self) -> float:
        """
        Get the cache timestamp.

        Returns:
            Unix timestamp of when cache was last updated
        """
        return self._data.get("timestamp", 0)

    def is_stale_for_directory(self, directory: Path) -> bool:
        """
        Check if cache is stale compared to directory modification time.

        Phase 4.1: Auto-invalidation based on directory mtime.

        Args:
            directory: Directory to check modification time against

        Returns:
            True if directory was modified after cache was created
        """
        try:
            dir_mtime = directory.stat().st_mtime
            cache_time = self.get_timestamp()

            if cache_time == 0:
                return True  # No cache yet

            return dir_mtime > cache_time
        except OSError:
            return True  # If we can't stat, assume stale


# =============================================================================
# Global File Cache Instance
# =============================================================================

_global_cache: FileCache | None = None


def get_global_cache(project_root: Path | None = None) -> FileCache:
    """
    Get or create the global file cache instance.

    Args:
        project_root: Project root directory (required on first call)

    Returns:
        FileCache instance
    """
    global _global_cache

    if _global_cache is None:
        if project_root is None:
            raise ValueError("project_root required on first call to get_global_cache()")
        _global_cache = FileCache(project_root / ".file_cache.json")

    return _global_cache


def get_python_files_cached(
    project_root: Path, include_tests: bool = False, force_refresh: bool = False
) -> list[Path]:
    """
    Get Python files with automatic caching and auto-invalidation.

    This is the recommended function for most use cases.
    Uses FileCache for persistent caching across sessions.

    Phase 4.1: Auto-invalidation based on directory mtime.
    If the agentic_core directory has been modified since the cache
    was created, the cache is automatically invalidated.

    Args:
        project_root: Root directory to scan
        include_tests: If True, include test files
        force_refresh: If True, bypass cache and rescan

    Returns:
        List of Path objects for all matching Python files
    """
    cache = get_global_cache(project_root)

    # Phase 4.1: Auto-invalidation based on directory mtime
    agentic_core_dir = project_root / "agentic_core"
    if agentic_core_dir.exists() and cache.is_stale_for_directory(agentic_core_dir):
        Logger.debug("[SSOT_DISCOVERY] Auto-invalidating cache due to directory change")
        cache.invalidate()

    if not force_refresh and cache.is_valid():
        files = cache.get_files()
        Logger.debug(f"[SSOT_DISCOVERY] Returning {len(files)} files from cache")
        return files

    # Cache miss or forced refresh - do full scan
    files = get_python_files(project_root, include_tests=include_tests)

    # Update cache
    cache.update([str(f) for f in files])

    return files


# SSOT Import: Use centralized exclusion list from config
# This ensures consistency across all file discovery operations
try:
    from agentic_core.config.blueprint_sovereign.constants import (
        DEFAULT_EXCLUDE_DIRS as SSOT_EXCLUDE_DIRS,
    )

    # Convert frozenset to set for compatibility
    DEFAULT_EXCLUDE_DIRS: set[str] = set(SSOT_EXCLUDE_DIRS)
except ImportError:
    # Fallback if config not available (bootstrap scenario)
    DEFAULT_EXCLUDE_DIRS: set[str] = {
        ".sovereign_healing_backup",
        "archives",
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".tox",
        "build",
        "dist",
        "*.egg-info",
    }

# Layer directories in agentic_core
LAYER_DIRS: dict[str, str] = {
    "L0": "L0_maintenance",
    "L1": "L1_cognition",
    "L2": "L2_execution",
    "L3": "L3_orchestration",
    "L4": "L4_state",
    "L5": "L5_safety",
    "L6": "L6_observability",
}


def get_python_files(
    project_root: Path,
    include_tests: bool = False,
    exclude_dirs: set[str] | None = None,
    include_dirs: set[str] | None = None,
) -> list[Path]:
    """
    High-performance SSOT for Python file discovery.
    Optimized to ignore backup bloat (10k+ files) and focus on active code.

    Args:
        project_root: Root directory to scan
        include_tests: If True, include test files (test_*.py, *_test.py)
        exclude_dirs: Additional directories to exclude (merged with defaults)
        include_dirs: If specified, only scan these directories

    Returns:
        List of Path objects for all matching Python files

    Example:
        >>> files = get_python_files(Path("c:/Git/Agentic-Workflow"))
        >>> len(files)  # ~800 active files, not 10k+ with backups
        800
    """
    # Merge default excludes with any additional excludes
    all_excludes = DEFAULT_EXCLUDE_DIRS.copy()
    if exclude_dirs:
        all_excludes.update(exclude_dirs)

    active_files: list[Path] = []

    # Ensure project_root is a Path
    project_root = Path(project_root)

    for root, dirs, files in os.walk(project_root):
        root_path = Path(root)

        # Filter out excluded directories (modifies dirs in-place to prevent traversal)
        dirs[:] = [d for d in dirs if d not in all_excludes and not d.startswith(".")]

        # If include_dirs specified, filter to only those
        if include_dirs:
            dirs[:] = [
                d
                for d in dirs
                if d in include_dirs
                or any(str(root_path / d).endswith(inc) for inc in include_dirs)
            ]

        for file in files:
            if not file.endswith(".py"):
                continue

            # Skip test files unless explicitly included
            if not include_tests:
                if file.startswith("test_") or file.endswith("_test.py"):
                    continue
                if "conftest" in file:
                    continue

            # Skip __init__.py files that are empty or minimal
            # (optional optimization - can be removed if needed)

            active_files.append(root_path / file)

    Logger.debug(f"[SSOT_DISCOVERY] Found {len(active_files)} Python files in {project_root}")
    return active_files


def get_files_by_layer(project_root: Path, layer: str, include_tests: bool = False) -> list[Path]:
    """
    Get Python files for a specific L0-L6 layer.

    Args:
        project_root: Root directory of the project
        layer: Layer identifier (L0, L1, L2, L3, L4, L5, L6)
        include_tests: If True, include test files

    Returns:
        List of Path objects for files in the specified layer

    Example:
        >>> l3_files = get_files_by_layer(Path("c:/Git/Agentic-Workflow"), "L3")
        >>> len(l3_files)  # Files in L3_orchestration
        45
    """
    if layer not in LAYER_DIRS:
        Logger.warning(
            f"[SSOT_DISCOVERY] Unknown layer: {layer}. Valid layers: {list(LAYER_DIRS.keys())}"
        )
        return []

    layer_dir = project_root / "agentic_core" / LAYER_DIRS[layer]

    if not layer_dir.exists():
        Logger.warning(f"[SSOT_DISCOVERY] Layer directory not found: {layer_dir}")
        return []

    return get_python_files(layer_dir, include_tests=include_tests)


def get_agent_files(project_root: Path, include_tests: bool = False) -> list[Path]:
    """
    Get all Python files that are likely agent implementations.

    Filters for files ending in 'Agent.py' to focus on agent classes.

    Args:
        project_root: Root directory of the project
        include_tests: If True, include test files

    Returns:
        List of Path objects for agent files
    """
    all_files = get_python_files(project_root, include_tests=include_tests)
    return [f for f in all_files if f.name.endswith("Agent.py")]


def get_mixin_files(project_root: Path, include_tests: bool = False) -> list[Path]:
    """
    Get all Python files that are likely mixin implementations.

    Filters for files containing 'mixin' in the name (case-insensitive).

    Args:
        project_root: Root directory of the project
        include_tests: If True, include test files

    Returns:
        List of Path objects for mixin files
    """
    all_files = get_python_files(project_root, include_tests=include_tests)
    return [f for f in all_files if "mixin" in f.name.lower()]


def get_file_count_by_layer(project_root: Path) -> dict[str, int]:
    """
    Get count of Python files per layer for metrics/dashboard.

    Args:
        project_root: Root directory of the project

    Returns:
        Dict mapping layer name to file count
    """
    counts = {}
    for layer in LAYER_DIRS:
        files = get_files_by_layer(project_root, layer)
        counts[layer] = len(files)
    return counts


@lru_cache(maxsize=1)
def get_cached_python_files(project_root: str) -> tuple:
    """
    Cached version of get_python_files for repeated queries.

    Note: Returns tuple for hashability. Convert to list if needed.

    Args:
        project_root: Root directory as string (for cache key)

    Returns:
        Tuple of Path objects
    """
    return tuple(get_python_files(Path(project_root)))


def invalidate_cache() -> None:
    """Clear the file discovery cache."""
    get_cached_python_files.cache_clear()
    Logger.debug("[SSOT_DISCOVERY] Cache invalidated")


def compare_with_rglob(project_root: Path) -> dict[str, int]:
    """
    Compare SSOT discovery count with raw rglob for verification.

    This is used for TC-3 (Discovery Exhaustiveness) testing.

    Args:
        project_root: Root directory of the project

    Returns:
        Dict with 'ssot_count', 'rglob_count', 'delta'
    """
    # SSOT discovery (excludes backups)
    ssot_files = get_python_files(project_root)
    ssot_count = len(ssot_files)
    ssot_set = {str(f) for f in ssot_files}

    # Raw rglob with identical exclusion logic
    rglob_files = []
    for py_file in project_root.rglob("*.py"):
        str(py_file)

        # Apply same exclusions as SSOT - check each path component
        path_parts = py_file.parts
        skip = False
        for part in path_parts:
            if part in DEFAULT_EXCLUDE_DIRS or part.startswith("."):
                skip = True
                break
        if skip:
            continue

        # Skip test files (same logic as SSOT)
        if py_file.name.startswith("test_") or py_file.name.endswith("_test.py"):
            continue
        if "conftest" in py_file.name:
            continue

        rglob_files.append(py_file)

    rglob_count = len(rglob_files)
    rglob_set = {str(f) for f in rglob_files}

    # Find differences for debugging
    only_in_ssot = ssot_set - rglob_set
    only_in_rglob = rglob_set - ssot_set

    if only_in_ssot or only_in_rglob:
        Logger.debug(f"[SSOT_DISCOVERY] Files only in SSOT: {len(only_in_ssot)}")
        Logger.debug(f"[SSOT_DISCOVERY] Files only in rglob: {len(only_in_rglob)}")

    return {
        "ssot_count": ssot_count,
        "rglob_count": rglob_count,
        "delta": abs(ssot_count - rglob_count),
        "only_in_ssot": list(only_in_ssot)[:5],  # Sample for debugging
        "only_in_rglob": list(only_in_rglob)[:5],
    }


# =============================================================================
# Phase 6: Extended Data File Discovery
# =============================================================================


def get_data_files(
    project_root: Path,
    extensions: list[str] | None = None,
    include_tests: bool = False,
    exclude_dirs: set[str] | None = None,
) -> list[Path]:
    """
    Phase 6: Extended SSOT discovery for non-Python data files.

    Uses the same FileCache mechanism and backup exclusion logic as get_python_files()
    to provide consistent, high-performance discovery for JSON, MD, YAML files.

    Args:
        project_root: Root directory to scan
        extensions: List of file extensions to include (default: [".json", ".md", ".yaml", ".yml"])
        include_tests: If True, include test directories
        exclude_dirs: Additional directories to exclude (merged with defaults)

    Returns:
        List of Path objects for all matching data files

    Example:
        >>> json_files = get_data_files(Path("c:/Git/Agentic-Workflow"), extensions=[".json"])
        >>> len(json_files)  # JSON files excluding backups
        150
    """
    if extensions is None:
        extensions = [".json", ".md", ".yaml", ".yml"]

    # Normalize extensions to include leading dot
    extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

    # Merge default excludes with any additional excludes
    all_excludes = DEFAULT_EXCLUDE_DIRS.copy()
    if exclude_dirs:
        all_excludes.update(exclude_dirs)

    data_files: list[Path] = []

    # Ensure project_root is a Path
    project_root = Path(project_root)

    for root, dirs, files in os.walk(project_root):
        root_path = Path(root)

        # Filter out excluded directories (modifies dirs in-place to prevent traversal)
        dirs[:] = [d for d in dirs if d not in all_excludes and not d.startswith(".")]

        for file in files:
            file_path = root_path / file

            # Check extension
            if file_path.suffix.lower() not in extensions:
                continue

            # Skip test files if not included
            if not include_tests:
                if file.startswith("test_") or file.endswith("_test.json"):
                    continue

            data_files.append(file_path)

    Logger.debug(
        f"[SSOT_DISCOVERY] Found {len(data_files)} data files with extensions {extensions}"
    )
    return data_files


def get_json_files(project_root: Path, include_tests: bool = False) -> list[Path]:
    """
    Convenience function to get all JSON files.

    Args:
        project_root: Root directory to scan
        include_tests: If True, include test directories

    Returns:
        List of Path objects for JSON files
    """
    return get_data_files(project_root, extensions=[".json"], include_tests=include_tests)


def get_markdown_files(project_root: Path, include_tests: bool = False) -> list[Path]:
    """
    Convenience function to get all Markdown files.

    Args:
        project_root: Root directory to scan
        include_tests: If True, include test directories

    Returns:
        List of Path objects for Markdown files
    """
    return get_data_files(project_root, extensions=[".md"], include_tests=include_tests)


def compare_data_files_with_rglob(project_root: Path, extension: str = ".json") -> dict[str, Any]:
    """
    Compare get_data_files() with raw rglob for verification.

    Phase 6: Zero-loss verification for data file discovery.

    Args:
        project_root: Root directory of the project
        extension: File extension to compare

    Returns:
        Dict with 'ssot_count', 'rglob_count', 'delta'
    """
    # SSOT discovery (excludes backups)
    ssot_files = get_data_files(project_root, extensions=[extension])
    ssot_count = len(ssot_files)
    ssot_set = {str(f) for f in ssot_files}

    # Raw rglob with identical exclusion logic
    rglob_files = []
    pattern = f"*{extension}"
    for data_file in project_root.rglob(pattern):
        path_parts = data_file.parts
        skip = False
        for part in path_parts:
            if part in DEFAULT_EXCLUDE_DIRS or part.startswith("."):
                skip = True
                break
        if skip:
            continue
        rglob_files.append(data_file)

    rglob_count = len(rglob_files)
    rglob_set = {str(f) for f in rglob_files}

    only_in_ssot = ssot_set - rglob_set
    only_in_rglob = rglob_set - ssot_set

    return {
        "ssot_count": ssot_count,
        "rglob_count": rglob_count,
        "delta": abs(ssot_count - rglob_count),
        "only_in_ssot": list(only_in_ssot)[:5],
        "only_in_rglob": list(only_in_rglob)[:5],
    }


__all__ = [
    "get_python_files",
    "get_python_files_cached",
    "get_files_by_layer",
    "get_agent_files",
    "get_mixin_files",
    "get_file_count_by_layer",
    "get_cached_python_files",
    "get_global_cache",
    "invalidate_cache",
    "compare_with_rglob",
    "FileCache",
    "DEFAULT_EXCLUDE_DIRS",
    "LAYER_DIRS",
    # Phase 6 additions
    "get_data_files",
    "get_json_files",
    "get_markdown_files",
    "compare_data_files_with_rglob",
]
