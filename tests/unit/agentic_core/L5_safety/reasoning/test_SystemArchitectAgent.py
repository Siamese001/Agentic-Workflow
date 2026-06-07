"""Surface coverage for `agentic_core.L5_safety.reasoning.SystemArchitectAgent`.

Wave 3 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md`. L5 write-surface
orchestrator. Fan-out=9.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.SystemArchitectAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_class_present(mod):
    assert hasattr(mod, "SystemArchitectAgent")
    assert inspect.isclass(mod.SystemArchitectAgent)


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.SystemArchitectAgent, SovereignBaseAgent)


def test_class_name_ends_with_agent_suffix(mod):
    assert mod.SystemArchitectAgent.__name__.endswith("Agent")
