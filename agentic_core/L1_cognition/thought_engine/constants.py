"""
Sovereign domain constants - Re-exported from canonical location.
This module provides waterfall-compliant access to shared constants.
"""

import sys
from pathlib import Path

# Path insert no longer needed - using absolute import
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    MAX_DEPTH,
    MAX_LINES,
    MIN_DEPTH,
    MIN_LINES,
    ROOT_WHITELIST,
    SOVEREIGN_REGISTRY,
)

# Exclusion Zones
EXCLUDED_DIRS = {
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    'node_modules', '.tox', 'dist', 'build', '.mypy_cache', '.coverage',
    '.vscode', '.idea', '*.swp', '*.swo', '.DS_Store',
    'logs', 'tmp', 'temp', '.tmp',
    '.cache', 'cache', 'data', 'archives',
    'htmlcov', 'coverage.xml', '_build', 'site', '.doctrees',
}

EXCLUDED_FILES = {
    'canon_validator_v2_agentic.py',
    'test_*.py', '*_test.py', 'conftest.py',
    '*.pyc', '*.pyo', '*.pyd', '.DS_Store',
    '*.egg-info', '*.whl', '*.zip', '*.tar.gz',
    '.vscode/settings.json', '.idea/*.xml',
    'Thumbs.db', '*.tmp',
}

# [SSOT] Import from structure_blueprint.py instead of hardcoding
ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)

ALLOWED_ROOT_FILES = {
    'README.md', '.gitignore', 'LICENSE', 'pyproject.toml', 'requirements.txt',
    '.env', 'canon_validator_agentic.py', 'pytest.ini'
}