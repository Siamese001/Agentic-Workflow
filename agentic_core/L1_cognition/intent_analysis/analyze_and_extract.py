from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import sys
from typing import Any, List, Dict, Optional
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file
from agentic_core.utils.ssot_discovery import get_python_files, get_data_files

def analyze_and_extract() -> None:
    """Analyze legacy files and extract unique content (Python, JSON, and Markdown)."""
    source_dir: Any = Path('archives/legacy_lic')
    staging_dir: Any = Path('archive_code')
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    existing_hashes: Any = get_existing_file_hashes()
    extracted_files: Any = []
    duplicate_files: Any = []
    unique_content_files: Any = []
    # Phase 6.4: Use ssot_discovery instead of rglob
    all_files: Any = (list(get_python_files(source_dir)) + 
                      list(get_data_files(source_dir, extensions=['.json'])) + 
                      list(get_data_files(source_dir, extensions=['.md'])))
    for file_path in all_files:
        FILENAME: Any = file_path.name
        legacy_hash: Any = get_file_hash(file_path)
        if FILENAME not in existing_hashes:
            dest_path: Any = staging_dir / FILENAME
            shutil.copy2(file_path, dest_path)
            extracted_files.append(FILENAME)
            FILENAME.split('.')[-1].upper()
        elif existing_hashes[FILENAME] != legacy_hash:
            name_parts: Any = FILENAME.rsplit('.', 1)
            new_name: Any = f'{name_parts[0]}_LIC.{name_parts[1]}'
            dest_path: Any = staging_dir / new_name
            shutil.copy2(file_path, dest_path)
            unique_content_files.append((FILENAME, new_name))
            name_parts[1].upper()
        else:
            duplicate_files.append(FILENAME)
    return (extracted_files, unique_content_files, duplicate_files)
