from __future__ import annotations
"""
config/blueprint_sovereign – Sovereign Territory

Purpose:
    Sovereign territory

Best Practices:
    - Single responsibility per module
    - Explicit imports only from approved layers (gravity compliance)
    - All public functions/classes fully typed and documented
    - No side effects unless explicitly in L2_execution or L4_state
    - No raw strings — use prompt_governance for prompts
    - No inline Pydantic models — use schemas/models

Current Status (December 28, 2025):
    - Territory claimed and protected
    - Awaiting sovereign curation of high-signal implementations

Future Curation Roadmap:
    - Implement canonical patterns for this layer
    - Add unit + property + stateful tests
    - Register with relevant L4/L5 systems
"""

# Exports from structure_blueprint
from .structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
    APPS_RG_SUBFOLDER_MAP,
    APPS_LIC_SUBFOLDER_MAP,
    APPS_SHARED_SUBFOLDER_MAP,
    TESTS_L2_SUBFOLDER_MAP,
    FORBIDDEN_ROOT_FOLDERS,
    FORBIDDEN_FOLDER_PATTERN,
    ACTIVE_CANON_KEYS,
    ROOT_PROTECTED_FILES,
    CANON_KEY_TO_FOLDER_MAP,
    CANON_SIGNALS,
)

__all__ = [
    "SOVEREIGN_REGISTRY",
    "CORE_SUBFOLDER_MAP", 
    "APPS_RG_SUBFOLDER_MAP",
    "APPS_LIC_SUBFOLDER_MAP",
    "APPS_SHARED_SUBFOLDER_MAP",
    "TESTS_L2_SUBFOLDER_MAP",
    "FORBIDDEN_ROOT_FOLDERS",
    "FORBIDDEN_FOLDER_PATTERN",
    "ACTIVE_CANON_KEYS",
    "ROOT_PROTECTED_FILES",
    "CANON_KEY_TO_FOLDER_MAP",
    "CANON_SIGNALS",
]
