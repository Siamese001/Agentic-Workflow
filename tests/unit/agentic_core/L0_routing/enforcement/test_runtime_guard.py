"""Runtime-hardened tests for ``runtime_guard``."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


@pytest.fixture(scope="module")
def runtime_guard_module():
    return pytest.importorskip("agentic_core.L0_routing.enforcement.runtime_guard")


class TestPublicRuntimeGuardSurface:
    def test_runtime_guard_returns_callable_decorator(self, enforcement_package):
        decorator = enforcement_package.runtime_guard("test_entry")

        assert callable(decorator)

    def test_runtime_guard_decorator_preserves_function_execution(self, enforcement_package):
        decorator = enforcement_package.runtime_guard("test_entry")

        @decorator
        def test_func():
            return "guarded"

        assert test_func() == "guarded"

    def test_assert_v15_guarded_is_callable(self, enforcement_package):
        assert callable(enforcement_package.assert_v15_guarded)


class TestRuntimeGuardContextVars:
    def test_active_guards_reset_after_exception(self, runtime_guard_module):
        entry_id = "test.reset.exception"
        assert entry_id not in runtime_guard_module._ACTIVE_GUARDS.get()

        def raising_fn():
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            runtime_guard_module._guarded_call(raising_fn, entry_id, (), {})

        assert entry_id not in runtime_guard_module._ACTIVE_GUARDS.get()

    def test_correlation_id_reset_after_normal_exit(self, runtime_guard_module):
        def ok_fn():
            return "ok"

        result = runtime_guard_module._guarded_call(ok_fn, "test.reset.ok", (), {})

        assert result == "ok"
        assert runtime_guard_module._get_correlation_id() is None

    def test_active_guards_set_during_call(self, runtime_guard_module):
        entry_id = "test.inside.guard"
        seen_inside: list[bool] = []

        def inspect_fn():
            seen_inside.append(entry_id in runtime_guard_module._ACTIVE_GUARDS.get())

        runtime_guard_module._guarded_call(inspect_fn, entry_id, (), {})

        assert seen_inside == [True]
        assert entry_id not in runtime_guard_module._ACTIVE_GUARDS.get()
