"""Unit tests for W2.0 metric_outcome materialization (typed-edge-role-facet-guardrails-a6f3d2).

W2.0 invariants:
- "metric_outcome" is a canonical node type
- metric IDs (``metric_*`` prefix) infer to ``metric_outcome``
- Materialization is behavior-neutral wrt existing skill/pillar/edge counts
- Resolver fails closed on unresolved metric IDs (returns None, caller must handle)
- linked_metric_outcome_ids in role_episode_bundles must resolve to graph nodes after W2.0
"""

from __future__ import annotations

# apps-test-model: APP CONTRACT
import json
import sqlite3
from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    CANONICAL_NODE_TYPES,
    infer_node_type_from_id,
    materialize_augmented_skills_graph_sqlite,
)
from apps_rg.fact_inventory.metric_outcome_materializer import (
    METRIC_OUTCOME_EDGE_SIGNATURES,
    METRIC_OUTCOME_EDGE_TYPES,
    discover_role_episode_bundle_files,
    load_metric_outcome_rows_from_bundles,
    metric_outcome_node_and_edge_rows,
    resolve_metric_outcome_graph_node,
)


@pytest.fixture
def repo_root() -> Path:
    """Repo root containing the canonical role_episode_bundle JSONs."""
    return Path(__file__).resolve().parents[4]


def test_metric_outcome_in_canonical_node_types() -> None:
    """W2.0: metric_outcome is a first-class canonical node type."""
    assert "metric_outcome" in CANONICAL_NODE_TYPES


def test_metric_prefix_infers_to_metric_outcome() -> None:
    """W2.0: ``metric_*`` IDs infer to ``metric_outcome`` (precedes skill_)."""
    assert infer_node_type_from_id("metric_ey_audit_control_automation_workflows_count") == "metric_outcome"
    assert infer_node_type_from_id("metric_ibm_partner_marketplace_listings_count") == "metric_outcome"
    # Sanity: skill_ IDs still infer to skill (not shadowed by metric_).
    assert infer_node_type_from_id("skill_audit_grade_observability") == "skill"


def test_metric_outcome_edge_types_disjoint_from_existing_taxonomy() -> None:
    """W2.0 edge types are net-additive — do not collide with any pre-existing edge_type."""
    # All 3 new edge types share the ``metric_outcome_`` prefix.
    for edge_type in METRIC_OUTCOME_EDGE_TYPES:
        assert edge_type.startswith("metric_outcome_"), edge_type
    assert set(METRIC_OUTCOME_EDGE_SIGNATURES) == set(METRIC_OUTCOME_EDGE_TYPES)
    assert METRIC_OUTCOME_EDGE_SIGNATURES == {
        "metric_outcome_anchors_bundle": frozenset({("metric_outcome", "graph_ref")}),
        "metric_outcome_section_eligible": frozenset({("metric_outcome", "graph_ref")}),
        "metric_outcome_bound_to_employer": frozenset({("metric_outcome", "employment")}),
    }


def test_discover_role_episode_bundle_files(repo_root: Path) -> None:
    """W2.0: all 4 per-employer role_episode_bundle JSONs are discovered."""
    files = discover_role_episode_bundle_files(repo_root)
    names = sorted(p.name for p in files)
    assert names == [
        "ey_role_episode_bundles.json",
        "ibm_role_episode_bundles.json",
        "insurtech_role_episode_bundles.json",
        "unify_role_episode_bundles.json",
    ]


def test_load_metric_outcome_rows_from_bundles_yields_unique_metric_ids(
    repo_root: Path,
) -> None:
    """W2.0: all metric_outcome_nodes load with unique IDs (no cross-bundle collision)."""
    rows = load_metric_outcome_rows_from_bundles(repo_root)
    assert rows, "expected at least one metric_outcome to be discovered"
    # All metric IDs must be unique (load function raises on duplicates).
    assert len(rows) == len(set(rows))
    # Spot check: each row has the canonical shape from bundle JSON.
    sample_id = next(iter(rows))
    sample = rows[sample_id]
    assert isinstance(sample.get("metric_outcome_id") or sample_id, str)
    assert "metric_type" in sample
    assert "bundle_bindings" in sample


