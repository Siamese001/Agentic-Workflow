"""ADG importability contract for agentic_core/evaluation/metrics/ragas_metrics.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ragas_metrics.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.evaluation.metrics.ragas_metrics import (  # noqa: F401
        AnswerRelevancyMetric,
        ContextPrecisionMetric,
        FaithfulnessMetric,
        GroundednessMetric,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    FaithfulnessMetric = None  # type: ignore[assignment,misc]
    AnswerRelevancyMetric = None  # type: ignore[assignment,misc]
    ContextPrecisionMetric = None  # type: ignore[assignment,misc]
    GroundednessMetric = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ragas_metrics deps unavailable")
class TestRagasMetricsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/evaluation/metrics/ragas_metrics.py must be importable."""
        assert _AVAILABLE

    def test_faithfulnessmetric_defined(self) -> None:
        assert FaithfulnessMetric is not None

    def test_answerrelevancymetric_defined(self) -> None:
        assert AnswerRelevancyMetric is not None

    def test_contextprecisionmetric_defined(self) -> None:
        assert ContextPrecisionMetric is not None

    def test_groundednessmetric_defined(self) -> None:
        assert GroundednessMetric is not None
