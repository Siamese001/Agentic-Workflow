"""Hierarchy-scan coverage for StructureEnforcerAgent."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent


pytestmark = pytest.mark.unit


def test_scan_root_violations_flags_target_territory_files(tmp_path: Path) -> None:
    territory = tmp_path / "apps_rg"
    territory.mkdir(parents=True)
    stray = territory / "stray.py"
    stray.write_text("x = 1\n", encoding="utf-8")
    allowed = territory / "__init__.py"
    allowed.write_text("", encoding="utf-8")

    agent = StructureEnforcerAgent(project_root=tmp_path)
    results = agent.scan_root_violations(target_territory="apps_rg")

    assert results["violations_found"] == 1
    assert len(results["territory_root_files"]) == 1
    violation = results["territory_root_files"][0]
    assert violation["file"] == "stray.py"
    assert violation["path"].replace("\\", "/") == "apps_rg/stray.py"


def test_heal_repository_returns_clean_noop_when_tree_has_no_root_files(tmp_path: Path) -> None:
    territory = tmp_path / "apps_rg" / "runtime"
    territory.mkdir(parents=True)
    (territory / "module.py").write_text("x = 1\n", encoding="utf-8")

    agent = StructureEnforcerAgent(project_root=tmp_path)
    results = agent.heal_repository(dry_run=True, execute=False, target_territory="apps_rg")

    assert results["message"] == "No root violations to heal"
    assert results["violations"] == 0
    assert results["fixed"] == 0
