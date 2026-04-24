"""W5 unit tests for the L2 best-practices gap plan (b7c4e2).

Covers:
- LLM call temperature audit (G11)
- Runtime behavior monitor: tool sequence / retry storm / cost drift (G13)
- Seal schema validator (G14)
- Trace grading hooks (G15)
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement.llm_call_audit import (
    LLMCallEnvelope,
    audit_llm_call,
)
from agentic_core.L2_execution.enforcement.runtime_behavior_monitor import (
    BehaviorMonitor,
    TraceEvent,
    WorkflowTrace,
)
from agentic_core.L2_execution.enforcement.seal_schema_validator import (
    FieldSpec,
    SealSchema,
    SealValidationError,
    validate_sealed_artifact,
)
from agentic_core.L2_execution.types.trace_grading_hooks import (
    GradingBundle,
    GradingTarget,
)


# ---------------------------------------------------------------------------
# LLM call audit (G11)
# ---------------------------------------------------------------------------


class TestLLMCallAudit:
    def test_tool_choice_none_is_compliant(self) -> None:
        env = LLMCallEnvelope(model="m", temperature=0.9, tool_choice="none")
        f = audit_llm_call(env)
        assert f.compliant is True
        assert f.severity == "info"

    def test_low_temperature_compliant(self) -> None:
        env = LLMCallEnvelope(model="m", temperature=0.1, tool_choice="auto")
        f = audit_llm_call(env)
        assert f.compliant is True

    def test_high_temperature_warning(self) -> None:
        env = LLMCallEnvelope(model="m", temperature=0.8, tool_choice="auto")
        f = audit_llm_call(env)
        assert f.compliant is False
        assert f.severity == "warning"
        assert "0.8" in f.reason

    def test_custom_ceiling(self) -> None:
        env = LLMCallEnvelope(model="m", temperature=0.4, tool_choice="required")
        assert audit_llm_call(env).compliant is False
        assert audit_llm_call(env, temperature_ceiling=0.5).compliant is True


# ---------------------------------------------------------------------------
# Behavior monitor (G13)
# ---------------------------------------------------------------------------


class TestBehaviorMonitor:
    def test_clean_trace_no_findings(self) -> None:
        t = WorkflowTrace()
        t.record(TraceEvent(step_id="s1", tool_name="a"))
        t.record(TraceEvent(step_id="s2", tool_name="b"))
        assert BehaviorMonitor().evaluate(t) == []

    def test_tool_streak_warning(self) -> None:
        t = WorkflowTrace()
        for i in range(3):
            t.record(TraceEvent(step_id=f"s{i}", tool_name="hot"))
        findings = BehaviorMonitor().evaluate(t)
        assert any(f.kind == "tool_sequence_anomaly" and f.severity == "warning" for f in findings)

    def test_tool_streak_critical(self) -> None:
        t = WorkflowTrace()
        for i in range(6):
            t.record(TraceEvent(step_id=f"s{i}", tool_name="hot"))
        findings = BehaviorMonitor().evaluate(t)
        assert any(f.kind == "tool_sequence_anomaly" and f.severity == "critical" for f in findings)

    def test_retry_storm(self) -> None:
        t = WorkflowTrace()
        t.record(TraceEvent(step_id="s1", tool_name="x", retry_count=6))
        findings = BehaviorMonitor().evaluate(t)
        assert any(f.kind == "retry_storm" and f.severity == "critical" for f in findings)

    def test_cost_drift_tokens(self) -> None:
        t = WorkflowTrace()
        t.record(TraceEvent(step_id="s1", tool_name="x", tokens=60_000))
        findings = BehaviorMonitor().evaluate(t)
        assert any(f.kind == "cost_drift" and f.severity == "warning" for f in findings)

    def test_cost_drift_wall(self) -> None:
        t = WorkflowTrace()
        t.record(TraceEvent(step_id="s1", tool_name="x", wall_ms=150_000))
        findings = BehaviorMonitor().evaluate(t)
        assert any(f.kind == "cost_drift" and f.severity == "critical" for f in findings)


# ---------------------------------------------------------------------------
# Seal schema validator (G14)
# ---------------------------------------------------------------------------


class TestSealSchemaValidator:
    def _schema(self) -> SealSchema:
        return SealSchema(
            name="sealed_step",
            fields=(
                FieldSpec("status", str, enum=("SUCCESS", "FAILURE", "NEEDS_HELP")),
                FieldSpec("trace_id", str, min_len=1),
                FieldSpec("attempts", int),
                FieldSpec("note", str, required=False, max_len=200),
            ),
            allow_extra=False,
        )

    def test_happy_path(self) -> None:
        validate_sealed_artifact(
            {"status": "SUCCESS", "trace_id": "t-1", "attempts": 1},
            self._schema(),
        )

    def test_missing_required(self) -> None:
        with pytest.raises(SealValidationError) as exc:
            validate_sealed_artifact(
                {"status": "SUCCESS", "attempts": 1},
                self._schema(),
            )
        assert any("trace_id" in e for e in exc.value.errors)

    def test_wrong_type(self) -> None:
        with pytest.raises(SealValidationError) as exc:
            validate_sealed_artifact(
                {"status": "SUCCESS", "trace_id": "t", "attempts": "one"},
                self._schema(),
            )
        assert any("attempts" in e for e in exc.value.errors)

    def test_enum_violation(self) -> None:
        with pytest.raises(SealValidationError) as exc:
            validate_sealed_artifact(
                {"status": "MEH", "trace_id": "t", "attempts": 1},
                self._schema(),
            )
        assert any("MEH" in e for e in exc.value.errors)

    def test_extra_field_rejected(self) -> None:
        with pytest.raises(SealValidationError):
            validate_sealed_artifact(
                {
                    "status": "SUCCESS",
                    "trace_id": "t",
                    "attempts": 1,
                    "rogue": 42,
                },
                self._schema(),
            )

    def test_allow_extra(self) -> None:
        schema = SealSchema(
            name="open",
            fields=(FieldSpec("x", int),),
            allow_extra=True,
        )
        validate_sealed_artifact({"x": 1, "y": "ok"}, schema)


# ---------------------------------------------------------------------------
# Trace grading hooks (G15)
# ---------------------------------------------------------------------------


class TestTraceGradingHooks:
    def test_add_and_filter(self) -> None:
        b = GradingBundle(trace_id="t-1")
        s1 = b.add(slot_id="d1", target=GradingTarget.DECISION)
        s2 = b.add(slot_id="t1", target=GradingTarget.TOOL_CALL)
        assert len(b.slots) == 2
        assert b.by_target(GradingTarget.DECISION) == [s1]
        assert b.by_target(GradingTarget.TOOL_CALL) == [s2]

    def test_with_grade_is_immutable(self) -> None:
        b = GradingBundle(trace_id="t")
        s = b.add(slot_id="x", target=GradingTarget.E3_EXECUTE)
        graded = s.with_grade(0.85, rationale="tool succeeded cleanly")
        assert s.grade is None  # original unchanged
        assert graded.grade == 0.85
        assert graded.slot_id == s.slot_id

    def test_to_dict_bundle(self) -> None:
        b = GradingBundle(trace_id="t-9")
        b.add(
            slot_id="s1",
            target=GradingTarget.E5_SEAL,
            preliminary_signals={"attempts": 2},
            metadata={"reason": "sealed after heal"},
        )
        d = b.to_dict()
        assert d["trace_id"] == "t-9"
        assert len(d["slots"]) == 1
        assert d["slots"][0]["preliminary_signals"] == {"attempts": 2}
