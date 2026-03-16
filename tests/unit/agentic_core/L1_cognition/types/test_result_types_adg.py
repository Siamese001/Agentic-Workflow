"""ADG-driven tests for L1_cognition/types/result_types.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_result_types_adg")
_emit_applies_guardrail("p0", "test_result_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_result_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_result_types_adg", "state_snapshot")
emit_replay_key("p0", "test_result_types_adg")
emit_determinism_digest("p0", "test_result_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.result_types import (
    DraftResult,
    QaResult,
    StrategyResultStrategy,
)


class TestStrategyResultStrategy:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StrategyResultStrategy)

    def test_creates(self):
        s = StrategyResultStrategy(_strategy="react", _confidence=0.9)
        assert s._strategy == "react"
        assert s._confidence == 0.9


class TestDraftResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DraftResult)

    def test_creates(self):
        dr = DraftResult(_sections=["intro", "body"], _content="hello world")
        assert dr._content == "hello world"
        assert len(dr._sections) == 2


class TestQaResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(QaResult)

    def test_creates(self):
        qa = QaResult(_findings="no issues found", confidence=0.95)
        assert qa._findings == "no issues found"
        assert qa.confidence == 0.95
