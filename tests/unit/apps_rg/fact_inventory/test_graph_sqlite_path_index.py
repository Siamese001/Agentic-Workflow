from __future__ import annotations

# apps-test-model: APP CONTRACT
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from apps_rg.fact_inventory.apply_graphdb_capability_sqlite_hardening import (
    apply_graphdb_capability_sqlite_hardening,
)
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    DDL_STATEMENTS,
    default_graph_sqlite_path,
    open_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    METRIC_NODE_TYPES,
    SIBLING_NODE_TYPES,
    build_graph_index_rows,
    build_graph_neighborhoods,
    build_graph_sibling_links,
    compute_sqlite_graph_digest,
    ensure_graphdb_capability_schema,
    materialize_graph_path_index,
    query_best_metric_candidates,
    query_repeated_metrics,
    query_reverse_metric_paths,
    query_section_evidence_budget,
    query_sibling_alternatives,
    record_graph_selection_rejection,
    record_resume_metric_usage,
    require_graphdb_capability_schema,
    table_exists,
    validate_graphdb_capability_integrity,
)
from apps_rg.fact_inventory.validate_graph_sqlite_path_index import (
    validate_graph_sqlite_path_index,
)
from apps_rg.runtime.c0.c03_sqlite_graph_selection import (
    _query_sibling_alternatives,
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
        ("metric_runtime_001", "metric", "Audit coverage"),
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
        ("e1", "role_svp_ai", "pillar_agentic_runtime", "identity_supported_by_pillar"),
        ("e2", "pillar_agentic_runtime", "skill_runtime_governance", "capability_domain_contains_skill"),
        ("e3", "pillar_agentic_runtime", "skill_audit_observability", "capability_domain_contains_skill"),
        ("e4", "skill_runtime_governance", "fact_runtime_001", "skill_supported_by_fact"),
        ("e5", "skill_runtime_governance", "metric_runtime_001", "skill_can_surface_metric"),
        ("e6", "skill_runtime_governance", "section_executive_summary", "skill_allowed_in_section"),
    ]
    conn.executemany(
        "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES (?,?,?,?)",
        edges,
    )
    conn.execute(
        "INSERT INTO skill_fact_links(skill_id,fact_id) VALUES (?,?)",
        ("skill_runtime_governance", "fact_runtime_001"),
    )
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
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths if path.exists()}


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
        before_edge_columns = {row[1] for row in conn.execute("PRAGMA table_info(graph_edges)").fetchall()}
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
        conn.execute("CREATE TABLE graph_edges_reverse (edge_id TEXT, source_node_id TEXT)")
        conn.commit()
        conn.execute("PRAGMA query_only=ON")
        with pytest.raises(ValueError, match="missing view: graph_edges_reverse"):
            require_graphdb_capability_schema(conn)
    finally:
        conn.close()


def test_sqlite_graph_digest_encodes_blobs_deterministically() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        for ddl in DDL_STATEMENTS:
            conn.execute(ddl)
        conn.execute(
            "INSERT INTO graph_nodes(node_id,node_type,label,created_at,updated_at) "
            "VALUES ('blob_node','fact',?,'t','t')",
            (sqlite3.Binary(b"\x00\xff\x10"),),
        )
        conn.commit()

        first = compute_sqlite_graph_digest(conn)
        second = compute_sqlite_graph_digest(conn)

        assert first == second
        assert len(first) == 64
    finally:
        conn.close()


def test_sqlite_graph_digest_translates_weak_raw_type_to_value_error() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        for ddl in DDL_STATEMENTS:
            conn.execute(ddl)

        class WeakValueConnection:
            def execute(self, sql: str, parameters: tuple[object, ...] = ()) -> object:
                if sql.startswith("SELECT node_id,node_type,label,"):

                    class WeakRows:
                        @staticmethod
                        def fetchall() -> list[tuple[object, ...]]:
                            return [(object(), "fact", "label", "", "", "", 0, "", "")]

                    return WeakRows()
                return conn.execute(sql, parameters)

        with pytest.raises(
            ValueError,
            match="unsupported SQLite value: table=graph_nodes column=node_id",
        ):
            compute_sqlite_graph_digest(WeakValueConnection())  # type: ignore[arg-type]
    finally:
        conn.close()


