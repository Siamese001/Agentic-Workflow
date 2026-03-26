"""
Structural invariant: cross-territory import edges must not grow.

AST-based deterministic scan of agentic_core imports.
Enforces:
  - No agentic_core → ops_scripts edges
  - Cross-layer edge count is bounded (non-growing debt per §29)
  - Snapshot is deterministic across runs
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    OPS_SCRIPTS_DIR,
)

ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = ROOT / AGENTIC_CORE_DIR
SNAPSHOT_PATH = ROOT / "artifacts" / "structure" / "import_boundary_snapshot.json"

# Forbidden cross-territory edges
FORBIDDEN_TARGETS = frozenset({OPS_SCRIPTS_DIR, "dev_tools"})


def _extract_import_edges() -> list[tuple[str, str]]:
    """Extract all (source_module, target_top_package) edges from agentic_core."""
    edges: list[tuple[str, str]] = []
    for py_file in AGENTIC_CORE.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        rel = str(py_file.relative_to(ROOT)).replace("\\", "/")
        for node in ast.walk(tree):
            target: str | None = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name:
                        target = alias.name.split(".")[0]
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    target = node.module.split(".")[0]
            if target and target not in {"__future__"}:
                edges.append((rel, target))
    return sorted(set(edges))


def _compute_forbidden_edges(edges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Filter edges to only forbidden cross-territory imports."""
    return [(src, tgt) for src, tgt in edges if tgt in FORBIDDEN_TARGETS]


def _hash_edges(edges: list[tuple[str, str]]) -> str:
    """Deterministic SHA256 hash of sorted edge list."""
    content = json.dumps(edges, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class TestImportGraphContract:
    """Hard gate: import graph must not contain forbidden edges."""

    def test_no_forbidden_cross_territory_edges(self) -> None:
        from agentic_core.L0_routing.config.path_constants import (
    """Test no_forbidden_cross_territory_edges contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

"""Test edge_hash_deterministic contract compliance."""
# Arrange
# TODO: Set up contract parties and terms
contract_terms = {}  # Replace with actual contract terms

# Act
# TODO: Execute contract operations
contract_result = None  # Replace with actual contract operation
"""Test snapshot_persisted contract compliance."""
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
        assert "forbidden_edge_count" in data
        assert "hash" in data

    def test_forbidden_edge_count_non_growing(self) -> None:
    """Test forbidden_edge_count_non_growing contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    """Test synthetic_forbidden_edge_detected contract compliance."""
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
