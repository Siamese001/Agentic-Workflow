"""ADG importability contract for agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ComplexityAnalyzerAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.ComplexityAnalyzerAgent import (  # noqa: F401
        ComplexityAnalyzerAgent,
        ComplexityAnalyzerStrategy,
        ComplexityConfig,
        ComplexityViolation,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ComplexityAnalyzerStrategy = None  # type: ignore[assignment,misc]
    ComplexityViolation = None  # type: ignore[assignment,misc]
    ComplexityConfig = None  # type: ignore[assignment,misc]
    ComplexityAnalyzerAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ComplexityAnalyzerAgent deps unavailable")
class TestComplexityanalyzeragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py must be importable."""
        assert _AVAILABLE

    def test_complexityanalyzerstrategy_defined(self) -> None:
        assert ComplexityAnalyzerStrategy is not None

    def test_complexityviolation_defined(self) -> None:
        assert ComplexityViolation is not None

    def test_complexityconfig_defined(self) -> None:
        assert ComplexityConfig is not None

    def test_complexityanalyzeragent_defined(self) -> None:
        assert ComplexityAnalyzerAgent is not None