def test_path_index_and_reverse_metric_paths() -> None:
    conn = _conn()
    materialize_graph_path_index(conn, max_depth=4)
    paths = query_reverse_metric_paths(conn, metric_id="metric_runtime_001")
    assert paths
    assert any("skill_runtime_governance" in p["node_path"] for p in paths)


def test_path_proof_inventory_includes_governed_non_fact_evidence_type() -> None:
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO graph_nodes(node_id,node_type,label,created_at,updated_at) "
            "VALUES ('bullet_runtime_001','locked_bullet','Runtime bullet','t','t')"
        )
        conn.execute(
            "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) "
            "VALUES ('e_bullet','skill_audit_observability','bullet_runtime_001',"
            "'skill_supported_by_fact')"
        )
        conn.commit()

        materialize_graph_path_index(conn, max_depth=4)
        direct = conn.execute(
            "SELECT proof_fact_ids_json,proof_strength_score FROM graph_paths "
            "WHERE path_depth=1 AND end_node_id='bullet_runtime_001'"
        ).fetchone()
        deeper = conn.execute(
            "SELECT proof_fact_ids_json,proof_strength_score FROM graph_paths "
            "WHERE path_depth>1 AND start_node_id='role_svp_ai' "
            "AND end_node_id='bullet_runtime_001' ORDER BY path_depth LIMIT 1"
        ).fetchone()

        assert direct is not None
        assert json.loads(direct[0]) == ["bullet_runtime_001"]
        assert float(direct[1]) > 0
        assert deeper is not None
        assert json.loads(deeper[0]) == ["bullet_runtime_001"]
        assert float(deeper[1]) > 0
    finally:
        conn.close()


def test_metric_candidate_query_uses_all_first_class_metric_types() -> None:
    conn = _conn()
    try:
        conn.executemany(
            "INSERT INTO graph_nodes(node_id,node_type,label,created_at,updated_at) VALUES (?,?,?,'t','t')",
            (
                ("canonical_metric", "metric", "Canonical metric"),
                ("canonical_metric_bucket", "metric_bucket", "Canonical metric bucket"),
            ),
        )
        conn.executemany(
            "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES (?,?,?,?)",
            (
                (
                    "e_canonical_metric",
                    "skill_runtime_governance",
                    "canonical_metric",
                    "skill_can_surface_metric",
                ),
                (
                    "e_canonical_metric_bucket",
                    "skill_runtime_governance",
                    "canonical_metric_bucket",
                    "skill_has_metric_bucket",
                ),
            ),
        )
        conn.commit()
        materialize_graph_path_index(conn, max_depth=2)

        rows = query_best_metric_candidates(conn, limit=25)
        observed = {row["metric_id"] for row in rows}
        assert {
            "canonical_metric",
            "canonical_metric_bucket",
            "metric_runtime_001",
        } <= observed
        assert METRIC_NODE_TYPES == {"metric", "metric_bucket", "metric_outcome"}
    finally:
        conn.close()


def test_metric_candidate_query_uses_only_current_run_usage() -> None:
    conn = _conn()
    try:
        materialize_graph_path_index(conn, max_depth=2)
        record_resume_metric_usage(
            conn,
            run_id="prior_run",
            resume_section="executive_summary",
            metric_id="metric_runtime_001",
            fact_id="fact_runtime_001",
            skill_id="skill_runtime_governance",
            usage_count=7,
        )

        current_rows = query_best_metric_candidates(conn, run_id="current_run", limit=25)
        prior_rows = query_best_metric_candidates(conn, run_id="prior_run", limit=25)
        current_metric = next(row for row in current_rows if row["metric_id"] == "metric_runtime_001")
        prior_metric = next(row for row in prior_rows if row["metric_id"] == "metric_runtime_001")

        assert current_metric["prior_usage"] == 0
        assert prior_metric["prior_usage"] == 7
    finally:
        conn.close()


