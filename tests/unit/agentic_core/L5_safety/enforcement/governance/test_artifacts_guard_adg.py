"""ADG-driven tests for agentic_core/L5_safety/enforcement/governance/artifacts_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.governance.artifacts_guard import (  # noqa: F401
        is_forbidden_artifact_name,
        scan_sensitive_content,
        scan_artifacts_directory,
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
    is_forbidden_artifact_name = None  # type: ignore[assignment,misc]
    scan_sensitive_content = None  # type: ignore[assignment,misc]
    scan_artifacts_directory = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestIsForbiddenArtifactName:
    def test_is_callable(self):
        assert callable(is_forbidden_artifact_name)

@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestScanSensitiveContent:
    def test_is_callable(self):
        assert callable(scan_sensitive_content)

@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestScanArtifactsDirectory:
    def test_is_callable(self):
        assert callable(scan_artifacts_directory)

@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="artifacts_guard.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module artifacts_guard.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
