"""Surface coverage for `agentic_core.L5_safety.reasoning.InterfaceBoundaryAgent`.

Wave 6 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.InterfaceBoundaryAgent"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_class_present(mod):
    assert hasattr(mod, "InterfaceBoundaryAgent")
    assert inspect.isclass(mod.InterfaceBoundaryAgent)


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.InterfaceBoundaryAgent, SovereignBaseAgent)


def test_class_name_ends_with_agent_suffix(mod):
    assert mod.InterfaceBoundaryAgent.__name__.endswith("Agent")
