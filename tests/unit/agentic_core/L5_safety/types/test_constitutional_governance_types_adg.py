"""ADG contract tests for L5_safety/types/constitutional_governance_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_constitutional_governance_types_adg")
_emit_applies_guardrail("p0", "test_constitutional_governance_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_constitutional_governance_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_constitutional_governance_types_adg", "state_snapshot")
emit_replay_key("p0", "test_constitutional_governance_types_adg")
emit_determinism_digest("p0", "test_constitutional_governance_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L5_safety.types.constitutional_governance_types import (
    ConstitutionalPrinciple,
    GovernanceResult,
    PrincipleViolation,
)


class TestConstitutionalPrinciple:
    def test_is_enum(self):
        import enum; assert issubclass(ConstitutionalPrinciple, enum.Enum)
    def test_has_harmlessness(self): assert ConstitutionalPrinciple.HARMLESSNESS.value == "harmlessness"
    def test_has_seven_principles(self): assert len(list(ConstitutionalPrinciple)) == 7

class TestPrincipleViolation:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(PrincipleViolation)
    def test_creates(self):
        v = PrincipleViolation(principle=ConstitutionalPrinciple.HONESTY, severity="minor",
                               description="potential deception")
        assert v.principle == ConstitutionalPrinciple.HONESTY
        assert v.suggested_revision is None

class TestGovernanceResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(GovernanceResult)
    def test_compliant_no_violations(self):
        r = GovernanceResult(compliant=True); assert r.violations == []
    def test_non_compliant(self):
        v = PrincipleViolation(principle=ConstitutionalPrinciple.FAIRNESS, severity="severe", description="d")
        r = GovernanceResult(compliant=False, violations=[v])
        assert len(r.violations) == 1
