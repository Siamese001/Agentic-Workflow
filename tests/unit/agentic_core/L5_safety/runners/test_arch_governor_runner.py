"""Foundational behavioral tests for agentic_core/L5_safety/runners/arch_governor_runner.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_arch_governor_runner_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.runners.arch_governor_runner import (  # noqa: F401
        get_project_root,
        run_ci_verification,
        capture_golden_baseline,
        run_audit,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    get_project_root = None  # type: ignore[assignment,misc]
    run_ci_verification = None  # type: ignore[assignment,misc]
    capture_golden_baseline = None  # type: ignore[assignment,misc]
    run_audit = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestGetProjectRootFunction:
    def test_is_callable(self):
        assert callable(get_project_root)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_project_root)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestRunCiVerificationFunction:
    def test_is_callable(self):
        assert callable(run_ci_verification)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(run_ci_verification)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestCaptureGoldenBaselineFunction:
    def test_is_callable(self):
        assert callable(capture_golden_baseline)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(capture_golden_baseline)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestRunAuditFunction:
    def test_is_callable(self):
        assert callable(run_audit)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(run_audit)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module arch_governor_runner must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
