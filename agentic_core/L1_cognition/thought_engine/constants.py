"""
Sovereign domain constants - Re-exported from canonical location.
This module provides waterfall-compliant access to shared constants.
[SSOT] All structural constants derived from structure_blueprint.py
"""

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    ROOT_WHITELIST,
    ROOT_PROTECTED_FILES,
    SOVEREIGN_REGISTRY,
)

# [SSOT] Depth constants derived from SOVEREIGN_REGISTRY — no hardcoded values
# Each root folder has its own depth defined in SOVEREIGN_REGISTRY[root]["depth"]
DEPTH_MAP = {root: cfg["depth"] for root, cfg in SOVEREIGN_REGISTRY.items()}

# Architectural Constants - derived from SSOT
MAX_LINES = 200
MIN_LINES = 10

# Exclusion Zones - [SSOT] Use ROOT_WHITELIST for allowed folders
EXCLUDED_DIRS = {
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    'node_modules', '.tox', 'dist', 'build', '.mypy_cache', '.coverage',
    '.vscode', '.idea', '.DS_Store',
    'logs', 'tmp', 'temp', '.tmp',
    '.cache', 'cache', 'data', 'archives',
    'htmlcov', '_build', 'site', '.doctrees',
}

EXCLUDED_FILES = {
    'canon_validator_v2_agentic.py',
    'conftest.py',
    '.DS_Store',
    'Thumbs.db',
}

# [SSOT] Import from structure_blueprint.py instead of hardcoding
ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)

# [SSOT] Protected root files from structure_blueprint.py
ALLOWED_ROOT_FILES = ROOT_PROTECTED_FILES