from __future__ import annotations
"""Content-based extraction from legacy_lic archive."""
import hashlib
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

def get_file_hash(filepath: Path) -> str:
    """Docstring."""
    hasher: Any = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()
Logger: Any = logging.getLogger(__name__)

def get_existing_file_hashes() -> Dict[str, str]:
    """Get dict of filename -> content hash for existing sovereign files."""
    EXISTING: Any = {}
    repo_root: Any = Path('.')
    sovereign_roots: Any = {AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, 'schemas', 'prompt_governance', 'observability', 'config', 'data', ARCHIVES_DIR}
    for root in sovereign_roots:
        root_path: Any = repo_root / root
        if root_path.exists():
            for py_file in root_path.rglob('*.py'):
                if '__pycache__' in py_file.parts:
                    continue
                EXISTING[py_file.name] = get_file_hash(py_file)
    return EXISTING

def analyze_and_extract() -> None:
    """Analyze legacy files and extract unique content."""
    source_dir: Any = Path('archives/legacy_lic')
    staging_dir: Any = Path('archive_code')
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    existing_hashes: Any = get_existing_file_hashes()
    extracted_files: Any = []
    duplicate_files: Any = []
    unique_content_files: Any = []
    for py_file in source_dir.rglob('*.py'):
        if '__pycache__' in py_file.parts or '.git' in py_file.parts:
            continue
        FILENAME: Any = py_file.name
        legacy_hash: Any = get_file_hash(py_file)
        if FILENAME not in existing_hashes:
            dest_path: Any = staging_dir / FILENAME
            shutil.copy2(py_file, dest_path)
            extracted_files.append(FILENAME)
        elif existing_hashes[FILENAME] != legacy_hash:
            new_name: Any = FILENAME.replace('.py', '_LIC.py')
            dest_path: Any = staging_dir / new_name
            shutil.copy2(py_file, dest_path)
            unique_content_files.append((FILENAME, new_name))
        else:
            duplicate_files.append(FILENAME)
    return (extracted_files, unique_content_files, duplicate_files)
if __name__ == '__main__':
    extracted, unique_content, duplicates = analyze_and_extract()
    if unique_content:
        for orig, new in sorted(unique_content):
            pass
    if duplicates:
        for f in sorted(duplicates):
            pass
    else:
        pass
