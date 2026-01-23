from __future__ import annotations

"""
Public API for configuration - SSOT for constants and registry.

This module provides clean import paths for configuration constants,
decoupling consumers from the internal folder structure.

SSOT Consolidation (Jan 20, 2026):
Instead of:
    from agentic_core.config.blueprint_sovereign.constants import DEFAULT_EXCLUDE_DIRS

Use:
    from agentic_core.config import DEFAULT_EXCLUDE_DIRS
"""


# Re-export from the SSOT modules
# Import from structure_blueprint (actual SSOT location)
try:
    from agentic_core.L5_safety.validators.structure_blueprint import (
        CANON_SIGNALS,
    )
except ImportError:
    CANON_SIGNALS = set()

# Define constants that may not exist in structure_blueprint
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

from .blueprint_sovereign.registry import (
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
    # Constants
    "DEFAULT_EXCLUDE_DIRS",
    "FORBIDDEN_PATTERNS_RAW",
    "CANON_SIGNALS",
    "NAMING_EXEMPT_FILES",
    "NAMING_EXEMPT_DIRS",
    "ALLOWED_DUPLICATE_FILENAMES",
    "PYTHON_STDLIB_MODULES",
    "VALIDATED_FILE_EXTENSIONS",
    # Registry
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
]
