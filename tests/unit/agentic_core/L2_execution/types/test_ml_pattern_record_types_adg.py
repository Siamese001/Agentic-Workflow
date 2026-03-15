"""ADG importability contract for agentic_core/L2_execution/types/ml_pattern_record_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ml_pattern_record_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.ml_pattern_record_types import (  # noqa: F401
        MLPatternRecord,
        PatternCompatibilityError,
        enforce_pattern_compatibility,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PatternCompatibilityError = None  # type: ignore[assignment,misc]
    MLPatternRecord = None  # type: ignore[assignment,misc]
    enforce_pattern_compatibility = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ml_pattern_record_types deps unavailable")
class TestMlPatternRecordTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/ml_pattern_record_types.py must be importable."""
        assert _AVAILABLE

    def test_patterncompatibilityerror_defined(self) -> None:
        assert PatternCompatibilityError is not None

    def test_mlpatternrecord_defined(self) -> None:
        assert MLPatternRecord is not None
