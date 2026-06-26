"""apps-test-model: APP CONTRACT.

SQLite graph-index helper tests for apps_rg C0.3 traversal support.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    materialize_augmented_skills_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    DEFAULT_MAX_DEPTH,
    materialize_graph_path_index,
    query_best_metric_candidates,
    query_repeated_metrics,
    query_reverse_metric_paths,
    query_section_evidence_budget,
    query_sibling_alternatives,
    record_graph_selection_rejection,
    record_resume_metric_usage,
)
from apps_rg.fact_inventory.validate_graph_sqlite_path_index import (
    validate_graph_sqlite_path_index,
)

REPO = Path(__file__).resolve().parents[4]


@pytest.fixture
def sqlite_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "graph_index.sqlite"
    materialize_augmented_skills_graph_sqlite(repo_root=REPO, db_path=db_path)
    return db_path


def test_materialization_preserves_graph_nodes_and_edges(sqlite_db: Path) -> None:
    graph = load_augmented_skills_graph(repo_root=REPO)
    expected_edges = len(
        [
            edge
            for edge in graph.get("graph_edges") or []
            if isinstance(edge, dict) and edge.get("edge_id")
        ]
    )
    conn = sqlite3.connect(str(sqlite_db))
    try:
        node_count = conn.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0]
        edge_count = conn.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0]
        link_count = conn.execute("SELECT COUNT(*) FROM skill_fact_links").fetchone()[0]
        helper_counts = materialize_graph_path_index(conn, created_at="2026-06-25T00:00:00Z")
    finally:
        conn.close()

    assert DEFAULT_MAX_DEPTH == 4
    assert node_count >= int(graph["graph_metadata"]["node_count"])
    assert edge_count >= expected_edges
    assert link_count > 0
    assert helper_counts["graph_path_count"] > 0
    assert helper_counts["graph_neighborhood_count"] > 0
    assert helper_counts["graph_sibling_link_count"] > 0


def test_reverse_traversal_finds_upstream_skill_for_fact(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        rows = query_reverse_metric_paths(
            conn,
            metric_id="fact_engineering_platform_001",
            limit=20,
        )
    finally:
        conn.close()

    assert rows
    assert any(row["upstream_node_id"] == "skill_runtime_gate_mesh_design" for row in rows)
    assert all("rationale" in row for row in rows)


def test_sibling_links_produce_skill_alternatives(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        rows = query_sibling_alternatives(
            conn,
            node_id="skill_runtime_gate_mesh_design",
            limit=10,
        )
    finally:
        conn.close()

    assert rows
    assert all(row["alternate_node_id"].startswith("skill_") for row in rows)
    assert {row["sibling_reason"] for row in rows}


def test_metric_usage_penalizes_repeated_metric_candidates(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        candidates = query_best_metric_candidates(
            conn,
            section_id="executive_summary",
            role_family_key="SVP_ENGINEERING_AI_PLATFORM",
            limit=5,
        )
        assert candidates
        metric_id = str(candidates[0]["metric_id"])
        record_resume_metric_usage(
            conn,
            run_id="run_a",
            resume_section="executive_summary",
            metric_id=metric_id,
            metric_value=str(candidates[0]["metric_label"]),
            role_family_key="SVP_ENGINEERING_AI_PLATFORM",
            usage_count=2,
            created_at="2026-06-25T00:00:00Z",
        )
        conn.commit()
        repeated = query_repeated_metrics(conn)
        refreshed = query_best_metric_candidates(
            conn,
            section_id="executive_summary",
            role_family_key="SVP_ENGINEERING_AI_PLATFORM",
            limit=500,
        )
    finally:
        conn.close()

    assert any(row["metric_id"] == metric_id for row in repeated)
    ledger_row = next(row for row in repeated if row["metric_id"] == metric_id)
    assert int(ledger_row["appearances"]) >= 2
    assert refreshed
    if any(int(row["prior_usage"]) == 0 for row in refreshed):
        assert refreshed[0]["metric_id"] != metric_id


def test_section_evidence_budget_loads_defaults(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        budget = query_section_evidence_budget(
            conn,
            section_id="executive_summary",
            role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        )
    finally:
        conn.close()

    assert budget is not None
    assert int(budget["max_metric_reuse"]) == 1
    assert "skill_supported_by_fact" in str(budget["preferred_edge_types_json"])


def test_rejection_receipts_can_be_inserted_and_queried(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        record_graph_selection_rejection(
            conn,
            run_id="run_reject",
            section_id="executive_summary",
            candidate_node_id="skill_runtime_gate_mesh_design",
            candidate_node_type="skill",
            rejected_reason="repeated_metric",
            rejected_at_stage="metric_novelty",
            competing_selected_node_id="skill_graph_aware_relationship_grounding",
            path_signature="skill_runtime_gate_mesh_design->fact_engineering_platform_001",
            created_at="2026-06-25T00:00:00Z",
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT rejected_reason, rejected_at_stage, competing_selected_node_id
            FROM graph_selection_rejections
            WHERE run_id = 'run_reject'
            """
        ).fetchone()
    finally:
        conn.close()

    assert row == (
        "repeated_metric",
        "metric_novelty",
        "skill_graph_aware_relationship_grounding",
    )


def test_graph_paths_contains_valid_skill_fact_path(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        row = conn.execute(
            """
            SELECT path_signature, proof_fact_ids_json, path_depth
            FROM graph_paths
            WHERE start_node_id = 'skill_runtime_gate_mesh_design'
              AND end_node_id = 'fact_engineering_platform_001'
            ORDER BY path_depth ASC, path_score DESC
            LIMIT 1
            """
        ).fetchone()
    finally:
        conn.close()

    assert row is not None
    assert row[0] == "skill_runtime_gate_mesh_design->fact_engineering_platform_001"
    assert "fact_engineering_platform_001" in row[1]
    assert int(row[2]) >= 1


def test_validation_fails_if_required_tables_missing(tmp_path: Path) -> None:
    db_path = tmp_path / "missing_graph_index.sqlite"
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("CREATE TABLE graph_edges (edge_id TEXT PRIMARY KEY)")
        conn.commit()
    finally:
        conn.close()

    result = validate_graph_sqlite_path_index(
        repo_root=REPO,
        db_path=db_path,
        materialize=False,
    )

    assert result["status"] == "FAIL"
    assert result["issues"]
