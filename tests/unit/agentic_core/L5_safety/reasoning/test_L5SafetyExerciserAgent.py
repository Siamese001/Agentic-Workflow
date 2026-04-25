"""Surface coverage for `agentic_core.L5_safety.reasoning.L5SafetyExerciserAgent`.

Wave 3 of `.windsurf/plans/test-coverage-waves-f8f5a7.md`. L5 orchestrator —
exercises the safety plane end-to-end. Fan-out=8.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.L5SafetyExerciserAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_exerciser_class_present(mod):
    assert hasattr(mod, "L5SafetyExerciserAgent")
    assert inspect.isclass(mod.L5SafetyExerciserAgent)


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.L5SafetyExerciserAgent, SovereignBaseAgent)


@pytest.mark.parametrize(
    "private_factory",
    [
        "_get_layer_entry",
        "_get_hierarchy_agent",
        "_get_naming_agent",
        "_get_import_agent",
        "_get_RedTeamAgent",
        "_get_healer_agent",
    ],
)
def test_lazy_factory_helpers_callable(mod, private_factory):
    """Lazy factories must remain callable (avoid import-time blow-up)."""
    fn = getattr(mod, private_factory, None)
    assert callable(fn), f"{private_factory} must be callable"


def test_log_event_callable(mod):
    assert callable(mod.log_event)
