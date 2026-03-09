"""
agentic_core/interfaces/structure_config.py

Sovereign structure config interface for apps_* consumption.

Re-exports structural config constants from L5_safety structure_blueprint_config
so apps_* tools and configs can import from the approved interface boundary.

AUTHORITY CONSTRAINTS:
- Config constants are read-only — no mutation authority
- No access to enforcement logic
- No structural write authority

USAGE (apps_*):
    from agentic_core.interfaces.structure_config import (
        DASHBOARD_DIR,
        get_validated_project_root,
        CORE_SUBFOLDER_MAP,
        FORBIDDEN_PATTERNS,
        FORBIDDEN_ROOT_FOLDERS,
        ROOT_PROTECTED_FILES,
        ROOT_WHITELIST,
        SOVEREIGN_REGISTRY,
    )
"""

from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint import (  # noqa: F401
    CORE_SUBFOLDER_MAP,
    FORBIDDEN_PATTERNS,
    FORBIDDEN_ROOT_FOLDERS,
    ROOT_PROTECTED_FILES,
    ROOT_WHITELIST,
    SOVEREIGN_REGISTRY,
)

try:
    from agentic_core.L5_safety.config.structure_blueprint import (  # noqa: F401
        AGENT_DISCOVERY_JSON,
        AGENT_DISCOVERY_MANIFEST_JSON,
        AGENTIC_CORE_DIR,
        DASHBOARD_DIR,
        L0_MAINTENANCE_DIR,
        L1_COGNITION_DIR,
        L2_EXECUTION_DIR,
        L3_ORCHESTRATION_DIR,
        L4_STATE_DIR,
        L5_SAFETY_DIR,
        L6_OBSERVABILITY_DIR,
        SCRIPTS_DIR,
        TESTS_DIR,
        get_validated_project_root,
    )
except ImportError:
    AGENT_DISCOVERY_JSON = None  # type: ignore[assignment]
    AGENT_DISCOVERY_MANIFEST_JSON = None  # type: ignore[assignment]
    AGENTIC_CORE_DIR = None  # type: ignore[assignment]
    DASHBOARD_DIR = None  # type: ignore[assignment]
    L0_MAINTENANCE_DIR = None  # type: ignore[assignment]
    L1_COGNITION_DIR = None  # type: ignore[assignment]
    L2_EXECUTION_DIR = None  # type: ignore[assignment]
    L3_ORCHESTRATION_DIR = None  # type: ignore[assignment]
    L4_STATE_DIR = None  # type: ignore[assignment]
    L5_SAFETY_DIR = None  # type: ignore[assignment]
    L6_OBSERVABILITY_DIR = None  # type: ignore[assignment]
    SCRIPTS_DIR = None  # type: ignore[assignment]
    TESTS_DIR = None  # type: ignore[assignment]
    get_validated_project_root = None  # type: ignore[assignment]

__all__ = [
    "AGENT_DISCOVERY_JSON",
    "AGENT_DISCOVERY_MANIFEST_JSON",
    "AGENTIC_CORE_DIR",
    "CORE_SUBFOLDER_MAP",
    "DASHBOARD_DIR",
    "FORBIDDEN_PATTERNS",
    "FORBIDDEN_ROOT_FOLDERS",
    "L0_MAINTENANCE_DIR",
    "L1_COGNITION_DIR",
    "L2_EXECUTION_DIR",
    "L3_ORCHESTRATION_DIR",
    "L4_STATE_DIR",
    "L5_SAFETY_DIR",
    "L6_OBSERVABILITY_DIR",
    "ROOT_PROTECTED_FILES",
    "ROOT_WHITELIST",
    "SCRIPTS_DIR",
    "SOVEREIGN_REGISTRY",
    "TESTS_DIR",
    "get_validated_project_root",
]
