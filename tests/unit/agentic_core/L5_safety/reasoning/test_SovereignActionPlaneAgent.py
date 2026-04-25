"""Surface coverage for `agentic_core.L5_safety.reasoning.SovereignActionPlaneAgent`.

Wave 3 of `.windsurf/plans/test-coverage-waves-f8f5a7.md`. L5 execution-surface
orchestrator. Fan-out=13. Sovereign action plane that gates execution.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.SovereignActionPlaneAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_public_classes_present(mod):
    for name in ("SovereignToolsmith", "SovereignSandbox", "SovereignActionPlaneAgent"):
        assert hasattr(mod, name), f"{name} missing"
        assert inspect.isclass(getattr(mod, name))


def test_public_factory_functions(mod):
    assert hasattr(mod, "create_sovereign_action_plane")
    assert callable(mod.create_sovereign_action_plane)
    assert hasattr(mod, "get_sovereign_action_plane")
    assert callable(mod.get_sovereign_action_plane)


def test_create_sovereign_action_plane_signature(mod):
    sig = inspect.signature(mod.create_sovereign_action_plane)
    assert "safety_layer" in sig.parameters
    assert "SignalLedger" in sig.parameters


def test_sovereign_action_plane_agent_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.SovereignActionPlaneAgent, SovereignBaseAgent)