def test_sibling_links_find_nearby_alternative_skill() -> None:
    conn = _conn()
    conn.execute(
        "UPDATE graph_nodes SET external_eligible=1, activation_status='ACTIVE', "
        "support_level='DIRECT_FROM_RESUME_ARCHIVE' "
        "WHERE node_id='skill_audit_observability'"
    )
    build_graph_sibling_links(conn)
    siblings = query_sibling_alternatives(conn, node_id="skill_runtime_governance")
    assert any(s["sibling_node_id"] == "skill_audit_observability" for s in siblings)


@pytest.mark.parametrize(
    ("activation_status", "support_level"),
    (("BLOCKED", "DIRECT_FROM_RESUME_ARCHIVE"), ("ACTIVE", "INTERNAL_ONLY")),
)
def test_sibling_query_filters_structural_but_ineligible_alternatives(
    activation_status: str,
    support_level: str,
) -> None:
    conn = _conn()
    try:
        conn.execute(
            "UPDATE graph_nodes SET external_eligible=1, activation_status=?, "
            "support_level=? WHERE node_id='skill_audit_observability'",
            (activation_status, support_level),
        )
        build_graph_sibling_links(conn)
        assert conn.execute(
            "SELECT COUNT(*) FROM graph_sibling_links "
            "WHERE node_id='skill_runtime_governance' "
            "AND sibling_node_id='skill_audit_observability'"
        ).fetchone()[0]
        assert (
            query_sibling_alternatives(
                conn,
                node_id="skill_runtime_governance",
            )
            == []
        )
    finally:
        conn.close()


def test_graph_index_rows_preserve_sibling_contexts_for_declared_cohort() -> None:
    node_rows = [
        {"node_id": "parent_a", "node_type": "capability_domain"},
        {"node_id": "parent_b", "node_type": "career_epoch"},
        *(
            {"node_id": f"{node_type}_{suffix}", "node_type": node_type}
            for node_type in sorted(SIBLING_NODE_TYPES)
            for suffix in ("a", "b")
        ),
    ]
    edge_rows = [
        {
            "edge_id": f"edge_{parent}_{edge_type}_{node_type}_{suffix}",
            "source_node_id": parent,
            "target_node_id": f"{node_type}_{suffix}",
            "edge_type": edge_type,
        }
        for parent, edge_type in (
            ("parent_a", "contains"),
            ("parent_b", "supports"),
        )
        for node_type in sorted(SIBLING_NODE_TYPES)
        for suffix in ("a", "b")
    ]

    rows = build_graph_index_rows(
        node_rows=node_rows,
        edge_rows=edge_rows,
        section_rows=[],
        role_family_projection_rows=[],
        created_at="2026-07-18T00:00:00Z",
    )["graph_sibling_links"]

    expected_child_count = len(SIBLING_NODE_TYPES) * 2
    assert len(rows) == 2 * expected_child_count * (expected_child_count - 1)
    assert {
        (
            row["node_id"],
            row["sibling_node_id"],
            row["shared_parent_node_id"],
            row["shared_edge_type"],
        )
        for row in rows
        if row["node_id"] == "skill_a" and row["sibling_node_id"] == "skill_b"
    } == {
        ("skill_a", "skill_b", "parent_a", "contains"),
        ("skill_a", "skill_b", "parent_b", "supports"),
    }


