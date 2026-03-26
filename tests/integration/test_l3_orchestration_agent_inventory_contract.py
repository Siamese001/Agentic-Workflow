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

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L3_ORCHESTRATION_DIR,
    OPS_SCRIPTS_DIR,
)
#  # MOVED: from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

ROOT = Path(__file__).resolve().parents[3]
L3_ROOT = ROOT / L3_ORCHESTRATION_DIR

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
    for dirpath, dirs, filenames in os.walk(L3_ROOT):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
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
                from agentic_core.L0_routing.config.path_constants import (
                from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
            """Test has_agent_classdef contract compliance."""
            # Arrange
            # TODO: Set up contract parties and terms
            contract_terms = {}  # Replace with actual contract terms

    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

"""Test no_empty_agent_file contract compliance."""
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
    """Scan all production .py files for imports from L3_orchestration *Agent modules.

    Returns dict: agent_class_name -> [list of importing file paths]
    """
    imports: dict[str, list[str]] = {}
    prod_dirs = [
        ROOT / AGENTIC_CORE_DIR,
        ROOT / APPS_SHARED_DIR,
        ROOT / APPS_RG_DIR,
        ROOT / APPS_LIC_DIR,
        ROOT / OPS_SCRIPTS_DIR,
    ]
    for prod_dir in prod_dirs:
        if not prod_dir.exists():
            continue
        for dirpath, dirs, filenames in os.walk(prod_dir):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for fname in filenames:
                if not fname.endswith(".py"):
                    continue
                fpath = Path(dirpath) / fname
                try:
                    tree = ast.parse(fpath.read_text(encoding="utf-8"), filename=str(fpath))
                except (SyntaxError, UnicodeDecodeError):
                    continue
                for node in ast.walk(tree):
                    if (
                        isinstance(node, ast.ImportFrom)
                        and node.module
                        and L3_ORCHESTRATION_DIR in node.module
                    ):
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
    """Test agent_reachable_or_allowlisted contract compliance."""
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
    """Test agent_count_within_budget contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
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
