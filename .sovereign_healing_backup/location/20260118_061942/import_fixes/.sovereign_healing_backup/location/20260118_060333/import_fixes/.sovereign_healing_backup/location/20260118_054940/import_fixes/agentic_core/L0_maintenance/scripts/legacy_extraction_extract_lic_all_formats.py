from __future__ import annotations
"""Extract net incremental files (Python,
    JSON,
    and Markdown) from legacy_lic archive to staging directory."""
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

def get_file_hash(filepath: Path) -> str:
    """Docstring."""
    HASHER: Any = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            HASHER.update(chunk)
    return HASHER.hexdigest()

def get_existing_file_hashes() -> Dict[str, str]:
    """Get dict of filename -> content hash for existing sovereign files."""
    existing: Any = {}
    repo_root: Any = Path('.')
    sovereign_roots: Any = {AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, 'schemas', 'prompt_governance', 'observability', 'config', 'data', ARCHIVES_DIR, 'docs'}
    for root in sovereign_roots:
        root_path: Any = repo_root / root
        if root_path.exists():
            for file_path in root_path.rglob('*.py'):
                if '__pycache__' in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in root_path.rglob('*.json'):
                if '__pycache__' in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in root_path.rglob('*.md'):
                if '__pycache__' in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)
    return existing

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
    all_files: Any = list(source_dir.rglob('*.py')) + list(source_dir.rglob('*.json')) + list(source_dir.rglob('*.md'))
    for file_path in all_files:
        if '__pycache__' in file_path.parts or '.git' in file_path.parts:
            continue
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
if __name__ == '__main__':
    extracted, unique_content, duplicates = analyze_and_extract()
    if extracted:
        for f in sorted(extracted):
            pass
    if unique_content:
        for orig, new in sorted(unique_content):
            pass
