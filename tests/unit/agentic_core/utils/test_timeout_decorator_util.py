"""Foundational behavioral tests for agentic_core/utils/timeout_decorator_util.py."""

from __future__ import annotations

from threading import Thread

import pytest


def test_module_importable():
    """Module timeout_decorator_util must be importable."""
    from agentic_core.utils import timeout_decorator_util

    assert timeout_decorator_util is not None


def test_timeout_zero_raises_value_error():
    """seconds=0 must raise ValueError before touching signal."""
    from agentic_core.utils.timeout_decorator_impl_util import timeout

    @timeout(0)
    def _fn() -> int:
        return 42

    with pytest.raises(ValueError, match="greater than zero"):
        _fn()


def test_timeout_negative_raises_value_error():
    """seconds<0 must raise ValueError."""
    from agentic_core.utils.timeout_decorator_impl_util import timeout

    @timeout(-1)
    def _fn() -> int:
        return 99

    with pytest.raises(ValueError):
        _fn()


def test_timeout_happy_path_returns_result():
    """Fast function completes before timeout and return value is preserved."""
    from agentic_core.utils.timeout_decorator_impl_util import timeout

    @timeout(5)
    def _fast() -> str:
        return "ok"

    assert _fast() == "ok"


def test_timeout_non_main_thread_runs_function():
    """In a non-main thread the SIGALRM guard is skipped; function still executes."""
    from agentic_core.utils.timeout_decorator_impl_util import timeout

    results: dict[str, object] = {}

    @timeout(5)
    def _fn() -> str:
        return "thread_ok"

    def _worker() -> None:
        results["val"] = _fn()

    t = Thread(target=_worker)
    t.start()
    t.join(timeout=3)
    assert results.get("val") == "thread_ok"
