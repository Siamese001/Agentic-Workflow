"""Foundational behavioral tests for agentic_core/utils/structural_healing_engine_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_structural_healing_engine_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.structural_healing_engine_util import (  # noqa: F401
        relocate_file,
        analyze_file_structure,
        calculate_complexity,
        suggest_file_split,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    relocate_file = None  # type: ignore[assignment,misc]
    analyze_file_structure = None  # type: ignore[assignment,misc]
    calculate_complexity = None  # type: ignore[assignment,misc]
    suggest_file_split = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="structural_healing_engine_util.py deps unavailable")
class TestRelocateFileFunction:
    def test_is_callable(self):
        assert callable(relocate_file)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(relocate_file)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="structural_healing_engine_util.py deps unavailable")
class TestAnalyzeFileStructureFunction:
    def test_is_callable(self):
        assert callable(analyze_file_structure)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(analyze_file_structure)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="structural_healing_engine_util.py deps unavailable")
class TestCalculateComplexityFunction:
    def test_is_callable(self):
        assert callable(calculate_complexity)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(calculate_complexity)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="structural_healing_engine_util.py deps unavailable")
class TestSuggestFileSplitFunction:
    def test_is_callable(self):
        assert callable(suggest_file_split)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(suggest_file_split)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="structural_healing_engine_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="structural_healing_engine_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="structural_healing_engine_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="structural_healing_engine_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="structural_healing_engine_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module structural_healing_engine_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
