from __future__ import annotations
"""Detailed extraction analysis for legacy_lic archive."""
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple

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
from archives.location_violations.sovereign_index import SovereignIndex
from archives.location_violations.file_utils import safe_read_file, safe_write_file
from agentic_core.utils.ssot_discovery import get_python_files
sovereign_roots: Any = {AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, 'schemas', 'prompt_governance', 'observability', 'config', 'data', ARCHIVES_DIR}

def get_existing_filenames() -> Set[str]:
    """Get set of all Python filenames in sovereign codebase."""
    existing: Any = set()
    repo_root: Any = Path('.')
    for root in sovereign_roots:
        root_path: Any = repo_root / root
        if root_path.exists():
            # Phase 6.4: Use ssot_discovery instead of rglob
            for py_file in get_python_files(root_path):
                existing.add(py_file.name)
    return existing
Logger: Any = logging.getLogger(__name__)

def analyze_legacy_files() -> Tuple[List[str], List[str], List[str]]:
    """Analyze legacy files and categorize them."""
    source_dir: Any = Path('archives/legacy_lic')
    existing_filenames: Any = get_existing_filenames()
    net_incremental: Any = []
    duplicates: Any = []
    all_files: Any = []
    # Phase 6.4: Use ssot_discovery instead of rglob
    for py_file in get_python_files(source_dir):
        filename: Any = py_file.name
        all_files.append(filename)
        if filename in existing_filenames:
            duplicates.append(filename)
        else:
            net_incremental.append(filename)
    return (all_files, net_incremental, duplicates)

def extract_net_incremental() -> None:
    """Extract files that don't exist in sovereign codebase."""
    source_dir: Any = Path('archives/legacy_lic')
    staging_dir: Any = Path('archive_code')
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    existing_filenames: Any = get_existing_filenames()
    extracted_files: Any = []
    # Phase 6.4: Use ssot_discovery instead of rglob
    for py_file in get_python_files(source_dir):
        filename: Any = py_file.name
        if filename not in existing_filenames:
            dest_path: Any = staging_dir / filename
            shutil.copy2(py_file, dest_path)
            extracted_files.append(filename)
    return extracted_files
if __name__ == '__main__':
    all_files, net_incremental, duplicates = analyze_legacy_files()
    if net_incremental:
        for f in sorted(net_incremental):
            pass
        extracted: Any = extract_net_incremental()
    elif duplicates:
        for f in sorted(set(duplicates)):
            pass
