from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import sys
from typing import Any, List, Dict, Optional
from agentic_core.utils.sovereign_index import SovereignIndex

def get_existing_filenames() -> Set[str]:
    """Get set of all Python filenames in sovereign codebase."""
    existing: Any = set()
    repo_root: Any = Path('.')
    for root in SOVEREIGN_ROOTS:
        root_path: Any = repo_root / root
        if root_path.exists():
            # Final True 20: Use ssot_discovery instead of rglob
            from agentic_core.utils.ssot_discovery import get_python_files
            for py_file in get_python_files(root_path):
                existing.add(py_file.name)
    return existing
