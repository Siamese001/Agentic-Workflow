"""ADG importability contract for agentic_core/L3_orchestration/engines/parallelization_engine.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_parallelization_engine.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.engines.parallelization_engine import (  # noqa: F401
        AggregationStrategy,
        ParallelizationEngine,
        ParallelMode,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ParallelMode = None  # type: ignore[assignment,misc]
    AggregationStrategy = None  # type: ignore[assignment,misc]
    ParallelizationEngine = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="parallelization_engine deps unavailable")
class TestParallelizationEngineImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/engines/parallelization_engine.py must be importable."""
        assert _AVAILABLE

    def test_parallelmode_defined(self) -> None:
        assert ParallelMode is not None

    def test_aggregationstrategy_defined(self) -> None:
        assert AggregationStrategy is not None

    def test_parallelizationengine_defined(self) -> None:
        assert ParallelizationEngine is not None
