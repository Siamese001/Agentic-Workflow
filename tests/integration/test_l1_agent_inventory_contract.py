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

#  # MOVED: from agentic_core.L0_routing.config.path_constants import TESTS_DIR
#  # MOVED: from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

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
        for dirpath, dirs, filenames in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
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
    for dirpath, dirs, filenames in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
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
                from agentic_core.L0_routing.config.path_constants import TESTS_DIR
                from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
            """Test single_agent_classdef contract compliance."""
            # Arrange
            # TODO: Set up contract parties and terms
            contract_terms = {}  # Replace with actual contract terms

    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
    def import_index(self) -> dict[str, list[str]]:
        return _collect_l1_imports_in_repo()

    @pytest.mark.parametrize("agent_file", AGENT_FILES, ids=lambda p: os.path.basename(p))
    def test_agent_is_reachable(self, agent_file: str, import_index: dict[str, list[str]]) -> None:
    """Test agent_is_reachable contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
        )


class TestL1PinnedBudget:
    """Rule 3: L1 *Agent.py count must not exceed pinned budget."""

    def test_agent_count_within_budget(self) -> None:
    """Test agent_count_within_budget contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation
    """Test print_inventory contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
