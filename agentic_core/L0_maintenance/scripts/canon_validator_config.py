"""
Configuration constants and file discovery utilities.
The Three Laws of Subatomic Governance are defined here.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    MAX_DEPTH,
    MAX_LINES,
    MIN_DEPTH,
    MIN_LINES,
    ROOT_WHITELIST,
    SOVEREIGN_REGISTRY,
)

# Law 3: The Law of The Void - Root directory is sacred
# [SSOT] Import from structure_blueprint.py instead of hardcoding
ALLOWED_ROOT_FOLDERS = set(ROOT_WHITELIST)
ALLOWED_ROOT_FILES = {
    'README.md', '.gitignore', 'LICENSE', 'pyproject.toml', 'requirements.txt',
    '.env', 'canon_validator_agentic.py', 'pytest.ini'
}

# ==============================================================================
# CONFIGURATION: EXCLUSION ZONES (Strict Subatomic)
# ==============================================================================
EXCLUDED_DIRS = {
    # System & Environment
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs',
    'site-packages',
    # Project Data & Archives (Excluded from AST scanning)
    'archives', 'data',
    # Standard noise
    'cache', 'logs', 'tmp', 'temp'
}

EXCLUDED_FILES = {
    'canon_validator_v2_agentic.py',
    'auto_canon.py',
    '.DS_Store'
}


def is_excluded(path: str) -> bool:
    """Check if path should be excluded from validation."""
    parts = path.split(os.sep)
    if any(p in EXCLUDED_DIRS for p in parts):
        return True
    if any(p.startswith('.') and len(p) > 1 and p not in ['.github'] for p in parts):
        return True
    return False


def get_python_files() -> List[str]:
    """Get all Python files excluding specified directories and files."""
    python_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith('.py') and file not in EXCLUDED_FILES:
                file_path = os.path.join(root, file)
                if not is_excluded(file_path):
                    python_files.append(file_path)
    return python_files