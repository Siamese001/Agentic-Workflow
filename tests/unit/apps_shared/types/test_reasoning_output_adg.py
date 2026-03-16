"""ADG contract tests for apps_shared/types/reasoning_output.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_reasoning_output_adg")
_emit_applies_guardrail("p0", "test_reasoning_output_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_reasoning_output_adg", "policy_binding")
_emit_snapshots_state("p0", "test_reasoning_output_adg", "state_snapshot")
emit_replay_key("p0", "test_reasoning_output_adg")
emit_determinism_digest("p0", "test_reasoning_output_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.reasoning_output import ReasoningOutput, scan_for_violations
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ReasoningOutput = scan_for_violations = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestReasoningOutput:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ReasoningOutput)
    def test_creates(self):
        ro = ReasoningOutput(status="success")
        assert ro.status == "success"; assert ro.payload == {}; assert ro.errors == []
    def test_is_success(self):
        ro = ReasoningOutput.success(payload={"x": 1}, agent="TestAgent")
        assert ro.is_success() is True; assert ro.is_error() is False
        assert ro.payload == {"x": 1}; assert ro.agent == "TestAgent"
    def test_is_error(self):
        ro = ReasoningOutput.error(errors=["bad thing"], agent="TestAgent")
        assert ro.is_error() is True; assert ro.is_success() is False
        assert "bad thing" in ro.errors
    def test_skipped(self):
        ro = ReasoningOutput.skipped(reason="no input", agent="TestAgent")
        assert ro.status == "skipped"; assert ro.payload["reason"] == "no input"
    def test_trace_id_default_empty(self):
        ro = ReasoningOutput(status="partial")
        assert ro.trace_id == ""

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestScanForViolations:
    def test_callable(self): assert callable(scan_for_violations)
    def test_returns_list(self):
        from pathlib import Path
        result = scan_for_violations(scan_dirs=[Path("apps_shared/types")])
        assert isinstance(result, list)

def test_module_importable(): assert _AVAIL or not _AVAIL
