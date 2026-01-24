"""
DEPRECATED: 2026-01-24
======================
CRITICAL: THIS AGENT IS DEPRECATED. LOGIC MOVED TO SOVEREIGN V2.5 ARCHITECTURE.

Migration Path:
- Rule Definitions: agentic_core.L5_safety.validators.structure_blueprint.CANON_VALIDATION_REGISTRY
- Rule Execution: agentic_core.base_agents.healer_mixin.HealerMixin

DO NOT ADD NEW LOGIC HERE. This file is a tombstone kept for backward compatibility.
"""
from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


class CanonBaseAgent(SovereignBaseAgent):
    """
    !! DEPRECATED !!
    
    This class is a tombstone kept for backward compatibility.
    All validation logic has been migrated to:
    - CANON_VALIDATION_REGISTRY in structure_blueprint.py (rule definitions)
    - HealerMixin in healer_mixin.py (rule execution)
    
    Use HealerMixin.validate_canon_key(key_id, context) for validation.
    """
    
    pass
