"""Surface coverage for `agentic_core.L3_orchestration.reasoning.UnifiedAgent`.

Wave 4 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md`. L3 orchestration core.
The strategy registry that StructuralValidatorAgent and others delegate to.
Replaces the prior empty-body stub.
"""

from __future__ import annotations

import inspect
from enum import Enum

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L3_orchestration.reasoning.UnifiedAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports_declared(mod):
    assert hasattr(mod, "__all__")
    assert isinstance(mod.__all__, list)
    assert len(mod.__all__) >= 1


def test_unified_agent_class_present(mod):
    assert hasattr(mod, "UnifiedAgent")
    assert inspect.isclass(mod.UnifiedAgent)


@pytest.mark.parametrize(
    "name",
    [
        "AgentCategory",
        "ValidationResult",
        "OrchestrationResult",
        "HealingResult",
        "BaseStrategy",
        "ValidatorStrategy",
        "OrchestrationStrategy",
        "HealingStrategy",
        "GenericStrategy",
        "LocationHealingStrategy",
        "StructuralValidatorStrategy",
        "CodeValidatorStrategy",
        "StructureHealingStrategy",
    ],
)
def test_strategy_and_result_classes_present(mod, name):
    assert hasattr(mod, name), f"{name} missing"
    assert inspect.isclass(getattr(mod, name))


def test_agent_category_is_enum(mod):
    assert issubclass(mod.AgentCategory, Enum)
    members = list(mod.AgentCategory)
    assert len(members) >= 1


def test_unified_agent_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.UnifiedAgent, SovereignBaseAgent)


@pytest.mark.parametrize(
    "strat_cls",
    [
        "ValidatorStrategy",
        "OrchestrationStrategy",
        "HealingStrategy",
        "StructuralValidatorStrategy",
        "CodeValidatorStrategy",
    ],
)
def test_concrete_strategies_inherit_base_strategy(mod, strat_cls):
    assert issubclass(getattr(mod, strat_cls), mod.BaseStrategy)
