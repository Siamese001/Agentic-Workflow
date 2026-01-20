"""
Public API for Configuration - SSOT for constants and registry.

This module provides clean import paths for configuration constants,
decoupling consumers from the internal folder structure.

SSOT Consolidation (Jan 20, 2026):
Instead of:
    from agentic_core.config.blueprint_sovereign.constants import DEFAULT_EXCLUDE_DIRS

Use:
    from agentic_core.config import DEFAULT_EXCLUDE_DIRS
"""
from __future__ import annotations

# Re-export from the SSOT modules
from .blueprint_sovereign.constants import (
    DEFAULT_EXCLUDE_DIRS,
    FORBIDDEN_PATTERNS_RAW,
    CANON_SIGNALS,
    NAMING_EXEMPT_FILES,
    NAMING_EXEMPT_DIRS,
    ALLOWED_DUPLICATE_FILENAMES,
    PYTHON_STDLIB_MODULES,
    VALIDATED_FILE_EXTENSIONS,
)

from .blueprint_sovereign.registry import (
    SOVEREIGN_REGISTRY,
    HEALING_CONFIG,
    CORE_SUBFOLDER_MAP,
    VARIABLE_DEPTH_SUBFOLDERS,
    L4_APPROVED_FOLDERS,
    GRAVITY_CONFIG,
    MISSION_CONFIG,
    AGENT_RESILIENCE_CONFIG,
    MCP_CAPABILITIES,
    LAYER_DIRS,
    L2_TO_L1_MAP,
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
