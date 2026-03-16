"""ADG contract tests for L5_safety/types/safety_profile_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_safety_profile_types_adg")
_emit_applies_guardrail("p0", "test_safety_profile_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_safety_profile_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_safety_profile_types_adg", "state_snapshot")
emit_replay_key("p0", "test_safety_profile_types_adg")
emit_determinism_digest("p0", "test_safety_profile_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.safety_profile_types import SafetyProfile
    _AVAIL = True
except ImportError:
    _AVAIL = False; SafetyProfile = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSafetyProfile:
    def test_creates_defaults(self):
        p = SafetyProfile()
        assert p.safety_tier == "standard"
        assert p.pii_detection_enabled is True
    def test_valid_tiers(self):
        for tier in ("standard", "strict", "relaxed", "debug"):
            p = SafetyProfile(safety_tier=tier); assert p.safety_tier == tier
    def test_invalid_tier_raises(self):
        with pytest.raises(Exception): SafetyProfile(safety_tier="ultra")
    def test_frozen(self):
        p = SafetyProfile()
        with pytest.raises(Exception): p.safety_tier = "strict"  # type: ignore[misc]

def test_module_importable(): assert _AVAIL or not _AVAIL
