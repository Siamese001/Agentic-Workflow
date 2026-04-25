"""Surface coverage for `agentic_core.L5_safety.reasoning.root_hygiene_healer`.

Wave 3 of `.windsurf/plans/test-coverage-waves-f8f5a7.md`. L5 write-surface
orchestrator — heals root-level hygiene violations (SSOT enforcement).
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.root_hygiene_healer"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_root_hygiene_agent_class_present(mod):
    assert hasattr(mod, "RootHygieneHealerAgent")
    assert inspect.isclass(mod.RootHygieneHealerAgent)


def test_get_project_root_returns_path(mod):
    assert hasattr(mod, "get_project_root")
    assert callable(mod.get_project_root)
    result = mod.get_project_root()
    assert isinstance(result, Path)
    assert result.is_absolute()


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.RootHygieneHealerAgent, SovereignBaseAgent)


def test_main_is_callable(mod):
    assert hasattr(mod, "main")
    assert callable(mod.main)
