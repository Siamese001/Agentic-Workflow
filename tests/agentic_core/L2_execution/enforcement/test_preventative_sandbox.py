"""Tests for PreventativeSandbox - sandboxed execution environment."""
import pytest
from unittest.mock import Mock
from agentic_core.L2_execution.enforcement.preventative_sandbox import PreventativeSandbox


class TestPreventativeSandbox:
    def test_init(self):
        sb = PreventativeSandbox()
        assert sb is not None

    def test_execute_in_sandbox(self):
        sb = PreventativeSandbox()
        result = sb.execute(lambda: 42)
        assert result == 42

    def test_execute_with_timeout(self):
        import time
        sb = PreventativeSandbox(timeout_seconds=1)
        with pytest.raises(TimeoutError):
            sb.execute(lambda: time.sleep(2))

    def test_execute_blocks_disallowed_imports(self):
        sb = PreventativeSandbox(allowed_imports=["math"])
        with pytest.raises(ImportError):
            sb.execute(lambda: __import__("os"))

    def test_execute_resource_limits(self):
        sb = PreventativeSandbox(memory_limit_mb=10)
        # Smoke test — should not raise on simple operation
        result = sb.execute(lambda: sum(range(100)))
        assert result == sum(range(100))

    def test_execute_handles_exception(self):
        sb = PreventativeSandbox()
        with pytest.raises(ValueError):
            sb.execute(lambda: (_ for _ in ()).throw(ValueError("x")))

    def test_get_status(self):
        sb = PreventativeSandbox()
        status = sb.get_status()
        assert isinstance(status, dict)

    def test_reset_sandbox(self):
        sb = PreventativeSandbox()
        sb.execute(lambda: 1)
        sb.reset()
        # After reset state should be clean
        status = sb.get_status()
        assert status.get("executions_since_reset", 0) == 0
