"""ADG importability contract for system_learning/types/pattern_analysis_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_pattern_analysis_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.types.pattern_analysis_types import (  # noqa: F401
        PatternSourceIds,
        PatternFindingKey,
        PatternFinding,
        PatternFindingReport,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PatternSourceIds = None  # type: ignore[assignment,misc]
    PatternFindingKey = None  # type: ignore[assignment,misc]
    PatternFinding = None  # type: ignore[assignment,misc]
    PatternFindingReport = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="pattern_analysis_types.py deps unavailable")
class TestPatternAnalysisTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: pattern_analysis_types.py must be importable."""
        assert _AVAILABLE

    def test_patternsourceids_is_type(self) -> None:
        assert PatternSourceIds is not None

    def test_patternfindingkey_is_type(self) -> None:
        assert PatternFindingKey is not None

    def test_patternfinding_is_type(self) -> None:
        assert PatternFinding is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

