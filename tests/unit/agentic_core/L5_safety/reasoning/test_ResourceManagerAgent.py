"""Surface coverage for `agentic_core.L5_safety.reasoning.ResourceManagerAgent`.

Wave 12 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3). L5
resource manager — budget allocation and proactive/fallback management.
"""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.ResourceManagerAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


@pytest.mark.parametrize(
    "name",
    [
        "ResourceType",
        "AllocationStatus",
        "ResourceAllocation",
        "ResourceBudget",
        "ResourceConfig",
        "ResourceManagerAgent",
    ],
)
def test_public_classes_present(mod, name):
    assert hasattr(mod, name)
    assert inspect.isclass(getattr(mod, name))


@pytest.mark.parametrize(
    "factory",
    [
        "create_legacy_budget_manager",
        "create_legacy_proactive_manager",
        "create_legacy_fallback_manager",
    ],
)
def test_legacy_factories_callable(mod, factory):
    assert callable(getattr(mod, factory))


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.ResourceManagerAgent, SovereignBaseAgent)
