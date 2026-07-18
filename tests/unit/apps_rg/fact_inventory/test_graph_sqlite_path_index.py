from __future__ import annotations

# apps-test-model: APP CONTRACT
import hashlib
import sqlite3
from pathlib import Path

import pytest

from apps_rg.fact_inventory.apply_graphdb_capability_sqlite_hardening import (
    apply_graphdb_capability_sqlite_hardening,
)
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    DDL_STATEMENTS,
    open_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    build_graph_neighborhoods,
    build_graph_sibling_links,
    ensure_graphdb_capability_schema,
    materialize_graph_path_index,
    query_repeated_metrics,
    query_reverse_metric_paths,
    query_section_evidence_budget,
    query_sibling_alternatives,
    record_graph_selection_rejection,
    record_resume_metric_usage,
    require_graphdb_capability_schema,
    table_exists,
)
from apps_rg.fact_inventory.validate_graph_sqlite_path_index import (
    validate_graph_sqlite_path_index,
)


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    for ddl in DDL_STATEMENTS[:3]:
        conn.execute(ddl)
    nodes = [
        ("role_svp_ai", "role_family", "SVP AI"),
        ("pillar_agentic_runtime", "pillar", "Agentic Runtime"),
        ("skill_runtime_governance", "skill", "Runtime Governance"),
        ("skill_audit_observability", "skill", "Audit Observability"),
        ("fact_runtime_001", "fact", "Runtime proof fact"),
        ("metric_runtime_001", "metric_outcome", "Audit coverage"),
        ("section_executive_summary", "section", "Executive Summary"),
    ]
    conn.executemany(
        """
        INSERT INTO graph_nodes(
            node_id,node_type,label,created_at,updated_at
        ) VALUES (?,?,?,'t','t')
        """,
        nodes,
    )
    edges = [
        ("e1", "role_svp_ai", "pillar_agentic_runtime", "role_family_weights_pillar"),
        ("e2", "pillar_agentic_runtime", "skill_runtime_governance", "pillar_contains_skill"),
        ("e3", "pillar_agentic_runtime", "skill_audit_observability", "pillar_contains_skill"),
        ("e4", "skill_runtime_governance", "fact_runtime_001", "skill_supported_by_fact"),
        ("e5", "fact_runtime_001", "metric_runtime_001", "fact_has_metric_outcome"),
        ("e6", "skill_runtime_governance", "section_executive_summary", "skill_allowed_in_section"),
    ]
    conn.executemany(
        "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES (?,?,?,?)",
        edges,
    )
    conn.execute("INSERT INTO skill_fact_links(skill_id,fact_id) VALUES (?,?)", ("skill_runtime_governance", "fact_runtime_001"))
    conn.commit()
    return conn


def _write_conn_to_disk(conn: sqlite3.Connection, db_path: Path) -> None:
    disk = sqlite3.connect(db_path)
    try:
        conn.backup(disk)
    finally:
        disk.close()
        conn.close()


def _storage_snapshot(db_path: Path) -> dict[str, str]:
    paths = [db_path, *(Path(f"{db_path}{suffix}") for suffix in ("-journal", "-wal", "-shm"))]
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
        if path.exists()
    }


def test_schema_adds_graphdb_capability_tables_and_reverse_view() -> None:
    conn = _conn()
    try:
        ensure_graphdb_capability_schema(conn)
        assert table_exists(conn, "graph_edges_reverse")
        assert table_exists(conn, "graph_paths")
        assert table_exists(conn, "graph_sibling_links")
        assert table_exists(conn, "graph_neighborhoods")
        assert table_exists(conn, "resume_metric_usage")
        assert table_exists(conn, "section_evidence_budget")
        assert table_exists(conn, "graph_selection_rejections")
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        conn.close()


def test_require_schema_is_pure_and_works_with_query_only() -> None:
    conn = _conn()
    try:
        ensure_graphdb_capability_schema(conn)
        conn.execute("PRAGMA query_only=ON")
        schema = require_graphdb_capability_schema(conn)
        assert schema["schema_status"] == "GRAPHDB_CAPABILITY_SCHEMA_READY"
        assert schema["added_graph_edges_columns"] == []
    finally:
        conn.close()


def test_require_schema_does_not_create_or_repair_incomplete_projection() -> None:
    conn = _conn()
    try:
        before_edge_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(graph_edges)").fetchall()
        }
        conn.execute("PRAGMA query_only=ON")
        with pytest.raises(ValueError, match="graphDB capability schema incomplete"):
            require_graphdb_capability_schema(conn)
        assert not table_exists(conn, "graph_paths")
        assert before_edge_columns == {
            row[1] for row in conn.execute("PRAGMA table_info(graph_edges)").fetchall()
        }
    finally:
        conn.close()


def test_require_schema_rejects_table_masquerading_as_reverse_view() -> None:
    conn = _conn()
    try:
        ensure_graphdb_capability_schema(conn)
        conn.execute("DROP VIEW graph_edges_reverse")
        conn.execute(
            "CREATE TABLE graph_edges_reverse (edge_id TEXT, source_node_id TEXT)"
        )
        conn.commit()
        conn.execute("PRAGMA query_only=ON")
        with pytest.raises(ValueError, match="missing view: graph_edges_reverse"):
            require_graphdb_capability_schema(conn)
    finally:
        conn.close()


def test_path_index_and_reverse_metric_paths() -> None:
    conn = _conn()
    materialize_graph_path_index(conn, max_depth=4)
    paths = query_reverse_metric_paths(conn, metric_id="metric_runtime_001")
    assert paths
    assert any("skill_runtime_governance" in p["node_path"] for p in paths)


