"""Dep-graph regression gate.



Enforces non-growing bounds on import graph structural debt:

  - Cycle count must not exceed budget

  - Layer-inversion count must not exceed budget

  - Pinecone importer count must not exceed budget (shrinks as Pinecone is removed)

  - No new star-imports without __all__ in __init__.py files



Uses tools.dep_graph_db (NetworkX-backed) for accurate transitive queries.

Star-import check uses pure AST (no networkx needed for that gate).

"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT))


from tools.dep_graph_db import build as _build_dep_graph  # noqa: E402

# ---------------------------------------------------------------------------

# Budgets (current baselines — must only decrease, never increase)

# ---------------------------------------------------------------------------


CYCLE_BUDGET = 11  # current: 11  — target: 0 (was 13, -2 from Pinecone Wave 1)

INVERSION_BUDGET = 98  # current: 98  — target: 0 (was 100, -2 from Pinecone Wave 1)

PINECONE_BUDGET = 0  # current: 0   — Pinecone fully removed (Wave 1 complete)


# SSOT dirs scanned (for pure-AST star-import check only)

SSOT_DIRS = ["agentic_core", "apps_lic", "apps_rg", "apps_shared", "system_learning"]


# ---------------------------------------------------------------------------

# Shared fixture: build once per test class session

# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def dep_graph():
    """Build (or load cached) dep graph once for all tests in this module."""

    return _build_dep_graph(force=False)


# ---------------------------------------------------------------------------

# Tests

# ---------------------------------------------------------------------------


@pytest.mark.governance
class TestDepGraphRegression:
    """Import graph structural debt must not grow."""

    @pytest.fixture(autouse=True)
    def _load(self, dep_graph):
        self._dg = dep_graph

    def test_cycle_count_within_budget(self) -> None:
        """Import cycles must not exceed CYCLE_BUDGET."""

        cycles = self._dg.cycles()

        assert len(cycles) <= CYCLE_BUDGET, (
            f"Cycle count {len(cycles)} exceeds budget {CYCLE_BUDGET}. "
            f"New cycles introduced. First: {cycles[0] if cycles else 'none'}"
        )

    def test_layer_inversion_count_within_budget(self) -> None:
        """Layer inversions must not exceed INVERSION_BUDGET."""

        count = len(self._dg.layer_violations())

        assert count <= INVERSION_BUDGET, (
            f"Layer inversion count {count} exceeds budget {INVERSION_BUDGET}. "
            "A lower-layer module is now importing a higher-layer module."
        )

    def test_pinecone_importer_count_within_budget(self) -> None:
        """Pinecone transitive importers must be zero — Pinecone fully removed."""

        count = len(self._dg.pinecone_importers())

        assert count <= PINECONE_BUDGET, (
            f"Pinecone importer count {count} exceeds budget {PINECONE_BUDGET}. "
            "A new import path to Pinecone was introduced — revert it."
        )

    def test_no_new_pinecone_nodes(self) -> None:
        """No Pinecone nodes — Pinecone fully removed (Wave 1 complete)."""

        count = len(self._dg.pinecone_nodes())

        assert count == 0, (
            f"Pinecone node count is {count} (expected 0). A file directly imports Pinecone — remove it."
        )


@pytest.mark.governance
class TestStarImportAllShims:
    """__init__.py files with star-imports must declare __all__."""

    def test_no_unshimmed_star_imports_in_inits(self) -> None:
        """Any __init__.py doing 'from .X import *' must declare __all__."""

        violations: list[str] = []

        for d in SSOT_DIRS:
            scan_root = ROOT / d

            if not scan_root.exists():
                continue

            for py in scan_root.rglob("__init__.py"):
                try:
                    src = py.read_text(encoding="utf-8", errors="replace")

                    tree = ast.parse(src)

                except SyntaxError:
                    continue

                has_star = any(
                    isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names)
                    for n in ast.walk(tree)
                )

                has_all = any(
                    isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "__all__" for t in n.targets)
                    for n in ast.walk(tree)
                )

                if has_star and not has_all:
                    violations.append(str(py.relative_to(ROOT)))

        assert not violations, (
            f"__init__.py files with star-imports but no __all__ ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in sorted(violations))
        )
