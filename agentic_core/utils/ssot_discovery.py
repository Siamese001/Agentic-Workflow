"""
SSOT Discovery Module - Phase 1 Foundation

High-performance, centralized file discovery utility that excludes backup bloat
and focuses on active code. This replaces scattered rglob/glob usage across the codebase.

Key Features:
- Excludes .sovereign_healing_backup/ (10k+ files) and archives/
- Excludes __pycache__, .git, and other non-essential directories
- Optional test file inclusion
- Layer-specific file discovery
- Cached results for repeated queries

Usage:
    from agentic_core.utils.ssot_discovery import get_python_files, get_files_by_layer
    
    # Get all active Python files
    files = get_python_files(project_root)
    
    # Get files for a specific layer
    l3_files = get_files_by_layer(project_root, "L3")

Author: Cascade
Date: January 19, 2026
Phase: 1 - Foundation & Zero-Loss Protocols
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from functools import lru_cache
import logging

Logger = logging.getLogger(__name__)

# Default directories to exclude from all scans
# These directories contain backup bloat or non-essential files
DEFAULT_EXCLUDE_DIRS: Set[str] = {
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
LAYER_DIRS: Dict[str, str] = {
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
    exclude_dirs: Optional[Set[str]] = None,
    include_dirs: Optional[Set[str]] = None
) -> List[Path]:
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
    
    active_files: List[Path] = []
    
    # Ensure project_root is a Path
    project_root = Path(project_root)
    
    for root, dirs, files in os.walk(project_root):
        root_path = Path(root)
        
        # Filter out excluded directories (modifies dirs in-place to prevent traversal)
        dirs[:] = [d for d in dirs if d not in all_excludes and not d.startswith('.')]
        
        # If include_dirs specified, filter to only those
        if include_dirs:
            dirs[:] = [d for d in dirs if d in include_dirs or any(
                str(root_path / d).endswith(inc) for inc in include_dirs
            )]
        
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


def get_files_by_layer(
    project_root: Path,
    layer: str,
    include_tests: bool = False
) -> List[Path]:
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
        Logger.warning(f"[SSOT_DISCOVERY] Unknown layer: {layer}. Valid layers: {list(LAYER_DIRS.keys())}")
        return []
    
    layer_dir = project_root / "agentic_core" / LAYER_DIRS[layer]
    
    if not layer_dir.exists():
        Logger.warning(f"[SSOT_DISCOVERY] Layer directory not found: {layer_dir}")
        return []
    
    return get_python_files(layer_dir, include_tests=include_tests)


def get_agent_files(
    project_root: Path,
    include_tests: bool = False
) -> List[Path]:
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


def get_mixin_files(
    project_root: Path,
    include_tests: bool = False
) -> List[Path]:
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


def get_file_count_by_layer(project_root: Path) -> Dict[str, int]:
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


def compare_with_rglob(project_root: Path) -> Dict[str, int]:
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
    ssot_set = set(str(f) for f in ssot_files)
    
    # Raw rglob with identical exclusion logic
    rglob_files = []
    for py_file in project_root.rglob("*.py"):
        path_str = str(py_file)
        
        # Apply same exclusions as SSOT - check each path component
        path_parts = py_file.parts
        skip = False
        for part in path_parts:
            if part in DEFAULT_EXCLUDE_DIRS or part.startswith('.'):
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
    rglob_set = set(str(f) for f in rglob_files)
    
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
        "only_in_rglob": list(only_in_rglob)[:5]
    }


__all__ = [
    "get_python_files",
    "get_files_by_layer",
    "get_agent_files",
    "get_mixin_files",
    "get_file_count_by_layer",
    "get_cached_python_files",
    "invalidate_cache",
    "compare_with_rglob",
    "DEFAULT_EXCLUDE_DIRS",
    "LAYER_DIRS",
]
