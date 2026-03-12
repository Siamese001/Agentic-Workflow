"""ADG-driven tests for L2_execution/tools/tool_verifier_impl.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.tools.tool_verifier_impl import (
    VerificationResult,
    VerificationIssue,
)


class TestVerificationResult:
    def test_is_enum(self):
        import enum
        assert issubclass(VerificationResult, enum.Enum)

    def test_passed_value(self):
        assert VerificationResult.PASSED.value == "passed"

    def test_failed_value(self):
        assert VerificationResult.FAILED.value == "failed"

    def test_warning_value(self):
        assert VerificationResult.WARNING.value == "warning"


class TestVerificationIssue:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VerificationIssue)
