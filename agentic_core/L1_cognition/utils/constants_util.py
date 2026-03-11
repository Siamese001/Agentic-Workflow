from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Sovereign domain constants - Re-exported from canonical location.
This module provides waterfall-compliant access to shared constants.
[SSOT] All structural constants derived from structure_blueprint.py
"""
from typing import Any

from agentic_core.L0_routing.config import (
    ROOT_PROTECTED_FILES,
    ROOT_WHITELIST,
)
from agentic_core.L5_safety.config.structure_blueprint_config import DEPTH_RULES

depth_map: Any = dict(DEPTH_RULES)
max_lines: Any = 200
min_lines: Any = 10
excluded_dirs: Any = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".tox",
    "dist",
    "build",
    ".mypy_cache",
    ".coverage",
    ".vscode",
    ".idea",
    ".DS_Store",
    "logs",
    "tmp",
    "temp",
    ".tmp",
    ".cache",
    "cache",
    "data",
    ARCHIVES_DIR,
    "htmlcov",
    "_build",
    "site",
    ".doctrees",
}
excluded_files: Any = {"canon_validator_v2_agentic.py", "conftest.py", ".DS_Store", "Thumbs.db"}
allowed_root_folders: Any = set(ROOT_WHITELIST)
allowed_root_files: Any = ROOT_PROTECTED_FILES
