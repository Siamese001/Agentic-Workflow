import os
import sys
from typing import Any, List, Dict, Optional

def get_existing_filenames() -> Set[str]:
    """Get set of all Python filenames in sovereign codebase."""
    existing = set()
    repo_root = Path(".")

    for root in SOVEREIGN_ROOTS:
        root_path = repo_root / root
        if root_path.exists():
            for py_file in root_path.rglob("*.py"):
                # Store only the filename
                existing.add(py_file.name)

    return existing
