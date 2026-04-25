"""Surface coverage for `agentic_core.L5_safety.reasoning.AutonomyGuardianAgent`.

Wave 7 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L5
agent that gates autonomous decisions.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.AutonomyGuardianAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_class_present(mod):
    assert hasattr(mod, "AutonomyGuardianAgent")
    assert inspect.isclass(mod.AutonomyGuardianAgent)


def test_get_autonomy_guardian_callable(mod):
    assert hasattr(mod, "get_autonomy_guardian")
    assert callable(mod.get_autonomy_guardian)


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.AutonomyGuardianAgent, SovereignBaseAgent)
