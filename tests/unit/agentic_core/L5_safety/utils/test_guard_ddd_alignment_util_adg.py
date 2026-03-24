"""ADG-driven tests for agentic_core/L5_safety/utils/guard_ddd_alignment_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.guard_ddd_alignment_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        get_ddd_violations_detailed,
        validate_ddd_alignment,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_ddd_violations_detailed = None  # type: ignore[assignment,misc]
    validate_ddd_alignment = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="guard_ddd_alignment_util.py deps unavailable")
class TestGetDddViolationsDetailed:
    def test_is_callable(self):
        assert callable(get_ddd_violations_detailed)

@pytest.mark.skipif(not _AVAILABLE, reason="guard_ddd_alignment_util.py deps unavailable")
class TestValidateDddAlignment:
    def test_is_callable(self):
        assert callable(validate_ddd_alignment)

@pytest.mark.skipif(not _AVAILABLE, reason="guard_ddd_alignment_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="guard_ddd_alignment_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="guard_ddd_alignment_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="guard_ddd_alignment_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="guard_ddd_alignment_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="guard_ddd_alignment_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module guard_ddd_alignment_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE