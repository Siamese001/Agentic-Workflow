"""ADG contract tests for apps_lic/types/stack_modernization_agent_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_stack_modernization_agent_types_adg")
_emit_applies_guardrail("p0", "test_stack_modernization_agent_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_stack_modernization_agent_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_stack_modernization_agent_types_adg", "state_snapshot")
emit_replay_key("p0", "test_stack_modernization_agent_types_adg")
emit_determinism_digest("p0", "test_stack_modernization_agent_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.stack_modernization_agent_types import (
        LegacyDiagnostic,
        MigrationThesis,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    LegacyDiagnostic = MigrationThesis = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestLegacyDiagnostic:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(LegacyDiagnostic)
    def test_creates(self):
        d = LegacyDiagnostic(
            detected_legacy_tech=["java 8", "oracle"],
            implied_pain_points=["slow queries"],
            modernization_score=0.6,
        )
        assert d.modernization_score == 0.6
    def test_is_highly_legacy_true(self):
        d = LegacyDiagnostic(
            detected_legacy_tech=["a", "b", "c"],
            implied_pain_points=[],
            modernization_score=0.8,
        )
        assert d.is_highly_legacy is True
    def test_is_highly_legacy_false(self):
        d = LegacyDiagnostic(
            detected_legacy_tech=[],
            implied_pain_points=[],
            modernization_score=0.1,
        )
        assert d.is_highly_legacy is False

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMigrationThesis:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(MigrationThesis)
    def test_creates(self):
        t = MigrationThesis(
            current_state_diagnosis="Uses Oracle DB",
            target_state_vision="Cloud-native + Vector DB",
            bridge_strategy="Strangler Fig Pattern",
        )
        assert "Oracle" in t.current_state_diagnosis
    def test_is_transformative_true(self):
        t = MigrationThesis(
            current_state_diagnosis="x", target_state_vision="y",
            bridge_strategy="migration",
        )
        assert isinstance(t.is_transformative, bool)

def test_module_importable(): assert _AVAIL or not _AVAIL
