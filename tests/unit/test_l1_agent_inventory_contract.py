"""
L1 Agent Inventory Contract Test

Hard gates to prevent L1 agent/module inflation:
1. Naming/structure: *Agent.py must contain exactly one top-level ClassDef ending in Agent
2. Reachability: Every L1 agent must be imported by >=1 non-test file OR be explicitly allow-listed
3. Pinned budget: Fail if L1 *Agent.py count exceeds baseline constant

Created: 2026-02-10 as part of L1 cleanup pass.
"""

from __future__ import annotations

import ast
import glob
import os

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

L1_ROOTS = glob.glob("agentic_core/L1_*")

# Pinned budget: current count after cleanup.  Bump ONLY with justification.
L1_AGENT_BUDGET = 3

# Allow-listed agents that are reachable but through indirect/dynamic dispatch
# rather than a direct `from agentic_core.L1_...` import in non-test code.
REACHABILITY_ALLOWLIST: set[str] = set()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_l1_agent_files() -> list[str]:
    """Return all *Agent.py files under agentic_core/L1_*/."""
    agent_files: list[str] = []
    for root in L1_ROOTS:
        for dirpath, _, filenames in os.walk(root):
            for fname in filenames:
                if fname.endswith("Agent.py"):
                    agent_files.append(os.path.join(dirpath, fname))
    return sorted(agent_files)


def _parse_top_level_classes(filepath: str) -> list[str]:
    """Return names of top-level ClassDef nodes via AST."""
    source = open(filepath, encoding="utf-8").read()
    tree = ast.parse(source, filename=filepath)
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def _collect_l1_imports_in_repo() -> dict[str, list[str]]:
    """
    AST-scan the entire repo for ``from agentic_core.L1_... import <Name>``
    statements.  Returns {class_name: [importing_file, ...]}.
    """
    hits: dict[str, list[str]] = {}
    for dirpath, _, filenames in os.walk("."):
        if ".git" in dirpath.split(os.sep):
            continue
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            filepath = os.path.join(dirpath, fname)
            try:
                tree = ast.parse(
                    open(filepath, encoding="utf-8").read(),
                    filename=filepath,
                )
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and "L1_" in node.module:
                    for alias in node.names:
                        hits.setdefault(alias.name, []).append(filepath)
    return hits


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

AGENT_FILES = _collect_l1_agent_files()


class TestL1NamingStructure:
    """Rule 1: Every *Agent.py must have exactly one top-level ClassDef ending in 'Agent'."""

    @pytest.mark.parametrize("agent_file", AGENT_FILES, ids=lambda p: os.path.basename(p))
    def test_single_agent_classdef(self, agent_file: str) -> None:
        classes = _parse_top_level_classes(agent_file)
        agent_classes = [c for c in classes if c.endswith("Agent")]
        assert len(agent_classes) >= 1, (
            f"{agent_file}: no top-level ClassDef ending in 'Agent'. Found classes: {classes}"
        )
        assert len(agent_classes) == 1, (
            f"{agent_file}: expected exactly 1 *Agent ClassDef, found {len(agent_classes)}: {agent_classes}"
        )


class TestL1Reachability:
    """Rule 2: Every L1 agent class must be imported by >=1 non-test file or allow-listed."""

    @pytest.fixture(scope="class")
    def import_index(self) -> dict[str, list[str]]:
        return _collect_l1_imports_in_repo()

    @pytest.mark.parametrize("agent_file", AGENT_FILES, ids=lambda p: os.path.basename(p))
    def test_agent_is_reachable(self, agent_file: str, import_index: dict[str, list[str]]) -> None:
        classes = _parse_top_level_classes(agent_file)
        agent_classes = [c for c in classes if c.endswith("Agent")]
        if not agent_classes:
            pytest.fail(f"No agent class in {agent_file}")

        agent_name = agent_classes[0]
        if agent_name in REACHABILITY_ALLOWLIST:
            return

        importers = import_index.get(agent_name, [])
        prod_importers = [p for p in importers if "tests" not in p.replace(os.sep, "/").split("/")]
        assert len(prod_importers) >= 1, (
            f"{agent_name} (in {agent_file}) has 0 non-test importers. "
            f"Either add a production import or add to REACHABILITY_ALLOWLIST with justification."
        )


class TestL1PinnedBudget:
    """Rule 3: L1 *Agent.py count must not exceed pinned budget."""

    def test_agent_count_within_budget(self) -> None:
        count = len(AGENT_FILES)
        assert count <= L1_AGENT_BUDGET, (
            f"L1 *Agent.py count ({count}) exceeds budget ({L1_AGENT_BUDGET}). "
            f"Files: {AGENT_FILES}. "
            f"If intentional, update L1_AGENT_BUDGET with justification."
        )

    def test_print_inventory(self) -> None:
        """Governance signal: print count, expected, delta."""
        count = len(AGENT_FILES)
        delta = count - L1_AGENT_BUDGET
        print(f"\n[L1 INVENTORY] count={count}  budget={L1_AGENT_BUDGET}  delta={delta}")
        for f in AGENT_FILES:
            print(f"  {f}")
