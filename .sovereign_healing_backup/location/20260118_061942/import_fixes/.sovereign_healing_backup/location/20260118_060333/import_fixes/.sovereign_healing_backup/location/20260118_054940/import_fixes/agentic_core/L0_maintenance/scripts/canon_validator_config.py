
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
"""
Configuration constants and file discovery utilities.
The Three Laws of Subatomic Governance are defined here.
[SSOT] All structural constants derived from structure_blueprint.py
"""
import os
from pathlib import Path
from typing import Any, List
from agentic_core.L5_safety.validators.structure_blueprint import ROOT_WHITELIST, ROOT_PROTECTED_FILES, SOVEREIGN_REGISTRY
depth_map: Any = {root: cfg['depth'] for root, cfg in SOVEREIGN_REGISTRY.items()}
max_lines: Any = 200
min_lines: Any = 10
allowed_root_folders: Any = set(ROOT_WHITELIST)
allowed_root_files: Any = ROOT_PROTECTED_FILES
excluded_dirs: Any = {'.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', 'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs', 'site-packages', 'archives', 'data', 'cache', 'logs', 'tmp', 'temp'}
excluded_files: Any = {'canon_validator_v2_agentic.py', 'auto_canon.py', '.DS_Store'}

def is_excluded(path: str) -> bool:
    """Check if path should be excluded from validation."""
    parts: Any = path.split(os.sep)
    if any((p in EXCLUDED_DIRS for p in parts)):
        return True
    if any((p.startswith('.') and len(p) > 1 and (p not in ['.github']) for p in parts)):
        return True
    return False

def get_python_files() -> List[str]:
    """Get all Python files excluding specified directories and files."""
    python_files: Any = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith('.py') and file not in EXCLUDED_FILES:
                file_path: Any = os.path.join(root, file)
                if not is_excluded(file_path):
                    python_files.append(file_path)
    return python_files