def test_prebuilt_and_in_place_sibling_materializers_are_context_equivalent() -> None:
    conn = _conn()
    try:
        ensure_graphdb_capability_schema(conn)
        conn.execute(
            """
            INSERT INTO graph_nodes(
                node_id,node_type,label,activation_status,support_level,
                created_at,updated_at
            ) VALUES ('skill_blocked','skill','Blocked skill','BLOCKED','BLOCKED','t','t')
            """
        )
        conn.execute(
            """
            INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type)
            VALUES (
                'e_blocked_skill','pillar_agentic_runtime','skill_blocked',
                'capability_domain_contains_skill'
            )
            """
        )
        conn.commit()

        node_rows = [
            {"node_id": row[0], "node_type": row[1]}
            for row in conn.execute("SELECT node_id,node_type FROM graph_nodes")
        ]
        edge_rows = [
            {
                "edge_id": row[0],
                "source_node_id": row[1],
                "target_node_id": row[2],
                "edge_type": row[3],
            }
            for row in conn.execute("SELECT edge_id,source_node_id,target_node_id,edge_type FROM graph_edges")
        ]
        prebuilt = build_graph_index_rows(
            node_rows=node_rows,
            edge_rows=edge_rows,
            section_rows=[],
            role_family_projection_rows=[],
            created_at="2026-07-18T00:00:00Z",
        )["graph_sibling_links"]
        build_graph_sibling_links(conn)
        persisted = conn.execute(
            """
            SELECT node_id,sibling_node_id,shared_parent_node_id,shared_edge_type
            FROM graph_sibling_links
            """
        ).fetchall()

        expected_contexts = {
            (
                row["node_id"],
                row["sibling_node_id"],
                row["shared_parent_node_id"],
                row["shared_edge_type"],
            )
            for row in prebuilt
        }
        assert set(persisted) == expected_contexts
        assert (
            "skill_runtime_governance",
            "skill_blocked",
            "pillar_agentic_runtime",
            "capability_domain_contains_skill",
        ) in expected_contexts
    finally:
        conn.close()


def test_sibling_queries_return_unique_peers_with_shared_context_count(
    tmp_path: Path,
) -> None:
    conn = _conn()
    ensure_graphdb_capability_schema(conn)
    conn.execute(
        "INSERT INTO graph_nodes(node_id,node_type,label,created_at,updated_at) "
        "VALUES ('parent_alt','capability_domain','Alternative parent','t','t')"
    )
    conn.executemany(
        "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES (?,?,?,?)",
        (
            (
                "e_alt_runtime",
                "parent_alt",
                "skill_runtime_governance",
                "capability_domain_contains_skill",
            ),
            (
                "e_alt_audit",
                "parent_alt",
                "skill_audit_observability",
                "capability_domain_contains_skill",
            ),
        ),
    )
    conn.execute(
        "UPDATE graph_nodes SET external_eligible=1 "
        "WHERE node_id IN ('skill_runtime_governance','skill_audit_observability')"
    )
    conn.commit()
    build_graph_sibling_links(conn)

    direct = query_sibling_alternatives(
        conn,
        node_id="skill_runtime_governance",
    )
    assert [row["sibling_node_id"] for row in direct] == ["skill_audit_observability"]
    assert direct[0]["shared_context_count"] == 2

    db_path = tmp_path / "graph.sqlite"
    _write_conn_to_disk(conn, db_path)
    reader = open_graph_sqlite(repo_root=tmp_path, db_path=db_path)
    try:
        runtime = _query_sibling_alternatives(
            conn=reader,
            selected_skill_ids=["skill_runtime_governance"],
        )
    finally:
        reader.close()
    assert [row["skill_id"] for row in runtime["skill_runtime_governance"]] == ["skill_audit_observability"]
    assert runtime["skill_runtime_governance"][0]["shared_context_count"] == 2


def test_sibling_integrity_requires_reciprocity_in_the_same_context() -> None:
    conn = _conn()
    try:
        ensure_graphdb_capability_schema(conn)
        conn.executemany(
            "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES (?,?,?,?)",
            (
                (
                    "e_supports_runtime",
                    "pillar_agentic_runtime",
                    "skill_runtime_governance",
                    "pillar_supports_skill",
                ),
                (
                    "e_supports_audit",
                    "pillar_agentic_runtime",
                    "skill_audit_observability",
                    "pillar_supports_skill",
                ),
            ),
        )
        conn.executemany(
            """
            INSERT INTO graph_sibling_links(
                node_id,sibling_node_id,sibling_reason,shared_parent_node_id,
                shared_edge_type,sibling_score
            ) VALUES (?,?,?,?,?,?)
            """,
            (
                (
                    "skill_runtime_governance",
                    "skill_audit_observability",
                    "shared parent",
                    "pillar_agentic_runtime",
                    "pillar_contains_skill",
                    1.5,
                ),
                (
                    "skill_audit_observability",
                    "skill_runtime_governance",
                    "shared parent",
                    "pillar_agentic_runtime",
                    "pillar_supports_skill",
                    1.5,
                ),
            ),
        )
        conn.commit()

        with pytest.raises(
            ValueError,
            match="nonreciprocal_graph_sibling_links=2",
        ):
            validate_graphdb_capability_integrity(conn)
    finally:
        conn.close()