def test_sibling_links_find_nearby_alternative_skill() -> None:
    conn = _conn()
    build_graph_sibling_links(conn)
    siblings = query_sibling_alternatives(conn, node_id="skill_runtime_governance")
    assert any(s["sibling_node_id"] == "skill_audit_observability" for s in siblings)


def test_neighborhoods_materialize() -> None:
    conn = _conn()
    out = build_graph_neighborhoods(conn, max_distance=3)
    assert out["graph_neighborhoods_materialized"] > 0


def test_metric_usage_repetition_query_and_budget() -> None:
    conn = _conn()
    record_resume_metric_usage(
        conn,
        run_id="r1",
        resume_section="executive_summary",
        metric_id="metric_runtime_001",
        metric_value="audit coverage",
        fact_id="fact_runtime_001",
        skill_id="skill_runtime_governance",
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
    )
    record_resume_metric_usage(
        conn,
        run_id="r1",
        resume_section="experience",
        metric_id="metric_runtime_001",
        metric_value="audit coverage",
        fact_id="fact_runtime_001",
        skill_id="skill_runtime_governance",
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
    )
    repeated = query_repeated_metrics(conn, min_count=2)
    assert repeated[0]["metric_id"] == "metric_runtime_001"
    budget = query_section_evidence_budget(conn, section_id="executive_summary")
    assert budget is not None
    assert budget["max_metric_reuse"] == 1


def test_rejection_receipt_insert() -> None:
    conn = _conn()
    record_graph_selection_rejection(
        conn,
        run_id="r1",
        section_id="executive_summary",
        candidate_node_id="metric_runtime_001",
        candidate_node_type="metric_outcome",
        rejected_reason="repeated_metric",
        rejected_at_stage="metric_novelty_filter",
    )
    row = conn.execute("SELECT rejected_reason FROM graph_selection_rejections").fetchone()
    assert row[0] == "repeated_metric"


def test_apply_graphdb_capability_hardening_opens_sqlite_writable(tmp_path) -> None:
    source = _conn()
    source.commit()
    db_path = tmp_path / "graph.sqlite"
    disk = sqlite3.connect(db_path)
    try:
        source.backup(disk)
    finally:
        disk.close()
        source.close()

    receipt = apply_graphdb_capability_sqlite_hardening(
        repo_root=tmp_path,
        db_path=db_path,
    )

    assert receipt["status"] == "GRAPHDB_CAPABILITY_SQLITE_HARDENED"
    assert receipt["materialization"]["schema"]["schema_status"] == "GRAPHDB_CAPABILITY_SCHEMA_READY"
    conn = sqlite3.connect(db_path)
    try:
        assert table_exists(conn, "graph_paths")
        assert table_exists(conn, "graph_selection_rejections")
    finally:
        conn.close()


def test_validate_graph_sqlite_path_index_is_read_only(tmp_path: Path) -> None:
    source = _conn()
    db_path = tmp_path / "graph.sqlite"
    _write_conn_to_disk(source, db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)
    before = _storage_snapshot(db_path)

    receipt = validate_graph_sqlite_path_index(
        repo_root=tmp_path,
        db_path=db_path,
        materialize_if_missing=False,
    )

    assert receipt["status"] == "PASS"
    assert receipt["graph_paths"] > 0
    assert receipt["section_evidence_budget"] >= 5
    assert receipt["counts_before"] == receipt["counts_after"]
    assert _storage_snapshot(db_path) == before


def test_query_helpers_are_pure_under_query_only_and_leave_storage_unchanged(
    tmp_path: Path,
) -> None:
    source = _conn()
    db_path = tmp_path / "graph.sqlite"
    _write_conn_to_disk(source, db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)
    before = _storage_snapshot(db_path)

    conn = open_graph_sqlite(repo_root=tmp_path, db_path=db_path, read_only=True)
    try:
        assert conn.execute("PRAGMA query_only").fetchone()[0] == 1
        assert query_reverse_metric_paths(conn, metric_id="metric_runtime_001")
        assert query_sibling_alternatives(conn, node_id="skill_runtime_governance")
        assert query_section_evidence_budget(conn, section_id="executive_summary")
        assert query_repeated_metrics(conn) == []
    finally:
        conn.close()

    assert _storage_snapshot(db_path) == before


def test_validator_rejects_write_intent_and_missing_projection_without_creation(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing.sqlite"
    with pytest.raises(ValueError, match="explicit applicator"):
        validate_graph_sqlite_path_index(
            repo_root=tmp_path,
            db_path=db_path,
            materialize_if_missing=True,
        )
    assert not db_path.exists()

    with pytest.raises(FileNotFoundError, match="projection not found"):
        validate_graph_sqlite_path_index(
            repo_root=tmp_path,
            db_path=db_path,
            materialize_if_missing=False,
        )
    assert not db_path.exists()


def test_validator_does_not_repair_incomplete_projection(tmp_path: Path) -> None:
    source = _conn()
    db_path = tmp_path / "incomplete.sqlite"
    _write_conn_to_disk(source, db_path)
    before = _storage_snapshot(db_path)

    with pytest.raises(ValueError, match="graphDB capability schema incomplete"):
        validate_graph_sqlite_path_index(
            repo_root=tmp_path,
            db_path=db_path,
            materialize_if_missing=False,
        )

    assert _storage_snapshot(db_path) == before
    conn = sqlite3.connect(db_path)
    try:
        assert not table_exists(conn, "graph_paths")
    finally:
        conn.close()
