from __future__ import annotations
"""
Canon Validator Configuration
Defines exclusion zones and constants for validation.
"""
import os
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
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
excluded_dirs: Any = {'.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', 'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs', ARCHIVES_DIR, 'data'}
excluded_files: Any = {'CanonValidatorAgent.py', 'canon_validator_backup.py', 'canon_validator_v2_agentic.py', 'auto_canon.py', '.DS_Store'}
max_healing_per_file: Any = int(os.getenv('MAX_HEALING_PER_FILE', '8'))
global_healing_budget: Any = int(os.getenv('GLOBAL_HEALING_BUDGET', '50'))

def is_excluded(path: str) -> bool:
    """Check if a path should be excluded from validation."""
    path_parts: Any = path.split(os.sep)
    for part in path_parts:
        if part in EXCLUDED_DIRS:
            return True
    filename: Any = os.path.basename(path)
    if filename in EXCLUDED_FILES:
        return True
    return False
