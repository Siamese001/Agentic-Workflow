"""Surface coverage for `agentic_core.L5_safety.reasoning.hierarchy_healer`.

Wave 3 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md`. L5 write-surface
orchestrator — heals file hierarchy violations. Fan-out=12.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L5_safety.reasoning.hierarchy_healer"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_hierarchy_healer_class_present(mod):
    assert hasattr(mod, "HierarchyHealerAgent")
    assert inspect.isclass(mod.HierarchyHealerAgent)


def test_get_hierarchy_agent_callable(mod):
    assert hasattr(mod, "get_hierarchy_agent")
    assert callable(mod.get_hierarchy_agent)


def test_inherits_sovereign_base(mod):
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    assert issubclass(mod.HierarchyHealerAgent, SovereignBaseAgent)


def test_get_hierarchy_agent_signature_accepts_project_root(mod):
    sig = inspect.signature(mod.get_hierarchy_agent)
    assert "project_root" in sig.parameters


def test_scan_root_violations_flags_target_territory_files(mod, tmp_path: Path) -> None:
    territory = tmp_path / "apps_rg"
    territory.mkdir(parents=True)
    stray = territory / "stray.py"
    stray.write_text("x = 1\n", encoding="utf-8")

    agent = mod.HierarchyHealerAgent(project_root=tmp_path)
    results = agent.scan_root_violations(target_territory="apps_rg")

    assert results["violations_found"] == 1
    assert len(results["territory_root_files"]) == 1
    violation = results["territory_root_files"][0]
    assert violation["file"] == "stray.py"
    assert violation["path"].replace("\\", "/") == "apps_rg/stray.py"


def test_heal_root_violations_returns_noop_when_tree_is_clean(mod, tmp_path: Path) -> None:
    agent = mod.HierarchyHealerAgent(project_root=tmp_path)

    results = agent.heal_root_violations(dry_run=True)

    assert results["message"] == "No root violations to heal"
    assert results["archived_files_moved"] == 0
    assert results["territory_files_relocated"] == 0
