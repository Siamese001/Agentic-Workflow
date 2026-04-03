"""Benchmarking Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.benchmarking_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.benchmarking_util import (
    BenchmarkSuite as _BenchmarkSuite,
    BenchmarkResult as _BenchmarkResult,
    benchmark_function as _benchmark_function,
)


class BenchmarkResult:
    """DEPRECATED: Use benchmarking_util.BenchmarkResult instead."""
    
    def __init__(self, **kwargs):
        warnings.warn("BenchmarkResult is deprecated. Use benchmarking_util.BenchmarkResult instead.", DeprecationWarning)
        self._impl = _BenchmarkResult(**kwargs)


class BenchmarkSuite:
    """DEPRECATED: Use benchmarking_util.BenchmarkSuite instead."""
    
    def __init__(self, **kwargs):
        warnings.warn("BenchmarkSuite is deprecated. Use benchmarking_util.BenchmarkSuite instead.", DeprecationWarning)
        self._impl = _BenchmarkSuite(**kwargs)


class BenchmarkingAgent(SovereignBaseAgent):
    """
    DEPRECATED: Benchmarking Agent - now delegates to benchmarking_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L5_safety.utils.benchmarking_util directly.
    """

    def __init__(self):
        """Initialize BenchmarkingAgent (deprecated, use benchmarking_util instead)."""
        super().__init__(name="BenchmarkingAgent", layer="L5")

        warnings.warn(
            "BenchmarkingAgent is deprecated. Use agentic_core.L5_safety.utils.benchmarking_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def benchmark_function(self, func, *args, **kwargs) -> Any:
        """Benchmark a function call."""
        return _benchmark_function(func, args, kwargs)
