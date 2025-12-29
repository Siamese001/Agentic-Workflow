"""
Global architectural constants and governance laws.
[SSOT] All structural constants derived from structure_blueprint.py
"""

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    ROOT_WHITELIST,
    ROOT_PROTECTED_FILES,
    SOVEREIGN_REGISTRY,
)

# Law 1: The Law of Depth - [SSOT] Derived from SOVEREIGN_REGISTRY
# Each root folder has its own depth defined in SOVEREIGN_REGISTRY[root]["depth"]
DEPTH_MAP = {root: cfg["depth"] for root, cfg in SOVEREIGN_REGISTRY.items()}

# Law 2: The Law of Atomicity - Files must be subatomic, not noise or monoliths
MAX_LINES = 200                    # Maximum file size (subatomic limit)
MIN_LINES = 10                     # Minimum file size (anti-noise limit)

# Law 3: The Law of The Void - Root directory is sacred
# [SSOT] Import from structure_blueprint.py instead of hardcoding
ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)
ALLOWED_ROOT_FILES = ROOT_PROTECTED_FILES

# [SSOT] Import from structure_blueprint instead of hardcoding
from agentic_core.config.blueprint_sovereign.structure_blueprint import SOVEREIGN_EXCLUDED_FOLDERS

# CONFIGURATION: EXCLUSION ZONES (Strict Subatomic)
EXCLUDED_DIRS = SOVEREIGN_EXCLUDED_FOLDERS

EXCLUDED_FILES = {
    # Only the active validator and runner
    'canon_validator_v2_agentic.py',
    # Test files
    'test_*.py', '*_test.py', 'conftest.py',
    # Cache & Data files
    '*.pyc', '*.pyo', '*.pyd', '.DS_Store',
    # Build artifacts
    '*.egg-info', '*.whl', '*.zip', '*.tar.gz',
    # IDE files
    '.vscode/settings.json', '.idea/*.xml',
    # OS files
    'Thumbs.db', '*.tmp',
}
