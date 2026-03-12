"""ADG contract tests for L5_safety/types/rule_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L5_safety.types.rule_types import (
    RuleType, RuleSeverity, ViolationType, ConstitutionalRule, ViolationReport,
)

class TestRuleType:
    def test_is_enum(self):
        import enum; assert issubclass(RuleType, enum.Enum)
    def test_has_safety(self): assert RuleType.SAFETY.value == "safety"

class TestRuleSeverity:
    def test_is_enum(self):
        import enum; assert issubclass(RuleSeverity, enum.Enum)
    def test_has_critical(self): assert RuleSeverity.CRITICAL.value == "critical"

class TestViolationType:
    def test_is_enum(self):
        import enum; assert issubclass(ViolationType, enum.Enum)
    def test_has_content(self): assert ViolationType.CONTENT.value == "content"

class TestConstitutionalRule:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ConstitutionalRule)
    def test_creates(self):
        r = ConstitutionalRule(rule_id="r1", RuleType=RuleType.SAFETY, title="T",
                               description="D", pattern=r"bad", Severity=RuleSeverity.HIGH, action="block")
        assert r.rule_id == "r1"

class TestViolationReport:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ViolationReport)
    def test_creates(self):
        v = ViolationReport(rule_id="r1", ViolationType=ViolationType.CONTENT, Severity=RuleSeverity.LOW,
                            location="line 5", content="bad word", suggestion="remove it", confidence=0.9)
        assert v.confidence == 0.9
