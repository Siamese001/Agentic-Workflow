"""ADG-driven tests for L5_safety/reasoning/CodeDetectorAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

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
