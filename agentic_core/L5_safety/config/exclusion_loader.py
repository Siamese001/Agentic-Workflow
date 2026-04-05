"""Exclusion loader - loads YAML config into Python constants.

SSOT: config/excluded_paths.yaml
This module converts the YAML exclusions into frozensets for runtime use.
"""
from __future__ import annotations

import hashlib
import os
from functools import lru_cache
from pathlib import Path
from typing import Final, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

# YAML import with fallback
try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


# ============================================================================
# PATH CONFIGURATION
# ============================================================================

CONFIG_PATH: Final[Path] = Path(__file__).parent.parent.parent.parent / "config" / "excluded_paths.yaml"


# ============================================================================
# LOADER
# ============================================================================

def _load_yaml_raw() -> dict[str, Any]:
    """Load and parse the YAML configuration file."""
    if yaml is None:
        raise ImportError("PyYAML required: pip install pyyaml")
    
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Exclusion config not found: {CONFIG_PATH}")
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=1)
def _load_exclusions_cached() -> tuple[frozenset[str], frozenset[str], str]:
    """Load exclusions with caching based on file mtime + content hash.
    
    Returns:
        Tuple of (all_excluded_dirs, file_patterns, cache_key)
    """
    data = _load_yaml_raw()
    
    # Collect all directory exclusions
    all_dirs: set[str] = set()
    
    # Category directories
    categories = [
        "build_cache_dirs",
        "version_control_dirs", 
        "virtual_env_dirs",
        "coverage_dirs",
        "archive_dirs",
        "ide_dirs",
        "vendor_dirs",
        "data_dirs",
        "special_dirs",
    ]
    
    for category in categories:
        dirs = data.get(category, [])
        if isinstance(dirs, list):
            all_dirs.update(dirs)
    
    # File patterns
    file_patterns = set(data.get("file_patterns", []))
    
    # Generate cache key from file content
    content = str(sorted(all_dirs)) + str(sorted(file_patterns))
    cache_key = hashlib.md5(content.encode()).hexdigest()[:16]
    
    return frozenset(all_dirs), frozenset(file_patterns), cache_key


def get_excluded_directories() -> frozenset[str]:
    """Get all excluded directory names from YAML config.
    
    Returns:
        Frozenset of directory names that should be excluded from scanning.
    """
    dirs, _, _ = _load_exclusions_cached()
    return dirs


def get_excluded_file_patterns() -> frozenset[str]:
    """Get all excluded file patterns from YAML config.
    
    Returns:
        Frozenset of glob patterns for files to exclude.
    """
    _, patterns, _ = _load_exclusions_cached()
    return patterns


# ============================================================================
# LEGACY COMPATIBILITY EXPORTS
# ============================================================================

# Load at module import time for compatibility with existing code
# This ensures constants are available like: from exclusion_loader import EXCLUDED_DIRS

try:
    _dirs, _patterns, _cache_key = _load_exclusions_cached()
except (FileNotFoundError, ImportError) as e:
    # Fallback to minimal set if YAML not available
    _dirs = frozenset({
        ".git", "__pycache__", ".pytest_cache", ".venv", "venv",
        "node_modules", "build", "dist", "coverage_html", ".test_artifacts",
    })
    _patterns = frozenset({"*.pyc", "*.pyo"})
    _cache_key = "fallback"

EXCLUDED_DIRS: Final[frozenset[str]] = _dirs
EXCLUDED_FILE_PATTERNS: Final[frozenset[str]] = _patterns
LOADER_CACHE_KEY: Final[str] = _cache_key


# ============================================================================
# SYNC VERIFICATION
# ============================================================================

def verify_against_ssot(ssot_frozenset: frozenset[str]) -> dict[str, Any]:
    """Verify YAML exclusions against ssot.py SOVEREIGN_EXCLUDED_FOLDERS.
    
    Returns dict with:
        - in_yaml_not_ssot: entries in YAML but missing from ssot
        - in_ssot_not_yaml: entries in ssot but missing from YAML
        - yaml_only: entries unique to YAML (candidates for ssot addition)
        - ssot_only: entries unique to ssot (legacy or intentional)
        - sync_percentage: how closely they match (0-100)
    """
    yaml_dirs = get_excluded_directories()
    
    in_yaml_not_ssot = yaml_dirs - ssot_frozenset
    in_ssot_not_yaml = ssot_frozenset - yaml_dirs
    
    if yaml_dirs:
        sync_percentage = len(yaml_dirs & ssot_frozenset) / len(yaml_dirs) * 100
    else:
        sync_percentage = 0.0
    
    return {
        "in_yaml_not_ssot": sorted(in_yaml_not_ssot),
        "in_ssot_not_yaml": sorted(in_ssot_not_yaml),
        "yaml_only": sorted(in_yaml_not_ssot),
        "ssot_only": sorted(in_ssot_not_yaml),
        "sync_percentage": round(sync_percentage, 2),
        "yaml_count": len(yaml_dirs),
        "ssot_count": len(ssot_frozenset),
    }


if __name__ == "__main__":
    # Self-test when run directly
    print(f"EXCLUDED_DIRS ({len(EXCLUDED_DIRS)} entries):")
    for d in sorted(EXCLUDED_DIRS)[:10]:
        print(f"  - {d}")
    if len(EXCLUDED_DIRS) > 10:
        print(f"  ... and {len(EXCLUDED_DIRS) - 10} more")
    
    print(f"\nEXCLUDED_FILE_PATTERNS ({len(EXCLUDED_FILE_PATTERNS)} entries):")
    for p in sorted(EXCLUDED_FILE_PATTERNS):
        print(f"  - {p}")
    
    print(f"\nCache key: {LOADER_CACHE_KEY}")
