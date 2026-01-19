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

# Exports from structure_blueprint (canonical location: L5_safety/validators/)
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    FORBIDDEN_ROOT_FOLDERS,
    FORBIDDEN_FOLDER_PATTERN,
    ACTIVE_CANON_KEYS,
    ROOT_PROTECTED_FILES,
    CANON_KEY_TO_FOLDER_MAP,
)

__all__ = [
    "SOVEREIGN_REGISTRY",
    "FORBIDDEN_ROOT_FOLDERS",
    "FORBIDDEN_FOLDER_PATTERN",
    "ACTIVE_CANON_KEYS",
    "ROOT_PROTECTED_FILES",
    "CANON_KEY_TO_FOLDER_MAP",
]
