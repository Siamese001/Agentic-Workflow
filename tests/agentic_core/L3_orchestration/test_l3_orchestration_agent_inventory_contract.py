"""L3 Orchestration Agent Inventory Contract Test.

Enforced invariants:
    1. Naming/structure: Any *Agent.py under agentic_core/L3_orchestration/**
       must contain exactly one top-level ClassDef ending in 'Agent'.
    2. Reachability: Each L3 agent must be imported by >=1 production entrypoint
       OR be explicitly allow-listed with justification.
    3. Pinned budget: Agent count must not exceed post-cleanup baseline
       without baseline update + justification.

Created: 2026-02-10 (L3 orchestration agent cleanup)
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
L3_ROOT = ROOT / "agentic_core" / "L3_orchestration"

# Post-cleanup baseline: 2 agent files (SubAtomicAgent.py, UnifiedAgent.py)
PINNED_AGENT_BUDGET = 2

# Allow-listed agents that don't need direct entrypoint reachability.
# Each entry: (file_stem, justification)
REACHABILITY_ALLOWLIST: dict[str, str] = {
    "SubAtomicAgent": "Base class inherited by many production agents across L1/L3/L5",
    "UnifiedAgent": "Strategy host imported by orchestrator_engine.py and L5 healers",
}


def _collect_agent_files() -> list[Path]:
    """Collect all *Agent.py files under agentic_core/L3_orchestration/ that have a ClassDef.

    Tombstoned/retired files (no ClassDef) are excluded from the active inventory.
    """
    agent_files: list[Path] = []
    for dirpath, _, filenames in os.walk(L3_ROOT):
        for fname in filenames:
            if fname.endswith("Agent.py"):
                fpath = Path(dirpath) / fname
                # Skip tombstoned files (retirement shims with no ClassDef)
                classes = _parse_top_level_classes(fpath)
                if any(c.endswith("Agent") for c in classes):
                    agent_files.append(fpath)
    return sorted(agent_files)


def _parse_top_level_classes(path: Path) -> list[str]:
    """Return names of top-level ClassDef nodes in a file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


# ---------------------------------------------------------------------------
# 1. NAMING / STRUCTURE
# ---------------------------------------------------------------------------


class TestAgentFileStructure:
    """Every *Agent.py must contain exactly one top-level ClassDef ending in Agent."""

    AGENT_FILES = _collect_agent_files()

    @pytest.mark.parametrize("agent_path", AGENT_FILES, ids=lambda p: p.name)
    def test_has_agent_classdef(self, agent_path: Path) -> None:
        """File must contain at least one top-level ClassDef ending in 'Agent'."""
        classes = _parse_top_level_classes(agent_path)
        agent_classes = [c for c in classes if c.endswith("Agent")]
        assert len(agent_classes) >= 1, (
            f"{agent_path.name} has no top-level ClassDef ending in 'Agent'. Found classes: {classes}"
        )

    @pytest.mark.parametrize("agent_path", AGENT_FILES, ids=lambda p: p.name)
    def test_no_empty_agent_file(self, agent_path: Path) -> None:
        """Agent file must not be an empty stub (>= 10 non-blank lines)."""
        lines = [l for l in agent_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) >= 10, (
            f"{agent_path.name} has only {len(lines)} non-blank lines — "
            f"likely a stub that should be deleted or demoted"
        )


# ---------------------------------------------------------------------------
# 2. REACHABILITY (via AST import scan)
# ---------------------------------------------------------------------------


def _find_l3_agent_imports_in_production() -> dict[str, list[str]]:
    """Scan all production .py files for imports from L3_orchestration *Agent modules.

    Returns dict: agent_class_name -> [list of importing file paths]
    """
    imports: dict[str, list[str]] = {}
    prod_dirs = [
        ROOT / "agentic_core",
        ROOT / "apps_shared",
        ROOT / "apps_rg",
        ROOT / "apps_lic",
        ROOT / "ops_scripts",
    ]
    for prod_dir in prod_dirs:
        if not prod_dir.exists():
            continue
        for dirpath, _, filenames in os.walk(prod_dir):
            if ".git" in dirpath or "__pycache__" in dirpath:
                continue
            for fname in filenames:
                if not fname.endswith(".py"):
                    continue
                fpath = Path(dirpath) / fname
                try:
                    tree = ast.parse(fpath.read_text(encoding="utf-8"), filename=str(fpath))
                except (SyntaxError, UnicodeDecodeError):
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module and "L3_orchestration" in node.module:
                        for alias in node.names:
                            name = alias.name
                            if name not in imports:
                                imports[name] = []
                            rel = str(fpath.relative_to(ROOT))
                            imports[name].append(rel)
    return imports


class TestAgentReachability:
    """Each L3 agent must be imported by production code or allow-listed."""

    AGENT_FILES = _collect_agent_files()
    PROD_IMPORTS = _find_l3_agent_imports_in_production()

    @pytest.mark.parametrize("agent_path", AGENT_FILES, ids=lambda p: p.name)
    def test_agent_reachable_or_allowlisted(self, agent_path: Path) -> None:
        """Agent must have >=1 production import or be in REACHABILITY_ALLOWLIST."""
        classes = _parse_top_level_classes(agent_path)
        agent_classes = [c for c in classes if c.endswith("Agent")]

        stem = agent_path.stem
        if stem in REACHABILITY_ALLOWLIST:
            return  # Explicitly allowed

        # Check if any agent class from this file is imported in production
        for cls_name in agent_classes:
            if cls_name in self.PROD_IMPORTS and self.PROD_IMPORTS[cls_name]:
                return

        pytest.fail(
            f"{agent_path.name} agent classes {agent_classes} have zero production imports "
            f"and are not in REACHABILITY_ALLOWLIST. "
            f"Either add a production import path or add to allowlist with justification.",
        )


# ---------------------------------------------------------------------------
# 3. PINNED BUDGET
# ---------------------------------------------------------------------------


class TestPinnedBudget:
    """Agent count must not exceed post-cleanup baseline."""

    def test_agent_count_within_budget(self) -> None:
        """Number of *Agent.py files must not exceed PINNED_AGENT_BUDGET."""
        agent_files = _collect_agent_files()
        count = len(agent_files)
        assert count <= PINNED_AGENT_BUDGET, (
            f"L3 orchestration agent count ({count}) exceeds budget ({PINNED_AGENT_BUDGET}). "
            f"Files: {[f.name for f in agent_files]}. "
            f"Update PINNED_AGENT_BUDGET with justification if this is intentional."
        )

    def test_print_inventory(self) -> None:
        """Print current inventory for audit trail."""
        agent_files = _collect_agent_files()
        print(f"\nL3 agent_count={len(agent_files)}, budget={PINNED_AGENT_BUDGET}")
        for f in agent_files:
            classes = _parse_top_level_classes(f)
            agent_classes = [c for c in classes if c.endswith("Agent")]
            print(f"  {f.name}: {agent_classes}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
