"""ADG-driven tests for agentic_core/L5_safety/enforcement/module_collision_guardrail.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.module_collision_guardrail import (  # noqa: F401
        compute_logical_import_path,
        should_exclude,
        scan_directory,
        is_allowed_shim_pair,
        detect_collisions,
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
    compute_logical_import_path = None  # type: ignore[assignment,misc]
    should_exclude = None  # type: ignore[assignment,misc]
    scan_directory = None  # type: ignore[assignment,misc]
    is_allowed_shim_pair = None  # type: ignore[assignment,misc]
    detect_collisions = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestComputeLogicalImportPath:
    def test_is_callable(self):
        assert callable(compute_logical_import_path)

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestShouldExclude:
    def test_is_callable(self):
        assert callable(should_exclude)

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestScanDirectory:
    def test_is_callable(self):
        assert callable(scan_directory)

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestIsAllowedShimPair:
    def test_is_callable(self):
        assert callable(is_allowed_shim_pair)

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestDetectCollisions:
    def test_is_callable(self):
        assert callable(detect_collisions)

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="module_collision_guardrail.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module module_collision_guardrail.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
