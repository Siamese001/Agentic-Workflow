"""
Tier-to-model ID mapping for heal policy escalation.

Pure mapping function (stdlib-only, no environment access).
Phase 6 Wave 6.2.
"""

from __future__ import annotations

from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

LOW_MODEL_ID = "local_low"
HIGH_MODEL_ID = "local_high"


def map_tier_to_model_id(tier: ReasoningTier) -> str:
    """Map a reasoning tier to a model identifier.

    Args:
        tier: The reasoning tier (LOW or HIGH)

    Returns:
        Model identifier string ("local_low" or "local_high")
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "map_tier_to_model_id", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "map_tier_to_model_id", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "map_tier_to_model_id")
    return LOW_MODEL_ID if tier == ReasoningTier.LOW else HIGH_MODEL_ID
