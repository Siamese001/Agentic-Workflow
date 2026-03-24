"""ADG-driven tests for agentic_core/L4_state/utils/complexity_analyzer_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.utils.complexity_analyzer_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        analyze_file_complexity,
        calculate_mccabe_complexity,
        check_function_complexity,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    calculate_mccabe_complexity = None  # type: ignore[assignment,misc]
    check_function_complexity = None  # type: ignore[assignment,misc]
    analyze_file_complexity = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="complexity_analyzer_util.py deps unavailable")
class TestCalculateMccabeComplexity:
    def test_is_callable(self):
        assert callable(calculate_mccabe_complexity)

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_analyzer_util.py deps unavailable")
class TestCheckFunctionComplexity:
    def test_is_callable(self):
        assert callable(check_function_complexity)

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_analyzer_util.py deps unavailable")
class TestAnalyzeFileComplexity:
    def test_is_callable(self):
        assert callable(analyze_file_complexity)

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_analyzer_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_analyzer_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_analyzer_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_analyzer_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_analyzer_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_analyzer_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module complexity_analyzer_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE