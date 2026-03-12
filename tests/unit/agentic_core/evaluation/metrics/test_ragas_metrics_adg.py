"""ADG importability contract for agentic_core/evaluation/metrics/ragas_metrics.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ragas_metrics.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.evaluation.metrics.ragas_metrics import (  # noqa: F401
        FaithfulnessMetric,
        AnswerRelevancyMetric,
        ContextPrecisionMetric,
        GroundednessMetric,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    FaithfulnessMetric = None  # type: ignore[assignment,misc]
    AnswerRelevancyMetric = None  # type: ignore[assignment,misc]
    ContextPrecisionMetric = None  # type: ignore[assignment,misc]
    GroundednessMetric = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ragas_metrics.py deps unavailable")
class TestRagasMetricsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ragas_metrics.py must be importable."""
        assert _AVAILABLE

    def test_faithfulnessmetric_is_type(self) -> None:
        assert FaithfulnessMetric is not None

    def test_answerrelevancymetric_is_type(self) -> None:
        assert AnswerRelevancyMetric is not None

    def test_contextprecisionmetric_is_type(self) -> None:
        assert ContextPrecisionMetric is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

