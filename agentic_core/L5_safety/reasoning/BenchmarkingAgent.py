"""Benchmarking Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L5_safety.utils.benchmarking_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.

AGENT-DELETION-AUTHORIZED: 2026-04-24 (W3.1 of agent-deprecation-migration-d7a3f2)
Authorization date: 2026-04-24
Archive-eligible date: 2026-07-23 (90-day cooling per constitutional \u00a73)
Consumers at authorization: 0 (verified via w3_verify_zero_consumers.py grep of
`from agentic_core.L5_safety.reasoning.BenchmarkingAgent import` and `import agentic_core.L5_safety.reasoning.BenchmarkingAgent` across live code,
excluding self and archives/ paths — zero hits).
Unique logic: none (pure delegation to agentic_core.L5_safety.utils.benchmarking_util per DEPRECATED docstring above).
Target archive path on or after eligibility date:
  archives/agents/2026-07-23/agentic_core__L5_safety__reasoning__BenchmarkingAgent.py
Cooling-timer artifact: artifacts/agent_deprecation/w3_BenchmarkingAgent.json
"""

from __future__ import annotations

import warnings
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.utils.benchmarking_util import (
    BenchmarkResult as _BenchmarkResult,
)
from agentic_core.L5_safety.utils.benchmarking_util import (
    BenchmarkSuite as _BenchmarkSuite,
)
from agentic_core.L5_safety.utils.benchmarking_util import (
    benchmark_function as _benchmark_function,
)


class BenchmarkResult:
    """DEPRECATED: Use benchmarking_util.BenchmarkResult instead."""

    def __init__(self, **kwargs):
        warnings.warn(
            "BenchmarkResult is deprecated. Use benchmarking_util.BenchmarkResult instead.",
            DeprecationWarning,
        )
        self._impl = _BenchmarkResult(**kwargs)


class BenchmarkSuite:
    """DEPRECATED: Use benchmarking_util.BenchmarkSuite instead."""

    def __init__(self, **kwargs):
        warnings.warn(
            "BenchmarkSuite is deprecated. Use benchmarking_util.BenchmarkSuite instead.", DeprecationWarning
        )
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
