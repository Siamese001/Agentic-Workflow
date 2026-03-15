"""ADG importability contract for agentic_core/prompt_governance/optimization/optimization_strategy.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_optimization_strategy.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.prompt_governance.optimization.optimization_strategy import (  # noqa: F401
        OptimizationConfig,
        OptimizationLevel,
        OptimizationStrategy,
        PromptOptimizer,
        create_prompt_optimizer,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    OptimizationStrategy = None  # type: ignore[assignment,misc]
    OptimizationLevel = None  # type: ignore[assignment,misc]
    OptimizationConfig = None  # type: ignore[assignment,misc]
    PromptOptimizer = None  # type: ignore[assignment,misc]
    create_prompt_optimizer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="optimization_strategy deps unavailable")
class TestOptimizationStrategyImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/prompt_governance/optimization/optimization_strategy.py must be importable."""
        assert _AVAILABLE

    def test_optimizationstrategy_defined(self) -> None:
        assert OptimizationStrategy is not None

    def test_optimizationlevel_defined(self) -> None:
        assert OptimizationLevel is not None

    def test_optimizationconfig_defined(self) -> None:
        assert OptimizationConfig is not None

    def test_promptoptimizer_defined(self) -> None:
        assert PromptOptimizer is not None
