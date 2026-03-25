"""ADG importability contract for agentic_core/evaluation/metrics/ragas_metrics.py."""
from __future__ import annotations

import agentic_core.evaluation.metrics.ragas_metrics  # noqa: F401


def test_module_importable():
    """Module ragas_metrics must be importable."""
    assert agentic_core.evaluation.metrics.ragas_metrics is not None
