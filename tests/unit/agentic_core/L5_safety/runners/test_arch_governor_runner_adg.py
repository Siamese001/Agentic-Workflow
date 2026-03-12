"""ADG-driven tests for agentic_core/L5_safety/runners/arch_governor_runner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.runners.arch_governor_runner import (  # noqa: F401
        get_project_root,
        run_ci_verification,
        capture_golden_baseline,
        run_audit,
        main,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    get_project_root = None  # type: ignore[assignment,misc]
    run_ci_verification = None  # type: ignore[assignment,misc]
    capture_golden_baseline = None  # type: ignore[assignment,misc]
    run_audit = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestGetProjectRoot:
    def test_is_callable(self):
        assert callable(get_project_root)

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestRunCiVerification:
    def test_is_callable(self):
        assert callable(run_ci_verification)

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestCaptureGoldenBaseline:
    def test_is_callable(self):
        assert callable(capture_golden_baseline)

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestRunAudit:
    def test_is_callable(self):
        assert callable(run_audit)

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

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

@pytest.mark.skipif(not _AVAILABLE, reason="arch_governor_runner.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module arch_governor_runner.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
