from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import sys
from typing import Any, List, Dict, Optional
from agentic_core.utils.sovereign_index import SovereignIndex

def extract_net_incremental() -> None:
    """Extract files that don't exist in sovereign codebase."""
    source_dir: Any = Path('archives/legacy_lic')
    staging_dir: Any = Path('archive_code')
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    existing_files: Any = get_existing_files()
    extracted_files: Any = []
    for py_file in source_dir.rglob('*.py'):
        if '__pycache__' in py_file.parts or '.git' in py_file.parts:
            continue
        FILENAME: Any = py_file.name
        name_exists: Any = any((FILENAME in existing for existing in existing_files))
        if not name_exists:
            dest_path: Any = staging_dir / FILENAME
            shutil.copy2(py_file, dest_path)
            extracted_files.append(FILENAME)
    return extracted_files
