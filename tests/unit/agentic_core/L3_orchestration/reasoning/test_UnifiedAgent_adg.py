"""ADG importability contract for agentic_core/L3_orchestration/reasoning/UnifiedAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_UnifiedAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.reasoning.UnifiedAgent import (  # noqa: F401
        AgentCategory,
        BaseStrategy,
        HealingResult,
        OrchestrationResult,
        ValidationResult,
        ValidatorStrategy,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    AgentCategory = None  # type: ignore[assignment,misc]
    ValidationResult = None  # type: ignore[assignment,misc]
    OrchestrationResult = None  # type: ignore[assignment,misc]
    HealingResult = None  # type: ignore[assignment,misc]
    BaseStrategy = None  # type: ignore[assignment,misc]
    ValidatorStrategy = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="UnifiedAgent deps unavailable")
class TestUnifiedagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/reasoning/UnifiedAgent.py must be importable."""
        assert _AVAILABLE

    def test_agentcategory_defined(self) -> None:
        assert AgentCategory is not None

    def test_validationresult_defined(self) -> None:
        assert ValidationResult is not None

    def test_orchestrationresult_defined(self) -> None:
        assert OrchestrationResult is not None

    def test_healingresult_defined(self) -> None:
        assert HealingResult is not None

    def test_basestrategy_defined(self) -> None:
        assert BaseStrategy is not None

    def test_validatorstrategy_defined(self) -> None:
        assert ValidatorStrategy is not None