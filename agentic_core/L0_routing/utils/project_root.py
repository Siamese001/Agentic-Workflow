"""
L0 Project Root Utilities.

Provides get_validated_project_root() without importing L5 at module level.
This eliminates upward import violations from L0 scripts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

PROJECT_ROOT_MARKERS: Final[frozenset[str]] = frozenset(
    {
        "pyproject.toml",
        "canon_validator_agentic_v2_thin.py",
        "agentic_core",
        ".git",
    },
)


def get_validated_project_root() -> Path:
    """Get the validated project root by searching upward from this file."""
    current = Path(__file__).resolve()

    for parent in [current, *list(current.parents)]:
        markers_found = sum(1 for marker in PROJECT_ROOT_MARKERS if (parent / marker).exists())
        if markers_found >= 2:
            return parent

    raise ValueError(f"Could not find valid project root from {__file__}")
