"""Coverage Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L3_orchestration.utils.coverage_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L3_orchestration.utils.coverage_util import (
    CoverageMetrics,
)
from agentic_core.L3_orchestration.utils.coverage_util import (
    calculate_coverage_metrics as _calculate_coverage_metrics,
)
from agentic_core.L3_orchestration.utils.coverage_util import (
    compute_proportions as _compute_proportions,
)
from agentic_core.L3_orchestration.utils.coverage_util import (
    shannon_entropy as _shannon_entropy,
)


class CoverageAgent(SovereignBaseAgent):
    """
    DEPRECATED: Coverage Agent - now delegates to coverage_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L3_orchestration.utils.coverage_util directly.
    """

    def __init__(self):
        """Initialize CoverageAgent (deprecated, use coverage_util instead)."""
        super().__init__(name="CoverageAgent", layer="L3")

        warnings.warn(
            "CoverageAgent is deprecated. Use agentic_core.L3_orchestration.utils.coverage_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def calculate_coverage_metrics(self, layer_counts: dict[str, int], threshold_entropy: float = 2.2) -> CoverageMetrics:
        """Calculate coverage metrics for layer distribution."""
        return _calculate_coverage_metrics(layer_counts, threshold_entropy)

    def compute_proportions(self, counts: dict[str, int]) -> dict[str, float]:
        """Compute layer activation proportions."""
        return _compute_proportions(counts)

    def shannon_entropy(self, probabilities: list[float]) -> float:
        """Calculate Shannon entropy for a probability distribution."""
        return _shannon_entropy(probabilities)

    def analyze_coverage(self, layer_data: dict[str, int], threshold: float = 2.2) -> dict[str, Any]:
        """Analyze layer coverage and return structured results."""
        metrics = _calculate_coverage_metrics(layer_data, threshold)
        return {
            "total_layers": metrics.total_layers,
            "active_layers": metrics.active_layers,
            "entropy": metrics.entropy,
            "entropy_ratio": metrics.entropy_ratio,
            "is_balanced": metrics.is_balanced,
            "underrepresented": metrics.underrepresented_layer,
            "proportions": metrics.proportions,
        }
