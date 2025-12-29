import os
import sys
from typing import Any, List, Dict, Optional

def get_existing_files() -> Set[str]:
    """Get set of all Python files in sovereign codebase."""
    existing = set()
    repo_root = Path(".")

    for root in SOVEREIGN_ROOTS:
        root_path = repo_root / root
        if root_path.exists():
            for py_file in root_path.rglob("*.py"):
                # Store relative path from repo root
                rel_path = py_file.relative_to(repo_root)
                existing.add(str(rel_path))

    return existing
