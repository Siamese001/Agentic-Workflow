"""Vector Cache Layout SSOT — Canonical paths for L2 semantic cache.

Defines unified cache directory structure for dual-backend (SQLite + ChromaDB)
semantic caching. Eliminates scattered path definitions.

Usage:
    from agentic_core.L4_state.contracts.vector_cache_layout import (
        VECTOR_CACHE_LAYOUT,
        get_sqlite_cache_path,
        get_chroma_cache_path,
    )
    
    layout = VECTOR_CACHE_LAYOUT  # frozen dataclass with all paths
    sqlite_path = get_sqlite_cache_path("artifacts/cache/l2")
    chroma_path = get_chroma_cache_path("artifacts/cache/l2")

Location: agentic_core/L4_state/contracts/vector_cache_layout.py
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VectorCacheLayout:
    """Canonical layout for vector cache storage.
    
    Attributes:
        base_dir: Root directory for all cache files
        sqlite_filename: SQLite database filename
        chroma_subdir: ChromaDB persistent client subdirectory
        default_tenant_id: Default tenant ID for multi-tenancy
        default_corpus_version: Default corpus version
    """
    base_dir: Path
    sqlite_filename: str = "l2_cache.db"
    chroma_subdir: str = "chroma"
    default_tenant_id: str = "default"
    default_corpus_version: str = "v1"
    
    @property
    def sqlite_path(self) -> Path:
        """Full path to SQLite cache database."""
        return self.base_dir / self.sqlite_filename
    
    @property
    def chroma_path(self) -> Path:
        """Full path to ChromaDB persistent storage."""
        return self.base_dir / self.chroma_subdir
    
    def ensure_directories(self) -> None:
        """Create cache directories if they don't exist."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_path.mkdir(parents=True, exist_ok=True)


# Canonical SSOT instance
# Default location: artifacts/cache/l2 (unified with other cache types)
VECTOR_CACHE_LAYOUT = VectorCacheLayout(
    base_dir=Path("artifacts/cache/l2"),
    sqlite_filename="l2_cache.db",
    chroma_subdir="chroma",
)

# Legacy path for backward compatibility
# Old location: artifacts/gptcache (deprecated, will be migrated)
LEGACY_VECTOR_CACHE_LAYOUT = VectorCacheLayout(
    base_dir=Path("artifacts/gptcache"),
    sqlite_filename="l2_cache.db",
    chroma_subdir="chroma",
)


def get_sqlite_cache_path(base_dir: str | Path) -> Path:
    """Get canonical SQLite cache path for a given base directory.
    
    Args:
        base_dir: Base cache directory
        
    Returns:
        Path to SQLite cache file
    """
    return Path(base_dir) / "l2_cache.db"


def get_chroma_cache_path(base_dir: str | Path) -> Path:
    """Get canonical ChromaDB cache path for a given base directory.
    
    Args:
        base_dir: Base cache directory
        
    Returns:
        Path to ChromaDB persistent directory
    """
    return Path(base_dir) / "chroma"


def validate_cache_layout(base_dir: str | Path) -> dict[str, bool]:
    """Validate that cache layout is correct.
    
    Args:
        base_dir: Base cache directory to validate
        
    Returns:
        Dict with validation results
    """
    base = Path(base_dir)
    sqlite_exists = (base / "l2_cache.db").exists()
    chroma_exists = (base / "chroma").exists()
    
    return {
        "base_dir_exists": base.exists(),
        "sqlite_exists": sqlite_exists,
        "chroma_exists": chroma_exists,
        "valid": base.exists() and (sqlite_exists or chroma_exists),
    }


__all__ = [
    "VectorCacheLayout",
    "VECTOR_CACHE_LAYOUT",
    "LEGACY_VECTOR_CACHE_LAYOUT",
    "get_sqlite_cache_path",
    "get_chroma_cache_path",
    "validate_cache_layout",
]
