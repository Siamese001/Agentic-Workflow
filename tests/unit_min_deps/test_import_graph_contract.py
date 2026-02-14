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

ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = ROOT / "agentic_core"
SNAPSHOT_PATH = ROOT / "artifacts" / "structure" / "import_boundary_snapshot.json"

# Forbidden cross-territory edges
FORBIDDEN_TARGETS = frozenset({"ops_scripts", "dev_tools"})


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
        """agentic_core must not import from ops_scripts or dev_tools."""
        edges = _extract_import_edges()
        forbidden = _compute_forbidden_edges(edges)
        assert not forbidden, (
            f"Found {len(forbidden)} forbidden cross-territory import edge(s):\n"
            + "\n".join(f"  {src} → {tgt}" for src, tgt in forbidden)
        )

    def test_edge_hash_deterministic(self) -> None:
        """Two consecutive scans must produce identical hashes."""
        edges1 = _extract_import_edges()
        edges2 = _extract_import_edges()
        h1 = _hash_edges(edges1)
        h2 = _hash_edges(edges2)
        assert h1 == h2, f"Non-deterministic scan: {h1} != {h2}"

    def test_snapshot_persisted(self) -> None:
        """Snapshot file must exist and be valid JSON."""
        if not SNAPSHOT_PATH.exists():
            # Generate initial snapshot
            edges = _extract_import_edges()
            forbidden = _compute_forbidden_edges(edges)
            snapshot = {
                "edge_count": len(edges),
                "forbidden_edge_count": len(forbidden),
                "hash": _hash_edges(edges),
            }
            SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
            SNAPSHOT_PATH.write_text(
                json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
            )
        data = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        assert "edge_count" in data
        assert "forbidden_edge_count" in data
        assert "hash" in data

    def test_forbidden_edge_count_non_growing(self) -> None:
        """Forbidden edge count must not exceed snapshot ceiling (§29)."""
        if not SNAPSHOT_PATH.exists():
            pytest.skip("No snapshot yet — run test_snapshot_persisted first")
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        ceiling = snapshot["forbidden_edge_count"]
        edges = _extract_import_edges()
        current = len(_compute_forbidden_edges(edges))
        assert current <= ceiling, (
            f"Forbidden edge count grew: {current} > {ceiling} (ceiling from snapshot)"
        )

    def test_synthetic_forbidden_edge_detected(self, tmp_path: Path) -> None:
        """Negative test: prove scanner catches a synthetic forbidden edge."""
        fake_edges: list[tuple[str, str]] = [
            ("agentic_core/fake.py", "ops_scripts"),
        ]
        forbidden = _compute_forbidden_edges(fake_edges)
        assert len(forbidden) == 1, "Scanner failed to detect synthetic forbidden edge"
