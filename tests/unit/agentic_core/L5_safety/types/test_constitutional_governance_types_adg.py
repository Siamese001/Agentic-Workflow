"""ADG contract tests for L5_safety/types/constitutional_governance_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L5_safety.types.constitutional_governance_types import (
    ConstitutionalPrinciple, PrincipleViolation, GovernanceResult,
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
