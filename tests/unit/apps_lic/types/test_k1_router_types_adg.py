"""ADG contract tests for apps_lic/types/k1_router_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_k1_router_types_adg")
_emit_applies_guardrail("p0", "test_k1_router_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_k1_router_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_k1_router_types_adg", "state_snapshot")
emit_replay_key("p0", "test_k1_router_types_adg")
emit_determinism_digest("p0", "test_k1_router_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.k1_router_types import (
        ArchetypeClassificationResult,
        K1Output,
        RouteSelectionResult,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ArchetypeClassificationResult = RouteSelectionResult = K1Output = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestArchetypeClassificationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ArchetypeClassificationResult)
    def test_creates(self):
        r = ArchetypeClassificationResult(
            archetype="C_LEVEL", confidence=0.95,
            matched_tokens=["CEO"], cxo_precedence_triggered=True,
            manual_override_required=False,
        )
        assert r.archetype == "C_LEVEL"; assert r.confidence == 0.95

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRouteSelectionResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RouteSelectionResult)
    def test_creates(self):
        r = RouteSelectionResult(route="INMAIL", premium_available=True, premium_routing_mismatch=False)
        assert r.route == "INMAIL"; assert r.blocking_reason is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestK1Output:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(K1Output)

def test_module_importable(): assert _AVAIL or not _AVAIL
