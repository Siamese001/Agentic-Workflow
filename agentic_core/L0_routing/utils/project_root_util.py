"""
SSOT for robust project root detection.

This module replaces all the fragile `../../..` path hacks and provides
a single, reliable way to find the project root directory.

SSOT Consolidation (Jan 20, 2026):
All scripts should import get_project_root from here instead of
computing paths manually.
"""

from functools import lru_cache
from pathlib import Path
from typing import Final

# Markers that indicate the root of the project
ROOT_MARKERS: list[str] = [
    "pyproject.toml",
    ".git",
    AGENTIC_CORE_DIR,  # The core package directory itself
    "requirements.txt",
]


@lru_cache(maxsize=1)
def get_project_root(start_path: str | None = None) -> Path:
    """
    Detect the project root directory by searching upward for markers.

    Args:
        start_path: The path to start searching from. Defaults to CWD.

    Returns:
        Path: The absolute path to the project root.

    Raises:
        RuntimeError: If the project root cannot be found after searching 10 levels up.
    """
    current = Path(start_path).resolve() if start_path else Path.cwd().resolve()

    # Safety: If we are in a file (not dir), start from its parent
    if current.is_file():
        current = current.parent

    # Traverse up to 10 levels
    for _ in range(10):
        # Check for markers
        for marker in ROOT_MARKERS:
            if (current / marker).exists():
                return current

        # Stop if we hit the filesystem root
        if current.parent == current:
            break

        current = current.parent

    # Fallback: If we are inside the 'agentic_core' package structure,
    # we might be deep inside. Try to find the 'agentic_core' folder specifically.
    # (This handles cases where markers are missing but structure is intact)
    try:
        current = Path(start_path).resolve() if start_path else Path.cwd().resolve()
        parts = current.parts
        if AGENTIC_CORE_DIR in parts:
            # Find the index of agentic_core and take the parent of that
            idx = parts.index("agentic_core")
            # If agentic_core is at root/agentic_core, the root is parts[:idx]
            return Path(*parts[:idx])
    # guardian: allow-silent-swallow
    except Exception:
        pass

    raise RuntimeError(
        f"Could not detect project root. Searched 10 levels up from {start_path or Path.cwd()}",
    )


def clear_project_root_cache() -> None:
    """Clear the cached project root. Useful for testing."""
    get_project_root.cache_clear()


PROJECT_ROOT_MARKERS: Final[frozenset[str]] = frozenset(
    {
        "pyproject.toml",
        "canon_validator_agentic_v2_thin.py",
        AGENTIC_CORE_DIR,
        ".git",
    },
)


def get_validated_project_root() -> Path:
    """Get the validated project root by searching upward from this file.

    Compatibility alias — delegates to get_project_root().
    """
    return get_project_root(str(Path(__file__)))


__all__ = [
    "get_project_root",
    "get_validated_project_root",
    "clear_project_root_cache",
    "ROOT_MARKERS",
    "PROJECT_ROOT_MARKERS",
]
