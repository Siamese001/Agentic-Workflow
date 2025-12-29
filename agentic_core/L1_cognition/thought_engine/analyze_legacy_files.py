import os
import sys
from typing import Any, List, Dict, Optional

def analyze_legacy_files() -> Tuple[List[str], List[str], List[str]]:
    """Analyze legacy files and categorize them."""
    source_dir = Path("archives/legacy_lic")
    existing_filenames = get_existing_filenames()

    net_incremental = []
    duplicates = []
    all_files = []

    # Scan all Python files in legacy_lic
    for py_file in source_dir.rglob("*.py"):
        if "__pycache__" in py_file.parts or ".git" in py_file.parts:
            continue

        filename = py_file.name
        all_files.append(filename)

        if filename in existing_filenames:
            duplicates.append(filename)
        else:
            net_incremental.append(filename)

    return all_files, net_incremental, duplicates
