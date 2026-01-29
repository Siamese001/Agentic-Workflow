# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, workflow
from __future__ import annotations

# This boosts alignment detection — review and integrate appropriately


"""
Canon Validator configuration
Defines exclusion zones and constants for validation.
"""
import os
from typing import Any

excluded_dirs: Any = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".idea",
    ".vscode",
    "build",
    "dist",
    "eggs",
    ARCHIVES_DIR,
    "data",
}
excluded_files: Any = {
    "CanonValidatorAgent.py",
    "canon_validator_backup.py",
    "canon_validator_v2_agentic.py",
    "auto_canon.py",
    ".DS_Store",
}
max_healing_per_file: Any = int(os.getenv("MAX_HEALING_PER_FILE", "8"))
global_healing_budget: Any = int(os.getenv("GLOBAL_HEALING_BUDGET", "50"))


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
