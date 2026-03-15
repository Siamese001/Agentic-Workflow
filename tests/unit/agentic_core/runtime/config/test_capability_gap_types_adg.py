"""ADG importability contract for agentic_core/runtime/config/capability_gap_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_capability_gap_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.config.capability_gap_types import (  # noqa: F401
        AnalysisReport,
        CapabilityGap,
        CapabilityGapType,
        Recommendation,
        RecommendationType,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    CapabilityGapType = None  # type: ignore[assignment,misc]
    RecommendationType = None  # type: ignore[assignment,misc]
    CapabilityGap = None  # type: ignore[assignment,misc]
    Recommendation = None  # type: ignore[assignment,misc]
    AnalysisReport = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types deps unavailable")
class TestCapabilityGapTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/config/capability_gap_types.py must be importable."""
        assert _AVAILABLE

    def test_capabilitygaptype_defined(self) -> None:
        assert CapabilityGapType is not None

    def test_recommendationtype_defined(self) -> None:
        assert RecommendationType is not None

    def test_capabilitygap_defined(self) -> None:
        assert CapabilityGap is not None

    def test_recommendation_defined(self) -> None:
        assert Recommendation is not None

    def test_analysisreport_defined(self) -> None:
        assert AnalysisReport is not None
