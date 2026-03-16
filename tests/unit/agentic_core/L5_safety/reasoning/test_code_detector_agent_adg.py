"""ADG-driven tests for L5_safety/reasoning/CodeDetectorAgent.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_code_detector_agent_adg")
_emit_applies_guardrail("p0", "test_code_detector_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_code_detector_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_code_detector_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_code_detector_agent_adg")
emit_determinism_digest("p0", "test_code_detector_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.CodeDetectorAgent import (
    CodeDetectorAgent,
    Detection,
    DetectionType,
    Severity,
)


class TestDetectionType:
    def test_dead_code_member(self):
        assert hasattr(DetectionType, "DEAD_CODE")

    def test_drift_member(self):
        assert hasattr(DetectionType, "DRIFT")

    def test_method_change_member(self):
        assert hasattr(DetectionType, "METHOD_CHANGE")


class TestSeverity:
    def test_info_value_0(self):
        assert Severity.INFO.value == 0

    def test_critical_highest(self):
        assert Severity.CRITICAL.value > Severity.ERROR.value

    def test_has_all_levels(self):
        for level in ("INFO", "WARNING", "ERROR", "CRITICAL"):
            assert hasattr(Severity, level)


class TestDetection:
    def test_creates(self):
        d = Detection(
            detection_type="DRIFT",
            file_path="foo.py",
            line_number=10,
            severity="WARNING",
            message="test detection",
        )
        assert d.detection_type == "DRIFT"
        assert d.line_number == 10


class TestCodeDetectorAgent:
    def test_creates(self):
        agent = CodeDetectorAgent()
        assert agent is not None

    def test_has_heal_repository(self):
        assert hasattr(CodeDetectorAgent, "heal_repository")
