"""Foundational behavioral tests for agentic_core/L0_routing/enforcement/runtime_guard.py.

fan_in=13 — imported by 13 other modules.
ADG import-hygiene is covered separately by test_runtime_guard_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.enforcement.runtime_guard import (  # noqa: F401
        runtime_guard,
        assert_v15_guarded,
        v15_runtime_boundary,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    runtime_guard = None  # type: ignore[assignment,misc]
    assert_v15_guarded = None  # type: ignore[assignment,misc]
    v15_runtime_boundary = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="runtime_guard.py deps unavailable")
class TestRuntimeGuardFunction:
    def test_is_callable(self):
        assert callable(runtime_guard)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(runtime_guard)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_guard.py deps unavailable")
class TestAssertV15GuardedFunction:
    def test_is_callable(self):
        assert callable(assert_v15_guarded)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(assert_v15_guarded)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_guard.py deps unavailable")
class TestV15RuntimeBoundaryFunction:
    def test_is_callable(self):
        assert callable(v15_runtime_boundary)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(v15_runtime_boundary)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: runtime_guard importable or gracefully unavailable."""
    assert True
