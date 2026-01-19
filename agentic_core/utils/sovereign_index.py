"""
SovereignIndex - Cached File Indexer to Replace rglob Calls

This module provides a singleton file indexer that caches filesystem scans,
dramatically reducing the performance impact of repeated rglob calls.

USAGE:
    from agentic_core.utils.sovereign_index import SovereignIndex
    
    # Get the singleton instance
    index = SovereignIndex.get_instance(project_root)
    
    # Get files matching a pattern
    python_files = index.get_files("*.py")
    agent_files = index.get_files("*Agent.py")
    
    # Force refresh if needed
    index.refresh()

PERFORMANCE:
    - Initial scan: O(n) where n = number of files
    - Subsequent queries: O(1) from cache
    - Auto-invalidation: Checks mtime of project root

SSOT PRINCIPLE:
    All file discovery should use SovereignIndex instead of direct rglob calls.
    This ensures consistent exclusion patterns and optimal performance.
"""
from __future__ import annotations

import fnmatch
import logging
import os
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

Logger = logging.getLogger(__name__)


class SovereignIndex:
    """
    Singleton file indexer with caching and auto-invalidation.
    
    This class replaces ad-hoc rglob calls with a centralized,
    cached file index that automatically invalidates when the
    filesystem changes.
    
    Features:
    1. Singleton pattern ensures single source of truth
    2. In-memory cache for fast repeated queries
    3. mtime-based invalidation for external changes
    4. Thread-safe operations
    5. Configurable exclusion patterns
    """
    
    _instance: Optional[SovereignIndex] = None
    _lock: threading.Lock = threading.Lock()
    
    # Default exclusion patterns - imported from SSOT blueprint
    # PRODUCTION LENS: Excludes test directories to focus on production code
    try:
        from agentic_core.L5_safety.validators.structure_blueprint import GLOBAL_EXCLUDED_DIRS
        DEFAULT_EXCLUDED_DIRS: Set[str] = set(GLOBAL_EXCLUDED_DIRS)
    except ImportError:
        # Fallback if blueprint not available during initialization
        DEFAULT_EXCLUDED_DIRS: Set[str] = {
            '__pycache__', '.pytest_cache', 'build', 'dist', '.eggs',
            '.git', '.svn', '.hg',
            '.venv', 'venv', 'env', '.env', 'node_modules',
            'coverage_html', 'htmlcov', '.coverage',
            'archives', '.sovereign_healing_backup', 'reports',
            'tests',  # Production Lens - exclude test files from healing scans
        }
    
    def __init__(self, project_root: Path) -> None:
        """
        Initialize the SovereignIndex.
        
        Note: Use get_instance() instead of direct instantiation
        to ensure singleton behavior.
        
        Args:
            project_root: Root directory to index
        """
        self._project_root = Path(project_root).resolve()
        self._cache: Dict[str, List[Path]] = {}
        self._all_files: List[Path] = []
        self._last_scan_time: float = 0.0
        self._root_mtime: float = 0.0
        self._excluded_dirs: Set[str] = self.DEFAULT_EXCLUDED_DIRS.copy()
        self._initialized: bool = False
        self._scan_lock: threading.Lock = threading.Lock()
        
        Logger.debug(f"[INDEX] SovereignIndex created for {self._project_root}")
    
    @classmethod
    def get_instance(cls, project_root: Optional[Path] = None) -> SovereignIndex:
        """
        Get the singleton instance of SovereignIndex.
        
        Args:
            project_root: Root directory to index (required on first call)
            
        Returns:
            The singleton SovereignIndex instance
            
        Raises:
            ValueError: If project_root is not provided on first call
        """
        with cls._lock:
            if cls._instance is None:
                if project_root is None:
                    raise ValueError("project_root is required on first call to get_instance()")
                cls._instance = cls(project_root)
            elif project_root is not None:
                # Verify same project root
                resolved = Path(project_root).resolve()
                if resolved != cls._instance._project_root:
                    Logger.warning(
                        f"[INDEX] Project root mismatch: {resolved} vs {cls._instance._project_root}. "
                        "Creating new instance."
                    )
                    cls._instance = cls(project_root)
            return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance.
        
        This is primarily for testing purposes.
        """
        with cls._lock:
            cls._instance = None
    
    def get_files(self, pattern: str = "*") -> List[Path]:
        """
        Get files matching a glob pattern.
        
        Args:
            pattern: Glob pattern to match (e.g., "*.py", "*Agent.py")
            
        Returns:
            List of Path objects matching the pattern
            
        Example:
            python_files = index.get_files("*.py")
            agent_files = index.get_files("*Agent.py")
        """
        # Ensure index is fresh
        self._ensure_fresh()
        
        # Check cache first
        if pattern in self._cache:
            return self._cache[pattern].copy()
        
        # Filter files by pattern
        matched = []
        for file_path in self._all_files:
            if fnmatch.fnmatch(file_path.name, pattern):
                matched.append(file_path)
        
        # Cache the result
        self._cache[pattern] = matched
        
        Logger.debug(f"[INDEX] Pattern '{pattern}' matched {len(matched)} files")
        return matched.copy()
    
    def get_python_files(self) -> List[Path]:
        """
        Get all Python files in the index.
        
        Convenience method equivalent to get_files("*.py").
        
        Returns:
            List of all .py files
        """
        return self.get_files("*.py")
    
    def get_agent_files(self) -> List[Path]:
        """
        Get all agent files in the index.
        
        Returns:
            List of files matching *Agent.py pattern
        """
        return self.get_files("*Agent.py")
    
    def file_exists(self, relative_path: str) -> bool:
        """
        Check if a file exists in the index.
        
        Args:
            relative_path: Path relative to project root
            
        Returns:
            True if file exists in index
        """
        self._ensure_fresh()
        full_path = self._project_root / relative_path
        return full_path in self._all_files
    
    def refresh(self) -> int:
        """
        Force a refresh of the file index.
        
        Returns:
            Number of files indexed
        """
        with self._scan_lock:
            return self._scan_filesystem()
    
    def invalidate(self) -> None:
        """
        Invalidate the cache without rescanning.
        
        The next get_files() call will trigger a rescan.
        """
        self._cache.clear()
        self._initialized = False
        Logger.debug("[INDEX] Cache invalidated")
    
    def add_exclusion(self, dir_name: str) -> None:
        """
        Add a directory to the exclusion list.
        
        Args:
            dir_name: Directory name to exclude
        """
        self._excluded_dirs.add(dir_name)
        self.invalidate()
    
    def remove_exclusion(self, dir_name: str) -> None:
        """
        Remove a directory from the exclusion list.
        
        Args:
            dir_name: Directory name to stop excluding
        """
        self._excluded_dirs.discard(dir_name)
        self.invalidate()
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            "project_root": str(self._project_root),
            "total_files": len(self._all_files),
            "cached_patterns": len(self._cache),
            "last_scan_time": self._last_scan_time,
            "excluded_dirs": list(self._excluded_dirs),
            "initialized": self._initialized,
        }
    
    def _ensure_fresh(self) -> None:
        """
        Ensure the index is fresh, rescanning if needed.
        
        Auto-invalidation is based on:
        1. Index not initialized
        2. Project root mtime changed
        """
        if not self._initialized:
            self.refresh()
            return
        
        # Check if project root mtime changed
        try:
            current_mtime = os.path.getmtime(self._project_root)
            if current_mtime != self._root_mtime:
                Logger.debug("[INDEX] Project root mtime changed, refreshing")
                self.refresh()
        except OSError:
            # If we can't check mtime, assume cache is valid
            pass
    
    def _scan_filesystem(self) -> int:
        """
        Scan the filesystem and populate the index.
        
        Uses os.scandir for better performance than pathlib.rglob.
        
        Returns:
            Number of files indexed
        """
        start_time = time.time()
        self._all_files.clear()
        self._cache.clear()
        
        try:
            self._root_mtime = os.path.getmtime(self._project_root)
        except OSError:
            self._root_mtime = 0.0
        
        # Use os.scandir for performance
        self._scan_directory(self._project_root)
        
        self._last_scan_time = time.time() - start_time
        self._initialized = True
        
        Logger.info(
            f"[INDEX] Scanned {len(self._all_files)} files in {self._last_scan_time:.2f}s"
        )
        
        return len(self._all_files)
    
    def _scan_directory(self, directory: Path) -> None:
        """
        Recursively scan a directory using os.scandir.
        
        Args:
            directory: Directory to scan
        """
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            # Skip excluded directories
                            if entry.name in self._excluded_dirs:
                                continue
                            # Skip hidden directories (except .git which is already excluded)
                            if entry.name.startswith('.') and entry.name not in self._excluded_dirs:
                                continue
                            # Recurse into subdirectory
                            self._scan_directory(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            self._all_files.append(Path(entry.path))
                    except (PermissionError, OSError):
                        # Skip files/dirs we can't access
                        continue
        except (PermissionError, OSError) as e:
            Logger.debug(f"[INDEX] Cannot scan {directory}: {e}")


__all__ = [
    "SovereignIndex",
]
