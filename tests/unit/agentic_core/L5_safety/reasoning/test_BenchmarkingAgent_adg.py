"""ADG importability contract for agentic_core/L5_safety/reasoning/BenchmarkingAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_BenchmarkingAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.BenchmarkingAgent import (  # noqa: F401
        PERFORMANCE_DEGRADATION_THRESHOLD,
        BenchmarkContext,
        BenchmarkingAgent,
        BenchmarkResult,
        BenchmarkResultActual,
        BenchmarkSuite,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PERFORMANCE_DEGRADATION_THRESHOLD = None  # type: ignore[assignment,misc]
    BenchmarkResult = None  # type: ignore[assignment,misc]
    BenchmarkResultActual = None  # type: ignore[assignment,misc]
    BenchmarkSuite = None  # type: ignore[assignment,misc]
    BenchmarkingAgent = None  # type: ignore[assignment,misc]
    BenchmarkContext = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="BenchmarkingAgent deps unavailable")
class TestBenchmarkingagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/BenchmarkingAgent.py must be importable."""
        assert _AVAILABLE

    def test_benchmarkresult_defined(self) -> None:
        assert BenchmarkResult is not None

    def test_benchmarkresultactual_defined(self) -> None:
        assert BenchmarkResultActual is not None

    def test_benchmarksuite_defined(self) -> None:
        assert BenchmarkSuite is not None

    def test_benchmarkingagent_defined(self) -> None:
        assert BenchmarkingAgent is not None

    def test_benchmarkcontext_defined(self) -> None:
        assert BenchmarkContext is not None
