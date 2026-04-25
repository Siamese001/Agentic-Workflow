"""Tests for RuntimeInterceptor - runtime call interception and policy."""
import pytest
from unittest.mock import Mock
from agentic_core.L2_execution.enforcement.runtime_interceptor import RuntimeInterceptor


class TestRuntimeInterceptor:
    def test_init(self):
        ri = RuntimeInterceptor()
        assert ri is not None

    def test_intercept_call(self):
        ri = RuntimeInterceptor()
        target = Mock()
        target.method.return_value = "ok"
        ri.attach(target)
        result = target.method()
        assert result == "ok"

    def test_intercept_blocks_forbidden(self):
        ri = RuntimeInterceptor(forbidden_calls=["delete_all"])
        target = Mock()
        ri.attach(target)
        with pytest.raises(PermissionError):
            ri.intercept(target, "delete_all", args=(), kwargs={})

    def test_intercept_records_call(self):
        ri = RuntimeInterceptor()
        target = Mock()
        ri.attach(target)
        ri.intercept(target, "method", args=(1,), kwargs={})
        history = ri.get_call_history()
        assert len(history) >= 1

    def test_detach(self):
        ri = RuntimeInterceptor()
        target = Mock()
        ri.attach(target)
        ri.detach(target)
        assert target not in ri.attached_targets

    def test_add_policy(self):
        ri = RuntimeInterceptor()
        policy = Mock()
        ri.add_policy(policy)
        assert policy in ri.policies

    def test_policy_blocks_call(self):
        ri = RuntimeInterceptor()
        policy = Mock()
        policy.allows.return_value = False
        ri.add_policy(policy)
        target = Mock()
        with pytest.raises(PermissionError):
            ri.intercept(target, "method", args=(), kwargs={})

    def test_clear_history(self):
        ri = RuntimeInterceptor()
        target = Mock()
        ri.attach(target)
        ri.intercept(target, "method", args=(), kwargs={})
        ri.clear_history()
        assert len(ri.get_call_history()) == 0
