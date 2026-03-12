"""ADG-driven tests for L2_execution/enforcement/sovereign_sandbox_isolation.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.sovereign_sandbox_isolation import (
    ReplayNondeterminismViolation,
    SandboxResult,
    execute_in_sandbox,
)


class TestReplayNondeterminismViolation:
    def test_is_exception(self):
        assert issubclass(ReplayNondeterminismViolation, Exception)

    def test_creates(self):
        err = ReplayNondeterminismViolation("mismatch", expected="a", actual="b")
        assert err.expected == "a"
        assert err.actual == "b"
        assert "mismatch" in str(err)


class TestSandboxResult:
    def test_is_named_tuple(self):
        res = SandboxResult(success=True, result="ok")
        assert res.success is True
        assert res.result == "ok"
        assert res.violation is None

    def test_failure_result(self):
        res = SandboxResult(success=False, result=None)
        assert res.success is False


class TestExecuteInSandbox:
    def test_callable(self):
        assert callable(execute_in_sandbox)

    def test_runs_normal_operation(self):
        result = execute_in_sandbox(
            lambda: "hello",
            args=(),
            kwargs={},
            replay_mode=False,
        )
        assert isinstance(result, SandboxResult)
        assert result.success is True
