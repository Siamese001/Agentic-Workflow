from __future__ import annotations

"""
SSOT for Sovereign Blueprint configuration.

This package is the Single Source of Truth for:
- DEFAULT_EXCLUDE_DIRS: Unified directory exclusion list
- SOVEREIGN_REGISTRY: Core territory definitions
- HEALING_CONFIG: Healing operation configuration

SSOT Consolidation (Jan 20, 2026):
- constants.py: Exclusion lists and naming constants
- registry.py: Territory and configuration data

For backward compatibility, this module also re-exports from
L5_safety/validators/structure_blueprint.py
"""


# SSOT Exports - Import from structure_blueprint (actual SSOT location)
try:
    from agentic_core.L5_safety.validators.structure_blueprint import CANON_SIGNALS
except ImportError:
    CANON_SIGNALS = set()

# Define constants
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "archives",
    ".sovereign_healing_backup",
}
FORBIDDEN_PATTERNS_RAW = []
NAMING_EXEMPT_FILES = set()
NAMING_EXEMPT_DIRS = set()
ALLOWED_DUPLICATE_FILENAMES = set()
PYTHON_STDLIB_MODULES = set()
VALIDATED_FILE_EXTENSIONS = {".py", ".pyi"}

# Backward compatibility: Re-export from structure_blueprint
from agentic_core.L5_safety.validators.structure_blueprint import (
    FORBIDDEN_FOLDER_PATTERN,
    FORBIDDEN_ROOT_FOLDERS,
    ROOT_PROTECTED_FILES,
)

from .registry import (
    AGENT_RESILIENCE_CONFIG,
    CORE_SUBFOLDER_MAP,
    GRAVITY_CONFIG,
    HEALING_CONFIG,
    L2_TO_L1_MAP,
    L4_APPROVED_FOLDERS,
    LAYER_DIRS,
    MCP_CAPABILITIES,
    MISSION_CONFIG,
    SOVEREIGN_REGISTRY,
    VARIABLE_DEPTH_SUBFOLDERS,
)

__all__ = [
    # From constants.py (SSOT)
    "DEFAULT_EXCLUDE_DIRS",
    "FORBIDDEN_PATTERNS_RAW",
    "CANON_SIGNALS",
    "NAMING_EXEMPT_FILES",
    "NAMING_EXEMPT_DIRS",
    "ALLOWED_DUPLICATE_FILENAMES",
    "PYTHON_STDLIB_MODULES",
    "VALIDATED_FILE_EXTENSIONS",
    # From registry.py (SSOT)
    "SOVEREIGN_REGISTRY",
    "HEALING_CONFIG",
    "CORE_SUBFOLDER_MAP",
    "VARIABLE_DEPTH_SUBFOLDERS",
    "L4_APPROVED_FOLDERS",
    "GRAVITY_CONFIG",
    "MISSION_CONFIG",
    "AGENT_RESILIENCE_CONFIG",
    "MCP_CAPABILITIES",
    "LAYER_DIRS",
    "L2_TO_L1_MAP",
    # Backward compatibility (from structure_blueprint)
    "FORBIDDEN_ROOT_FOLDERS",
    "FORBIDDEN_FOLDER_PATTERN",
    "ROOT_PROTECTED_FILES",
]
