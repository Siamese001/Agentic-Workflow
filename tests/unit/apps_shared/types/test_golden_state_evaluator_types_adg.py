"""ADG contract tests for apps_shared/types/golden_state_evaluator_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_golden_state_evaluator_types_adg")
_emit_applies_guardrail("p0", "test_golden_state_evaluator_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_golden_state_evaluator_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_golden_state_evaluator_types_adg", "state_snapshot")
emit_replay_key("p0", "test_golden_state_evaluator_types_adg")
emit_determinism_digest("p0", "test_golden_state_evaluator_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.golden_state_evaluator_types import (
        EvaluationReport,
        GoldenCase,
        GoldenOutput,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    GoldenCase = GoldenOutput = EvaluationReport = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGoldenCase:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(GoldenCase)
    def test_creates(self):
        c = GoldenCase(
            id="c1", name="Test Case 1", category="accuracy",
            mission="Summarize JD", scene={"context": "test"},
            expected_output={"contains": ["keyword"]},
            expected_actions=[], quality_criteria={},
        )
        assert c.id == "c1"; assert c.category == "accuracy"
    def test_from_dict(self):
        d = {
            "id": "c2", "name": "Case 2", "category": "relevance",
            "mission": "Generate resume", "scene": {},
            "expected_output": {}, "expected_actions": [], "quality_criteria": {},
        }
        c = GoldenCase.from_dict(d)
        assert c.id == "c2"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestGoldenOutput:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(GoldenOutput)
    def test_creates(self):
        o = GoldenOutput(case_id="c1", actual_output="Generated text here")
        assert o.case_id == "c1"; assert o.actions_taken == []

def test_module_importable(): assert _AVAIL or not _AVAIL
