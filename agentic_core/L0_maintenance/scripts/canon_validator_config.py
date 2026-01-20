"""
Configuration constants and file discovery utilities.
The Three Laws of Subatomic Governance are defined here.
[SSOT] All structural constants derived from structure_blueprint.py
[SSOT] File discovery uses ssot_discovery.py - DO NOT define get_python_files here
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List

from agentic_core.L5_safety.validators.structure_blueprint import (
    ROOT_WHITELIST,
    ROOT_PROTECTED_FILES,
    SOVEREIGN_REGISTRY,
)

# SSOT Import: Use centralized file discovery
from agentic_core.utils.ssot_discovery import get_python_files, DEFAULT_EXCLUDE_DIRS

depth_map: Any = {root: cfg['depth'] for root, cfg in SOVEREIGN_REGISTRY.items()}
max_lines: Any = 200
min_lines: Any = 10
allowed_root_folders: Any = set(ROOT_WHITELIST)
allowed_root_files: Any = ROOT_PROTECTED_FILES

# Use SSOT exclude dirs - kept for backward compatibility reference
EXCLUDED_DIRS = DEFAULT_EXCLUDE_DIRS
EXCLUDED_FILES: Any = {'canon_validator_v2_agentic.py', 'auto_canon.py', '.DS_Store'}


def is_excluded(path: str) -> bool:
    """Check if path should be excluded from validation."""
    parts: Any = path.split(os.sep)
    if any((p in EXCLUDED_DIRS for p in parts)):
        return True
    if any((p.startswith('.') and len(p) > 1 and (p not in ['.github']) for p in parts)):
        return True
    return False


# NOTE: get_python_files is now imported from ssot_discovery.py
# This ensures consistent file discovery across all agents
