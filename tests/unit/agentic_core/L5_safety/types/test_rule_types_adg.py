"""ADG contract tests for L5_safety/types/rule_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_rule_types_adg")
_emit_applies_guardrail("p0", "test_rule_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_rule_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_rule_types_adg", "state_snapshot")
emit_replay_key("p0", "test_rule_types_adg")
emit_determinism_digest("p0", "test_rule_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L5_safety.types.rule_types import (
    ConstitutionalRule,
    RuleSeverity,
    RuleType,
    ViolationReport,
    ViolationType,
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