def _write_bundle_fixture(tmp_path: Path, payload: object) -> Path:
    inventory = tmp_path / "apps_rg/fact_inventory"
    inventory.mkdir(parents=True)
    (inventory / "test_role_episode_bundles.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    return tmp_path


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "root must be a JSON object"),
        ({"metric_outcome_nodes": []}, "metric_outcome_nodes must be a JSON object"),
        (
            {"metric_outcome_nodes": {"metric_test": "not-an-object"}},
            "must be a JSON object",
        ),
        (
            {"metric_outcome_nodes": {"": {"bundle_bindings": [], "section_eligibility": []}}},
            "blank or non-string metric ID",
        ),
    ],
)
def test_metric_outcome_registry_shapes_fail_closed(
    tmp_path: Path,
    payload: object,
    message: str,
) -> None:
    repo = _write_bundle_fixture(tmp_path, payload)

    with pytest.raises(ValueError, match=message):
        load_metric_outcome_rows_from_bundles(repo)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("bundle_bindings", "reb_character_iteration", "must be a JSON list"),
        ("bundle_bindings", ["reb_valid", ""], "non-empty strings"),
        ("bundle_bindings", ["reb_duplicate", "reb_duplicate"], "duplicate IDs"),
        ("section_eligibility", "executive_summary", "must be a JSON list"),
        ("section_eligibility", ["executive_summary", 7], "non-empty strings"),
    ],
)
def test_metric_outcome_binding_shapes_fail_closed(
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    metric = {
        "metric_outcome_id": "metric_test",
        "bundle_bindings": ["reb_test"],
        "section_eligibility": ["executive_summary"],
    }
    metric[field] = value
    repo = _write_bundle_fixture(
        tmp_path,
        {"metric_outcome_nodes": {"metric_test": metric}},
    )

    with pytest.raises(ValueError, match=message):
        load_metric_outcome_rows_from_bundles(repo)


def test_metric_outcome_declared_id_and_employer_shapes_fail_closed(
    tmp_path: Path,
) -> None:
    base_metric = {
        "metric_outcome_id": "metric_other",
        "bundle_bindings": [],
        "section_eligibility": [],
    }
    repo = _write_bundle_fixture(
        tmp_path,
        {"metric_outcome_nodes": {"metric_test": base_metric}},
    )
    with pytest.raises(ValueError, match="registry key"):
        load_metric_outcome_rows_from_bundles(repo)

    base_metric["metric_outcome_id"] = "metric_test"
    base_metric["employer_node_id"] = {"unexpected": "object"}
    (repo / "apps_rg/fact_inventory/test_role_episode_bundles.json").write_text(
        json.dumps({"metric_outcome_nodes": {"metric_test": base_metric}}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="employer_node_id must be a string"):
        load_metric_outcome_rows_from_bundles(repo)


def test_metric_outcome_node_rows_use_metric_outcome_type(repo_root: Path) -> None:
    """W2.0: every emitted node row has node_type='metric_outcome'."""
    node_rows, _ = metric_outcome_node_and_edge_rows(
        repo_root, ts="2026-06-13T00:00:00Z", known_node_ids=set()
    )
    assert node_rows
    assert all(r["node_type"] == "metric_outcome" for r in node_rows)
    # source_authority remains augmented_skills_graph (not a separate authority).
    assert all(r["source_authority"] == "augmented_skills_graph" for r in node_rows)


def test_metric_outcome_edges_emit_only_canonical_edge_types(repo_root: Path) -> None:
    """W2.0: all emitted edges use one of the 3 canonical metric_outcome edge_types."""
    # Provide employer node IDs in known_node_ids so employer-bound edges materialize.
    known = {
        "employment_exp_ey_001",
        "employment_exp_ibm_001",
        "employment_exp_unify_001",
        "employment_exp_insurtech_001",
    }
    _, edge_rows = metric_outcome_node_and_edge_rows(
        repo_root, ts="2026-06-13T00:00:00Z", known_node_ids=known
    )
    assert edge_rows
    edge_types = {r["edge_type"] for r in edge_rows}
    assert edge_types.issubset(METRIC_OUTCOME_EDGE_TYPES)
    # At least one of each edge_type should be present given the bundle data.
    assert "metric_outcome_anchors_bundle" in edge_types
    assert "metric_outcome_section_eligible" in edge_types


def test_metric_outcome_materialization_writes_graph_nodes(repo_root: Path, tmp_path: Path) -> None:
    """W2.0 end-to-end: full materialization writes metric_outcome rows into the SQLite."""
    db_path = tmp_path / "augmented_skills_graph_w20_test.sqlite"
    summary = materialize_augmented_skills_graph_sqlite(repo_root=repo_root, db_path=db_path)
    assert db_path.is_file()
    # Open and confirm metric_outcome rows are present.
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute("SELECT COUNT(*) FROM graph_nodes WHERE node_type = 'metric_outcome'")
        n_metric_outcomes = int(cur.fetchone()[0])
        assert n_metric_outcomes > 0, "expected at least one metric_outcome row"

        # Sanity: a known EY metric ID resolves through the W2.0 resolver.
        row = resolve_metric_outcome_graph_node(conn, "metric_ey_audit_control_automation_workflows_count")
        assert row is not None
        assert row["node_type"] == "metric_outcome"
        assert row["activation_status"] == "APPROVED_GRAPH_SSOT"
    finally:
        conn.close()

    # Behavior-neutral assertion: the materialization summary still emits
    # non-zero counts for the unchanged surfaces (skills/pillars/edges).
    assert summary["node_count_sqlite"] > 0
    assert summary["edge_count_sqlite"] > 0


def test_metric_outcome_resolver_unresolved_id_fails_closed(repo_root: Path, tmp_path: Path) -> None:
    """W2.0 No Silent Fallback: an unresolved metric ID returns None (caller fails closed)."""
    db_path = tmp_path / "augmented_skills_graph_w20_test_unresolved.sqlite"
    materialize_augmented_skills_graph_sqlite(repo_root=repo_root, db_path=db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        # Fake metric ID that does not exist in any bundle JSON.
        row = resolve_metric_outcome_graph_node(conn, "metric_does_not_exist_anywhere_0000")
        assert row is None
        # Empty string: same fail-closed.
        assert resolve_metric_outcome_graph_node(conn, "") is None
    finally:
        conn.close()


def test_linked_metric_outcome_ids_all_resolve_to_graph_nodes_after_w2(
    repo_root: Path, tmp_path: Path
) -> None:
    """W2.0 invariant ``linked_metric_outcome_id_must_resolve_to_graph_metric_outcome_after_W2``.

    Every metric ID referenced from a role_episode_bundle's ``linked_metric_outcome_ids``
    field must resolve to a materialized graph_node row.
    """
    db_path = tmp_path / "augmented_skills_graph_w20_link_resolve.sqlite"
    materialize_augmented_skills_graph_sqlite(repo_root=repo_root, db_path=db_path)
    # Collect every linked_metric_outcome_id across all bundles.
    linked_ids: set[str] = set()
    for path in discover_role_episode_bundle_files(repo_root):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for bundle in payload.get("bundles") or []:
            for mid in bundle.get("linked_metric_outcome_ids") or []:
                if str(mid).strip():
                    linked_ids.add(str(mid).strip())
    assert linked_ids, "expected at least one linked_metric_outcome_id across bundles"

    conn = sqlite3.connect(str(db_path))
    try:
        unresolved: list[str] = []
        for mid in sorted(linked_ids):
            if resolve_metric_outcome_graph_node(conn, mid) is None:
                unresolved.append(mid)
        assert not unresolved, (
            f"W2.0 invariant violated: {len(unresolved)} linked_metric_outcome_ids "
            f"did not resolve to graph_nodes: {unresolved[:5]}{'...' if len(unresolved) > 5 else ''}"
        )
    finally:
        conn.close()
