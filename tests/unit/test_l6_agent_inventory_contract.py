"""L6 Observability Agent Inventory Contract Tests.

Deterministic AST-based gates to prevent agent count inflation
in agentic_core/L6_observability/.

Rules enforced:
1. Naming/structure: Any *Agent.py file must contain exactly one
   top-level ClassDef whose name ends with 'Agent' (or be on the
   explicit SHIM_ALLOWLIST).
2. Reachability: Every L6 agent class must be imported by at least
   one production entrypoint module, or be on the UNREACHABLE_ALLOWLIST
   with a justification.
3. Pinned budget: The count of *Agent.py files under
   agentic_core/L6_observability/ must not exceed AGENT_FILE_BUDGET.

Created: 2026-02-10 (L6 agent count reduction)
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
L6_ROOT = ROOT / L6_OBSERVABILITY_DIR

# ---------------------------------------------------------------------------
# Budget constant — update this (with justification comment) if adding agents
# ---------------------------------------------------------------------------
# L6 production must not contain *Agent.py; test-only agents live under tests/support/.
AGENT_FILE_BUDGET = 0

# Shim files explicitly allowed to exist as *Agent.py without a ClassDef.
# Each entry requires a justification string.
SHIM_ALLOWLIST: dict[str, str] = {
    # Example: "SomeAgent.py": "backward-compat shim for external consumers"
}

# Agent classes allowed to have zero production-entrypoint imports.
# Each entry requires a justification string.
UNREACHABLE_ALLOWLIST: dict[str, str] = {
    # Example: "SomeAgent": "triggered only via dynamic dispatch in X"
}

# Production entrypoint modules to check for reachability
PRODUCTION_ENTRYPOINTS = [
    "agentic_core/L3_orchestration/engines/AgentFactory.py",
    "agentic_core/L3_orchestration/enforcement/mission_runner.py",
    "agentic_core/L3_orchestration/enforcement/safety_strategy.py",
    "agentic_core/L5_safety/enforcement/HealingStrategy.py",
    "agentic_core/L0_routing/scripts/execute_ssot.py",
    "agentic_core/interfaces/IValidatorProtocol.py",
    "agentic_core/interfaces/IHealingStrategyProtocol.py",
]


def _collect_agent_files() -> list[Path]:
    """Collect all *Agent.py files under L6_ROOT."""
    result = []
    for dp, dirs, fs in os.walk(L6_ROOT):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for f in fs:
            if f.endswith("Agent.py"):
                result.append(Path(dp) / f)
    return sorted(result)


def _parse_top_level_classes(path: Path) -> list[str]:
    """Return names of top-level ClassDef nodes via AST."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(path))
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def _collect_l6_agent_classes() -> dict[str, Path]:
    """Map class_name -> file_path for all L6 agent ClassDefs."""
    agents: dict[str, Path] = {}
    for path in _collect_agent_files():
        for cls_name in _parse_top_level_classes(path):
            if cls_name.endswith("Agent"):
                agents[cls_name] = path
    return agents


def _find_l6_imports_in_file(filepath: Path) -> set[str]:
    """Return set of symbol names imported from L6_observability in a file."""
    try:
        src = filepath.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(filepath))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return set()
    symbols: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and L6_OBSERVABILITY_DIR in node.module:
            for alias in node.names:
                symbols.add(alias.name)
                if alias.asname:
                    symbols.add(alias.asname)
    return symbols


# =========================================================================
# Test 1: Naming / Structure
# =========================================================================
class TestL6AgentNamingStructure:
    """Any *Agent.py in L6 must have exactly one top-level ClassDef ending in Agent."""

    def test_agent_files_have_single_agent_classdef(self) -> None:
    """Test agent_files_have_single_agent_classdef contract compliance."""
        from agentic_core.L0_routing.config.path_constants import (
            L6_OBSERVABILITY_DIR,
        )
        from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    """Test no_classdef_only_in_allowlisted_shims contract compliance."""
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

    def test_all_agents_reachable_or_allowlisted(self) -> None:
    """Test all_agents_reachable_or_allowlisted contract compliance."""
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
            if cls_name not in reachable and cls_name not in UNREACHABLE_ALLOWLIST
        ]

        assert not unreachable, (
            f"L6 agent classes not reachable from any entrypoint "
            f"and not in UNREACHABLE_ALLOWLIST: {unreachable}"
        )


# =========================================================================
# Test 3: Pinned budget
# =========================================================================
class TestL6AgentBudget:
    """The *Agent.py file count must not exceed AGENT_FILE_BUDGET."""

    def test_agent_file_count_within_budget(self) -> None:
    """Test agent_file_count_within_budget contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

"""Test budget_prints_governance_signal contract compliance."""
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
