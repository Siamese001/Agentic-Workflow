from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import sys
from typing import Any, List, Dict, Optional

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
