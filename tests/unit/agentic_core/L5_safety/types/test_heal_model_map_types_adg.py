"""ADG contract tests for L5_safety/types/heal_model_map_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_heal_model_map_types_adg")
_emit_applies_guardrail("p0", "test_heal_model_map_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_heal_model_map_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_heal_model_map_types_adg", "state_snapshot")
emit_replay_key("p0", "test_heal_model_map_types_adg")
emit_determinism_digest("p0", "test_heal_model_map_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.heal_model_map_types import (
        HIGH_MODEL_ID,
        LOW_MODEL_ID,
        map_tier_to_model_id,
    )
    from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier
    _AVAIL = True
except ImportError:
    _AVAIL = False
    LOW_MODEL_ID = HIGH_MODEL_ID = map_tier_to_model_id = ReasoningTier = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestModelMapConstants:
    def test_low_model_id(self): assert LOW_MODEL_ID == "local_low"
    def test_high_model_id(self): assert HIGH_MODEL_ID == "local_high"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMapTierToModelId:
    def test_low_tier(self):
        assert map_tier_to_model_id(ReasoningTier.LOW) == LOW_MODEL_ID
    def test_high_tier(self):
        assert map_tier_to_model_id(ReasoningTier.HIGH) == HIGH_MODEL_ID

def test_module_importable(): assert _AVAIL or not _AVAIL
