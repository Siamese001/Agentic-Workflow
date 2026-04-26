"""Phase 8 — ADG / GraphRAG substrate boundary tests."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
    InMemoryGraphAdapter,
    SubstrateViolation,
    assert_no_direct_sqlite_traversal,
    run_graph_traverse,
    sqlite_substrate_guard,
)


C0_3_PACKAGE_NAME = "agentic_core.L0_routing.c0_retrieval.c0_3_enhanced"


def _runtime_module_files() -> list[Path]:
    pkg = importlib.import_module(C0_3_PACKAGE_NAME)
    pkg_dir = Path(pkg.__file__).parent  # type: ignore[arg-type]
    return [p for p in pkg_dir.glob("*.py") if p.name != "__init__.py"]


def test_sqlite_is_canonical_source_for_projection() -> None:
    """The InMemoryGraphAdapter exposes a non-SQLite projection manifest —
    it stands in for a GraphDB projection of the canonical SQLite ADG.
    Projection manifest must include canonical_source_hash + projection_version."""
    g = InMemoryGraphAdapter()
    pm = g.get_projection_manifest()
    assert pm.projection_version
    assert pm.snapshot_pointer
    assert pm.canonical_source_hash


def test_graphdb_projection_manifest_exists() -> None:
    g = InMemoryGraphAdapter()
    pm = g.get_projection_manifest()
    assert pm.graph_source


def test_graphdb_projection_preserves_node_ids(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    accepted_ids = {n.neighbor_id for n in pool.accepted_graph_neighbors}
    # Node IDs are preserved through the projection.
    assert "doc:example_v2" in accepted_ids


def test_graphdb_projection_preserves_relation_types(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    accepted_rels = {n.relation_path[-1] for n in pool.accepted_graph_neighbors}
    # The basic graph has known relation types -> they survive into the pool.
    assert {"supersedes", "owns", "contradicts"} & accepted_rels


def test_graphdb_projection_preserves_source_lineage(make_input, make_basic_graph) -> None:
    pool = run_graph_traverse(make_input(), make_basic_graph())
    for n in pool.accepted_graph_neighbors:
        assert n.source_id  # lineage preserved


def test_c0_3_runtime_modules_have_zero_direct_sqlite_imports() -> None:
    """Phase 4 substrate rule — no module under c0_3_enhanced may import
    sqlite3 directly. ``substrate.py`` is exempt because it installs the
    runtime guard and must reach into ``sqlite3`` to monkey-patch
    ``connect``."""
    bad: list[str] = []
    for path in _runtime_module_files():
        if path.name == "substrate.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "import sqlite3" in text or "from sqlite3" in text:
            bad.append(path.name)
    assert not bad, f"forbidden sqlite3 import in: {bad}"


def test_assert_no_direct_sqlite_traversal_passes_for_clean_runtime() -> None:
    # Should NOT raise.
    assert_no_direct_sqlite_traversal()


def test_substrate_guard_blocks_runtime_sqlite_connect() -> None:
    """The runtime guard MUST raise if a C0.3 runtime module tries to open a
    SQLite connection. We compile a function with ``__file__`` set to a path
    inside the runtime package and verify the guard fires when the function
    calls ``sqlite3.connect``.

    This avoids racy on-disk sentinel files that pytest's ``importlib`` mode
    can mishandle."""
    import sqlite3

    # Climb 6 parents to reach repo root (skip past tests/ tree).
    repo_root = Path(__file__).resolve().parents[5]
    pkg_dir = (repo_root / "agentic_core" / "L0_routing" / "c0_retrieval" / "c0_3_enhanced").resolve()
    fake_filename = str(pkg_dir / "_runtime_sqlite_probe_inline.py")

    src = "def open_db():\n    return sqlite3.connect(':memory:')\n"
    code = compile(src, fake_filename, "exec")
    namespace: dict = {"sqlite3": sqlite3}
    exec(code, namespace)  # noqa: S102 — inline test scaffolding
    open_db = namespace["open_db"]

    with sqlite_substrate_guard():
        with pytest.raises(SubstrateViolation):
            open_db()


def test_substrate_guard_allows_external_sqlite_connect() -> None:
    """A test (non-runtime) frame is allowed to open SQLite even under the
    guard."""
    import sqlite3

    with sqlite_substrate_guard():
        conn = sqlite3.connect(":memory:")
        conn.close()


def test_k_hop_traversal_returns_expected_neighbors(make_input, make_basic_graph) -> None:
    g = make_basic_graph()
    g.add_node(
        "doc:depth2",
        node_type="document",
        source_id="docs/depth2.md",
        source_type="docs",
        tenant="tenantA",
        region="us",
        data_class="internal",
        payload_preview="depth-2 doc",
    )
    g.add_edge("doc:example_v2", "doc:depth2", "references")

    pool1 = run_graph_traverse(make_input(max_hops=1), g)
    pool2 = run_graph_traverse(make_input(max_hops=2), g)
    accepted1 = {n.neighbor_id for n in pool1.accepted_graph_neighbors}
    accepted2 = {n.neighbor_id for n in pool2.accepted_graph_neighbors}
    assert "doc:depth2" not in accepted1
    assert "doc:depth2" in accepted2


def test_stale_projection_blocks_or_caveats(make_input, make_basic_graph) -> None:
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import (
        FreshnessClass,
        RejectionReason,
    )

    g = make_basic_graph()
    g.mark_stale("snapshot drift")
    pool_current = run_graph_traverse(make_input(freshness_class=FreshnessClass.CURRENT), g)
    reasons = {r.rejection_reason for r in pool_current.rejected_graph_neighbors}
    assert RejectionReason.PROJECTION_STALE in reasons

    # STATIC freshness allows but caveats.
    g2 = make_basic_graph()
    g2.mark_stale("snapshot drift")
    pool_static = run_graph_traverse(make_input(freshness_class=FreshnessClass.STATIC), g2)
    # Should NOT have PROJECTION_STALE rejections.
    reasons_static = {r.rejection_reason for r in pool_static.rejected_graph_neighbors}
    assert RejectionReason.PROJECTION_STALE not in reasons_static
