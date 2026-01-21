from __future__ import annotations

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from typing import Any


def analyze_legacy_files() -> Tuple[list[str], list[str], list[str]]:
    """Analyze legacy files and categorize them."""
    source_dir: Any = Path("archives/legacy_lic")
    existing_filenames: Any = get_existing_filenames()
    net_incremental: Any = []
    duplicates: Any = []
    all_files: Any = []
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files

    for py_file in get_python_files(source_dir):
        filename: Any = py_file.name
        all_files.append(filename)
        if filename in existing_filenames:
            duplicates.append(filename)
        else:
            net_incremental.append(filename)
    return (all_files, net_incremental, duplicates)