def test_integrity_accepts_governed_evidence_targets_and_rejects_unrelated_nodes() -> None:
    conn = _conn()
    try:
        ensure_graphdb_capability_schema(conn)
        conn.execute(
            "INSERT INTO graph_nodes(node_id,node_type,label,created_at,updated_at) "
            "VALUES ('bullet_runtime_001','locked_bullet','Runtime bullet','t','t')"
        )
        conn.execute(
            "INSERT INTO skill_fact_links(skill_id,fact_id) VALUES (?,?)",
            ("skill_runtime_governance", "bullet_runtime_001"),
        )
        conn.execute(
            "INSERT INTO skill_fact_links(skill_id,fact_id) VALUES (?,?)",
            ("skill_audit_observability", "metric_runtime_001"),
        )
        conn.commit()

        with pytest.raises(ValueError, match="broken_skill_fact_links=1"):
            validate_graphdb_capability_integrity(conn)
    finally:
        conn.close()


def test_metric_usage_accepts_opaque_metric_keys_but_rejects_broken_graph_refs() -> None:
    conn = _conn()
    try:
        ensure_graphdb_capability_schema(conn)
        record_resume_metric_usage(
            conn,
            run_id="valid_run",
            resume_section="executive_summary",
            metric_id="opaque_runtime_metric_key",
            fact_id="fact_runtime_001",
            skill_id="skill_runtime_governance",
        )
        record_resume_metric_usage(
            conn,
            run_id="invalid_run",
            resume_section="executive_summary",
            metric_id="another_opaque_runtime_metric_key",
            fact_id="missing_fact",
            skill_id="skill_runtime_governance",
        )

        with pytest.raises(ValueError, match="broken_resume_metric_usage_refs=1"):
            validate_graphdb_capability_integrity(conn)
    finally:
        conn.close()


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
    source.execute(
        "UPDATE graph_nodes SET external_eligible=1, activation_status='ACTIVE', "
        "support_level='DIRECT_FROM_RESUME_ARCHIVE' "
        "WHERE node_id='skill_audit_observability'"
    )
    source.commit()
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


def test_integrity_requires_exact_authoritative_metadata_status(
    tmp_path: Path,
) -> None:
    source = _conn()
    source.commit()
    db_path = tmp_path / "graph.sqlite"
    _write_conn_to_disk(source, db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("UPDATE graph_metadata SET authority_status='augmented_skills_graph_advisory'")
        conn.commit()

        with pytest.raises(
            ValueError,
            match="graph_metadata_authority_status_mismatch",
        ):
            validate_graphdb_capability_integrity(conn)
    finally:
        conn.close()


def test_open_graph_sqlite_rejects_writable_mode_for_canonical_path(
    tmp_path: Path,
) -> None:
    db_path = default_graph_sqlite_path(tmp_path)
    db_path.parent.mkdir(parents=True)
    sqlite3.connect(db_path).close()

    with pytest.raises(
        RuntimeError,
        match="writable graph SQLite access is internal-only.*atomic rebuild.*atomic capability",
    ):
        open_graph_sqlite(repo_root=tmp_path, db_path=db_path, read_only=False)


def test_open_graph_sqlite_rejects_writable_mode_for_arbitrary_projection_path(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "arbitrary_projection.sqlite"
    sqlite3.connect(db_path).close()

    with pytest.raises(
        RuntimeError,
        match="writable graph SQLite access is internal-only.*atomic rebuild.*atomic capability",
    ):
        open_graph_sqlite(repo_root=tmp_path, db_path=db_path, read_only=False)


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
