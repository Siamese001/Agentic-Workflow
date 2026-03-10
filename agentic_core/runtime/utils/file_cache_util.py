#!/usr/bin/env python3
from __future__ import annotations

"""
FileCache: Singleton-based file discovery cache for reducing I/O overhead.

This module provides a centralized, cached file discovery mechanism to eliminate
redundant rglob/glob calls across the codebase. All agents should use this cache
instead of direct path.rglob() calls.

Opportunity #3: rglob Scan Proliferation
- Consolidates 100+ redundant rglob calls into single cached SSOT
- Lazy loading: only scans disk on first request
- Built-in filtering for *.py and *.md extensions
- Automatic exclusion of .git, __pycache__, .sovereign_healing_backup
- Invalidation method for healer agents that modify files
- Uses os.walk with directory pruning for performance (not rglob)

Usage:

    cache = FileCache.get_instance()
    all_py_files = cache.get_files_by_extension('.py')
    all_files = cache.get_all_files()

    # After file modifications (healers):
    cache.invalidate()
"""


import logging
import os
import threading
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

Logger = logging.getLogger(__name__)


class FileCache:
    """
    Singleton file discovery cache.

    Thread-safe implementation using double-checked locking pattern.
    Provides lazy-loaded, filtered file discovery with automatic exclusions.
    Uses os.walk with directory pruning for performance.
    """

    _instance: FileCache | None = None
    _lock: threading.Lock = threading.Lock()

    # Directories to exclude from all scans (pruned during os.walk)
    EXCLUDED_DIRS: frozenset[str] = SOVEREIGN_EXCLUDED_FOLDERS

    def __init__(self, project_root: Path | None = None):
        """
        Initialize the cache. Should not be called directly - use get_instance().

        Args:
            project_root: Root directory for file discovery. Auto-detected if None.
        """
        self._project_root = project_root or self._detect_project_root()
        self._files: dict[str, list[Path]] = {}
        self._scan_count: int = 0
        self._is_populated: bool = False
        self._cache_lock: threading.Lock = threading.Lock()

    @classmethod
    def get_instance(cls, project_root: Path | None = None) -> FileCache:
        """
        Get the singleton instance of FileCache.

        Thread-safe using double-checked locking.

        Args:
            project_root: Optional project root (only used on first call)

        Returns:
            The singleton FileCache instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(project_root)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance. Useful for testing.
        """
        with cls._lock:
            cls._instance = None

    def _detect_project_root(self) -> Path:
        """Auto-detect project root by looking for key markers."""
        current = Path(__file__).resolve()

        # Walk up looking for project markers
        for parent in [current] + list(current.parents):
            if (parent / AGENTIC_CORE_DIR).is_dir() and (parent / "tests").is_dir():
                return parent
            if (parent / "pyproject.toml").exists():
                return parent
            if (parent / ".git").is_dir():
                return parent

        # Fallback to parent of agentic_core
        return Path(__file__).resolve().parent.parent.parent

    def _scan(self) -> None:
        """
        Scan the directory using os.walk with directory pruning.

        This is significantly faster than rglob because we prune excluded
        directories in-place, preventing descent into .git, __pycache__, etc.
        """
        Logger.debug(f"[FileCache] Scanning files from {self._project_root}")
        self._scan_count += 1

        new_files: dict[str, list[Path]] = {
            "all": [],
            "python": [],
            "markdown": [],
        }

        try:
            for root, dirs, files in os.walk(self._project_root):
                # Prune excluded directories in-place (CRITICAL for performance)
                # This prevents os.walk from descending into .git, __pycache__, etc.
                dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS and not d.endswith(".egg-info")]

                for file in files:
                    file_path = Path(root) / file
                    new_files["all"].append(file_path)

                    suffix = file_path.suffix.lower()
                    if suffix == ".py" or suffix == ".pyi":
                        new_files["python"].append(file_path)
                    elif suffix in {".md", ".markdown"}:
                        new_files["markdown"].append(file_path)

        except PermissionError as e:
            Logger.warning(f"[FileCache] Permission error during scan: {e}")
        except Exception as e:
            Logger.error(f"[FileCache] Error during scan: {e}")

        self._files = new_files
        self._is_populated = True
        Logger.debug(f"[FileCache] Scan complete: {len(new_files['all'])} files found")

    def get_all_files(self) -> list[Path]:
        """
        Get all files in the project (lazy-loaded).

        Returns:
            List of all file paths (excluding filtered directories)
        """
        with self._cache_lock:
            if not self._is_populated:
                self._scan()
            return self._files.get("all", []).copy()

    def get_files_by_extension(self, ext: str) -> list[Path]:
        """
        Get files filtered by extension (lazy-loaded).

        Args:
            ext: File extension including dot (e.g., '.py', '.md')

        Returns:
            List of file paths with the specified extension
        """
        # Normalize extension
        if not ext.startswith("."):
            ext = f".{ext}"
        ext = ext.lower()

        with self._cache_lock:
            if not self._is_populated:
                self._scan()

            # Return from pre-computed categories if available
            if ext in {".py", ".pyi"}:
                return [f for f in self._files.get("python", []) if f.suffix.lower() == ext]
            elif ext in {".md", ".markdown"}:
                return [f for f in self._files.get("markdown", []) if f.suffix.lower() == ext]

            # Filter from all files for other extensions
            return [f for f in self._files.get("all", []) if f.suffix.lower() == ext]

    def get_python_files(self) -> list[Path]:
        """
        Get all Python files (.py, .pyi).

        Returns:
            List of Python file paths
        """
        with self._cache_lock:
            if not self._is_populated:
                self._scan()
            return self._files.get("python", []).copy()

    def get_markdown_files(self) -> list[Path]:
        """
        Get all Markdown files (.md, .markdown).

        Returns:
            List of Markdown file paths
        """
        with self._cache_lock:
            if not self._is_populated:
                self._scan()
            return self._files.get("markdown", []).copy()

    def invalidate(self) -> None:
        """
        Invalidate the cache, forcing a re-scan on next access.

        Should be called by healer agents after modifying files.
        """
        with self._cache_lock:
            self._files = {}
            self._is_populated = False
            Logger.debug("[FileCache] cache invalidated")

    def get_scan_count(self) -> int:
        """
        Get the number of times the cache has scanned the filesystem.

        Useful for verifying cache effectiveness.

        Returns:
            Number of scans performed
        """
        return self._scan_count

    @property
    def project_root(self) -> Path:
        """Get the project root path."""
        return self._project_root

    def is_cached(self) -> bool:
        """Check if the cache has been populated."""
        return self._is_populated


# Convenience functions for common use cases
def get_python_files(project_root: Path | None = None) -> list[Path]:
    """
    Convenience function to get all Python files.

    Args:
        project_root: Optional project root (uses default if None)

    Returns:
        List of Python file paths
    """
    cache = FileCache.get_instance(project_root)
    return cache.get_python_files()


def get_all_files(project_root: Path | None = None) -> list[Path]:
    """
    Convenience function to get all files.

    Args:
        project_root: Optional project root (uses default if None)

    Returns:
        List of all file paths
    """
    cache = FileCache.get_instance(project_root)
    return cache.get_all_files()


def invalidate_cache() -> None:
    """
    Convenience function to invalidate the file cache.

    Should be called after file modifications.
    """
    if FileCache._instance is not None:
        FileCache._instance.invalidate()


__all__ = [
    "FileCache",
    "get_python_files",
    "get_all_files",
    "invalidate_cache",
]
