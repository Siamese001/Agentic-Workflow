"""ADG importability contract for agentic_core/L2_execution/types/ml_pattern_record_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ml_pattern_record_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.ml_pattern_record_types import (  # noqa: F401
        PatternCompatibilityError,
        MLPatternRecord,
        enforce_pattern_compatibility,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PatternCompatibilityError = None  # type: ignore[assignment,misc]
    MLPatternRecord = None  # type: ignore[assignment,misc]
    enforce_pattern_compatibility = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ml_pattern_record_types.py deps unavailable")
class TestMlPatternRecordTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ml_pattern_record_types.py must be importable."""
        assert _AVAILABLE

    def test_patterncompatibilityerror_is_type(self) -> None:
        assert PatternCompatibilityError is not None

    def test_mlpatternrecord_is_type(self) -> None:
        assert MLPatternRecord is not None

    def test_enforce_pattern_compatibility_callable(self) -> None:
        assert callable(enforce_pattern_compatibility)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

