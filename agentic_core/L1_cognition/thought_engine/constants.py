from __future__ import annotations

"""
Sovereign domain constants - Re-exported from canonical location.
This module provides waterfall-compliant access to shared constants.
[SSOT] All structural constants derived from structure_blueprint.py
"""
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    ROOT_PROTECTED_FILES,
    ROOT_WHITELIST,
    SOVEREIGN_REGISTRY,
)

depth_map: Any = {root: cfg['depth'] for root, cfg in SOVEREIGN_REGISTRY.items()}
max_lines: Any = 200
min_lines: Any = 10
excluded_dirs: Any = {'.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', 'node_modules', '.tox', 'dist', 'build', '.mypy_cache', '.coverage', '.vscode', '.idea', '.DS_Store', 'logs', 'tmp', 'temp', '.tmp', '.cache', 'cache', 'data', 'archives', 'htmlcov', '_build', 'site', '.doctrees'}
excluded_files: Any = {'canon_validator_v2_agentic.py', 'conftest.py', '.DS_Store', 'Thumbs.db'}
allowed_root_folders: Any = set(ROOT_WHITELIST)
allowed_root_files: Any = ROOT_PROTECTED_FILES
