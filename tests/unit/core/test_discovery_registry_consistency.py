"""Unit tests for discovery ↔ registry consistency.

Covers at least 5 representative mappings to prove:
  - canonical_file exists
  - canonical_class is in canonical_file (AST)
  - no shim references among active records

Hardening V2 — Outcome A.
"""

from __future__ import annotations

import ast

import pytest

from agentic_core.L0_maintenance.scripts.full_agent_discovery import (
    perform_deep_integrity_scan,
)
from agentic_core.L0_maintenance.utils.ssot_discovery_util import (
    load_agent_discovery,
)
from agentic_core.L5_safety.config.structure_blueprint_config import (
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()


@pytest.fixture(scope="module")
def verified_agents():
    raw = load_agent_discovery(PROJECT_ROOT, force_reload=True)
    verified, _stats = perform_deep_integrity_scan(raw, PROJECT_ROOT)
    return verified


REPRESENTATIVE_AGENTS = [
    "BenchmarkingAgent",
    "ASTValidatorAgent",
    "HierarchyAgent",
    "FilesystemSSOTReconcilerAgent",
    "SovereignCognitivePlaneAgent",
]


def _find_agent(agents: list[dict], class_name: str) -> dict | None:
    for a in agents:
        if a.get("canonical_class") == class_name:
            return a
    return None


class TestRepresentativeMappings:
    """Verify 5 representative executor agents resolve correctly."""

    @pytest.mark.parametrize("class_name", REPRESENTATIVE_AGENTS)
    def test_canonical_file_exists(self, verified_agents, class_name):
        agent = _find_agent(verified_agents, class_name)
        assert agent is not None, f"{class_name} not found in verified agents"
        canon_file = agent.get("canonical_file", "")
        assert canon_file, f"{class_name}: canonical_file is empty"
        full_path = PROJECT_ROOT / canon_file
        assert full_path.is_file(), f"{class_name}: {canon_file} does not exist"

    @pytest.mark.parametrize("class_name", REPRESENTATIVE_AGENTS)
    def test_canonical_class_in_file_ast(self, verified_agents, class_name):
        agent = _find_agent(verified_agents, class_name)
        assert agent is not None
        canon_file = agent["canonical_file"]
        full_path = PROJECT_ROOT / canon_file
        source = full_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(full_path))
        ast_classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        assert class_name in ast_classes, f"{class_name} not in AST of {canon_file} (found: {ast_classes})"

    @pytest.mark.parametrize("class_name", REPRESENTATIVE_AGENTS)
    def test_not_shim_reference(self, verified_agents, class_name):
        agent = _find_agent(verified_agents, class_name)
        assert agent is not None
        canon_file = agent["canonical_file"]
        full_path = PROJECT_ROOT / canon_file
        source = full_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(full_path))
        class_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
        assert class_count > 0, f"{canon_file} is a shim (0 ClassDefs)"


class TestAllActiveConsistent:
    """Full sweep: every active agent must pass consistency."""

    def test_no_missing_files(self, verified_agents):
        missing = [
            a.get("canonical_class", "?")
            for a in verified_agents
            if not (PROJECT_ROOT / a.get("canonical_file", "NONEXISTENT")).is_file()
        ]
        assert not missing, f"{len(missing)} agents with missing files: {missing[:10]}"

    def test_no_shim_references(self, verified_agents):
        shims = []
        for a in verified_agents:
            cf = a.get("canonical_file", "")
            if not cf:
                continue
            fp = PROJECT_ROOT / cf
            if not fp.is_file():
                continue
            try:
                src = fp.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src)
            except SyntaxError:
                continue
            if not any(isinstance(n, ast.ClassDef) for n in ast.walk(tree)):
                shims.append(a.get("canonical_class", "?"))
        assert not shims, f"{len(shims)} agents point to shim files: {shims[:10]}"
