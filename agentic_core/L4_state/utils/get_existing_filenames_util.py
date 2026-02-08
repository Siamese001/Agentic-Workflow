from __future__ import annotations

from pathlib import Path

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from typing import Any


def get_existing_filenames() -> Set[str]:
    """Get set of all Python filenames in sovereign codebase."""
    existing: Any = set()
    repo_root: Any = Path(".")
    for root in SOVEREIGN_ROOTS:
        root_path: Any = repo_root / root
        if root_path.exists():
            # Final True 20: Use ssot_discovery instead of rglob
            from agentic_core.utils.ssot_discovery_validator import get_python_files

            for py_file in get_python_files(root_path):
                existing.add(py_file.name)
    return existing
