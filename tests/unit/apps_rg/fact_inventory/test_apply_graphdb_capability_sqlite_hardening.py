from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from pathlib import Path

import pytest

from apps_rg.fact_inventory.apply_graphdb_capability_sqlite_hardening import (
    UnsupportedGraphSchemaError,
    apply_graphdb_capability_sqlite_hardening,
)
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    DDL_STATEMENTS,
    materialize_augmented_skills_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    GRAPH_INDEX_CAPABILITY_VERSION,
    GRAPH_INDEX_SCHEMA_VERSION,
    compute_sqlite_graph_digest,
)

# apps-test-model: LAW


PRESERVED_TABLES = {
    "c03_role_family_skill_weights",
    "c03_skill_selection_features",
    "graph_edges",
    "graph_nodes",
    "graph_selection_rejections",
    "resume_metric_usage",
    "role_family_projection",
    "section_eligibility",
    "section_evidence_budget",
    "skill_fact_links",
}

REPO = Path(__file__).resolve().parents[4]


def _seed_source(db_path: Path, *, complete_schema: bool = False) -> None:
    conn = sqlite3.connect(db_path)
    try:
        if complete_schema:
            for ddl in DDL_STATEMENTS:
                conn.execute(ddl)
        else:
            conn.executescript(
                """
                CREATE TABLE graph_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    activation_status TEXT NOT NULL DEFAULT 'ACTIVE_CONFIRMED',
                    support_level TEXT NOT NULL DEFAULT 'DIRECT_FROM_RESUME_ARCHIVE'
                );
                CREATE TABLE graph_edges (
                    edge_id TEXT PRIMARY KEY,
                    source_node_id TEXT NOT NULL,
                    target_node_id TEXT NOT NULL,
                    edge_type TEXT NOT NULL
                );
                CREATE TABLE skill_fact_links (
                    skill_id TEXT NOT NULL,
                    fact_id TEXT NOT NULL,
                    PRIMARY KEY (skill_id, fact_id)
                );
                """
            )
        if complete_schema:
            conn.executemany(
                "INSERT INTO graph_nodes(node_id,node_type,label,created_at,updated_at) VALUES (?,?,?,?,?)",
                (
                    ("skill_a", "skill", "Skill A", "t", "t"),
                    ("fact_a", "fact", "Fact A", "t", "t"),
                ),
            )
        else:
            conn.executemany(
                "INSERT INTO graph_nodes(node_id,node_type,label) VALUES (?,?,?)",
                (
                    ("skill_a", "skill", "Skill A"),
                    ("fact_a", "fact", "Fact A"),
                ),
            )
        conn.execute(
            "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES (?,?,?,?)",
            ("edge_a", "skill_a", "fact_a", "skill_supported_by_fact"),
        )
        conn.execute(
            "INSERT INTO skill_fact_links(skill_id,fact_id) VALUES (?,?)",
            ("skill_a", "fact_a"),
        )
        if complete_schema:
            sqlite_graph_digest = compute_sqlite_graph_digest(conn)
            conn.execute(
                """
                INSERT INTO graph_metadata (
                    graph_version, materialized_from, materialized_at, ledger_hash,
                    graph_count_summary, authority_status
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "test_graph_v1",
                    f"sqlite_projection:{db_path.name}",
                    "t",
                    sqlite_graph_digest,
                    json.dumps(
                        {
                            "canonical_digest_kind": "sqlite_projection_logical_v1",
                            "sqlite_graph_digest": sqlite_graph_digest,
                        },
                        sort_keys=True,
                    ),
                    "augmented_skills_graph_authoritative",
                ),
            )
        conn.commit()
    finally:
        conn.close()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_no_maintenance_artifacts(db_path: Path) -> None:
    assert not db_path.with_name(f".{db_path.name}.maintenance.lock").exists()
    assert list(db_path.parent.glob(f".{db_path.name}.*.tmp")) == []


def _refresh_trusted_logical_digest(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        summary = json.loads(conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0])
        summary["sqlite_graph_digest"] = compute_sqlite_graph_digest(conn)
        conn.execute(
            "UPDATE graph_metadata SET graph_count_summary = ?",
            (json.dumps(summary, sort_keys=True),),
        )
        conn.commit()
    finally:
        conn.close()


@pytest.mark.parametrize(
    ("ddl", "expected_object"),
    (
        ("CREATE TABLE custom_graph_notes(note TEXT)", "table:custom_graph_notes"),
        (
            "CREATE VIEW custom_graph_labels AS SELECT node_id,label FROM graph_nodes",
            "view:custom_graph_labels",
        ),
        (
            "CREATE TRIGGER custom_graph_node_audit AFTER INSERT ON graph_nodes BEGIN SELECT 1; END",
            "trigger:custom_graph_node_audit",
        ),
        (
            "CREATE INDEX custom_graph_node_label ON graph_nodes(label)",
            "index:custom_graph_node_label",
        ),
    ),
)
def test_hardening_rejects_unsupported_schema_objects_without_replacing_source(
    tmp_path: Path,
    ddl: str,
    expected_object: str,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _seed_source(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(ddl)
        conn.commit()
    finally:
        conn.close()
    before = _sha256(db_path)

    with pytest.raises(UnsupportedGraphSchemaError) as caught:
        apply_graphdb_capability_sqlite_hardening(
            repo_root=tmp_path,
            db_path=db_path,
        )

    assert caught.value.unsupported_objects == (expected_object,)
    assert caught.value.unsupported_columns == ()
    assert "migrate or remove these schema extensions explicitly" in str(caught.value)
    assert _sha256(db_path) == before
    _assert_no_maintenance_artifacts(db_path)


def test_hardening_rejects_unsupported_extra_column_without_replacing_source(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _seed_source(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("ALTER TABLE graph_nodes ADD COLUMN private_annotation TEXT")
        conn.execute("UPDATE graph_nodes SET private_annotation='must not disappear' WHERE node_id='skill_a'")
        conn.commit()
    finally:
        conn.close()
    before = _sha256(db_path)

    with pytest.raises(UnsupportedGraphSchemaError) as caught:
        apply_graphdb_capability_sqlite_hardening(
            repo_root=tmp_path,
            db_path=db_path,
        )

    assert caught.value.unsupported_objects == ()
    assert caught.value.unsupported_columns == ("graph_nodes.private_annotation",)
    assert _sha256(db_path) == before
    _assert_no_maintenance_artifacts(db_path)


@pytest.mark.parametrize(
    "graph_nodes_ddl",
    (
        """
        CREATE TABLE graph_nodes (
            node_id TEXT PRIMARY KEY CHECK (length(node_id) > 0),
            node_type TEXT NOT NULL,
            label TEXT NOT NULL,
            activation_status TEXT NOT NULL DEFAULT 'ACTIVE_CONFIRMED',
            support_level TEXT NOT NULL DEFAULT 'DIRECT_FROM_RESUME_ARCHIVE'
        )
        """,
        """
        CREATE TABLE graph_nodes (
            node_id TEXT,
            node_type TEXT NOT NULL,
            label TEXT NOT NULL,
            activation_status TEXT NOT NULL DEFAULT 'ACTIVE_CONFIRMED',
            support_level TEXT NOT NULL DEFAULT 'DIRECT_FROM_RESUME_ARCHIVE',
            PRIMARY KEY (node_id, node_type)
        )
        """,
        """
        CREATE TABLE graph_nodes (
            node_id TEXT PRIMARY KEY,
            node_type TEXT NOT NULL,
            label TEXT NOT NULL REFERENCES graph_nodes(node_id),
            activation_status TEXT NOT NULL DEFAULT 'ACTIVE_CONFIRMED',
            support_level TEXT NOT NULL DEFAULT 'DIRECT_FROM_RESUME_ARCHIVE'
        )
        """,
        """
        CREATE TABLE graph_nodes (
            node_id TEXT PRIMARY KEY,
            node_type TEXT NOT NULL,
            label TEXT GENERATED ALWAYS AS (node_id) STORED,
            activation_status TEXT NOT NULL DEFAULT 'ACTIVE_CONFIRMED',
            support_level TEXT NOT NULL DEFAULT 'DIRECT_FROM_RESUME_ARCHIVE'
        )
        """,
        """
        CREATE TABLE graph_nodes (
            node_id TEXT PRIMARY KEY,
            node_type TEXT NOT NULL,
            label TEXT NOT NULL COLLATE NOCASE,
            activation_status TEXT NOT NULL DEFAULT 'ACTIVE_CONFIRMED',
            support_level TEXT NOT NULL DEFAULT 'DIRECT_FROM_RESUME_ARCHIVE'
        ) WITHOUT ROWID
        """,
    ),
)
def test_hardening_rejects_same_column_table_assertion_drift_atomically(
    tmp_path: Path,
    graph_nodes_ddl: str,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _seed_source(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DROP TABLE graph_nodes")
        conn.execute(graph_nodes_ddl)
        conn.commit()
    finally:
        conn.close()
    before = _sha256(db_path)

    with pytest.raises(UnsupportedGraphSchemaError) as caught:
        apply_graphdb_capability_sqlite_hardening(
            repo_root=tmp_path,
            db_path=db_path,
        )

    assert caught.value.unsupported_objects == ("table:graph_nodes",)
    assert _sha256(db_path) == before
    _assert_no_maintenance_artifacts(db_path)


def test_hardening_rejects_drifted_supported_view_without_replacing_source(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _seed_source(db_path, complete_schema=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DROP VIEW graph_edges_reverse")
        conn.execute(
            "CREATE VIEW graph_edges_reverse AS "
            "SELECT node_id AS edge_id,node_id AS source_node_id,"
            "node_id AS target_node_id,'invalid' AS edge_type FROM graph_nodes"
        )
        conn.commit()
    finally:
        conn.close()
    before = _sha256(db_path)

    with pytest.raises(UnsupportedGraphSchemaError) as caught:
        apply_graphdb_capability_sqlite_hardening(
            repo_root=tmp_path,
            db_path=db_path,
        )

    assert caught.value.unsupported_objects == ("view:graph_edges_reverse",)
    assert _sha256(db_path) == before
    _assert_no_maintenance_artifacts(db_path)


def test_hardening_accepts_sqlite_internal_autoindexes(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    _seed_source(db_path)
    conn = sqlite3.connect(db_path)
    try:
        internal_indexes = {
            str(row[0])
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'sqlite_autoindex_%'"
            )
        }
    finally:
        conn.close()
    assert internal_indexes

    receipt = apply_graphdb_capability_sqlite_hardening(
        repo_root=tmp_path,
        db_path=db_path,
    )

    assert receipt["status"] == "GRAPHDB_CAPABILITY_SQLITE_HARDENED"
    assert receipt["preservation"]["status"] == "PRESERVED_TABLES_VERIFIED"
    _assert_no_maintenance_artifacts(db_path)


def test_hardening_verifies_copy_for_every_promised_table(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    _seed_source(db_path, complete_schema=True)

    receipt = apply_graphdb_capability_sqlite_hardening(
        repo_root=tmp_path,
        db_path=db_path,
    )

    preservation = receipt["preservation"]
    assert preservation["status"] == "PRESERVED_TABLES_VERIFIED"
    assert set(preservation["verified_tables"]) == PRESERVED_TABLES | {"graph_metadata"}
    assert preservation["source_counts"] == preservation["copied_counts"]
    assert preservation["source_digests"] == preservation["copied_digests"]
    assert preservation["source_rows_retained"] is True
    assert preservation["final_counts"] == receipt["after_counts"]
    assert set(receipt["before_counts"]) == PRESERVED_TABLES
    assert all(
        receipt["after_counts"][table_name] >= source_count
        for table_name, source_count in receipt["before_counts"].items()
    )


def _logical_derived_rows(db_path: Path) -> dict[str, list[tuple[object, ...]]]:
    conn = sqlite3.connect(db_path)
    try:
        out: dict[str, list[tuple[object, ...]]] = {}
        for table_name in (
            "graph_paths",
            "graph_neighborhoods",
            "graph_sibling_links",
        ):
            columns = [
                str(row[1])
                for row in conn.execute(f"PRAGMA table_info({table_name})")
                if str(row[1]) != "created_at"
            ]
            out[table_name] = sorted(
                conn.execute(f"SELECT {','.join(columns)} FROM {table_name}").fetchall(),
                key=repr,
            )
        return out
    finally:
        conn.close()


def test_fresh_and_atomic_hardening_share_exact_direct_only_index_capability(
    tmp_path: Path,
) -> None:
    fresh_path = tmp_path / "fresh.sqlite"
    hardened_path = tmp_path / "hardened.sqlite"
    materialize_augmented_skills_graph_sqlite(repo_root=REPO, db_path=fresh_path)
    shutil.copy2(fresh_path, hardened_path)
    fresh_rows = _logical_derived_rows(fresh_path)

    receipt = apply_graphdb_capability_sqlite_hardening(
        repo_root=REPO,
        db_path=hardened_path,
    )

    assert receipt["materialization"]["graph_index_capability_version"] == (GRAPH_INDEX_CAPABILITY_VERSION)
    assert receipt["materialization"]["index_mode"] == "direct_only"
    assert _logical_derived_rows(hardened_path) == fresh_rows
    conn = sqlite3.connect(hardened_path)
    try:
        assert conn.execute("SELECT DISTINCT path_depth FROM graph_paths").fetchall() == [(1,)]
        assert conn.execute("SELECT DISTINCT distance FROM graph_neighborhoods").fetchall() == [(1,)]
        raw_summary = conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0]
        summary = json.loads(raw_summary)
        assert summary["graph_index_schema_version"] == GRAPH_INDEX_SCHEMA_VERSION
        assert summary["graph_index_capability_version"] == (GRAPH_INDEX_CAPABILITY_VERSION)
    finally:
        conn.close()


def test_atomic_hardening_discards_historical_multihop_derived_rows(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _seed_source(db_path, complete_schema=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO graph_paths(
                path_id,start_node_id,end_node_id,path_depth,path_signature,
                node_path_json,edge_path_json,edge_types_json,created_at
            ) VALUES (
                'stale_depth4','skill_a','fact_a',4,'stale',
                '["skill_a","fact_a","skill_a","fact_a","skill_a"]',
                '["edge_a","edge_a","edge_a","edge_a"]',
                '["stale","stale","stale","stale"]','old'
            )
            """
        )
        conn.execute(
            """
            INSERT INTO graph_neighborhoods(
                center_node_id,neighbor_node_id,distance,connecting_path_json,
                edge_types_json,relationship_summary
            ) VALUES (
                'skill_a','fact_a',3,
                '["skill_a","fact_a","skill_a","fact_a"]',
                '["stale","stale","stale"]','historical_distance3'
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
    _refresh_trusted_logical_digest(db_path)

    apply_graphdb_capability_sqlite_hardening(
        repo_root=tmp_path,
        db_path=db_path,
    )

    conn = sqlite3.connect(db_path)
    try:
        assert conn.execute("SELECT DISTINCT path_depth FROM graph_paths").fetchall() == [(1,)]
        assert conn.execute("SELECT DISTINCT distance FROM graph_neighborhoods").fetchall() == [(1,)]
        assert (
            conn.execute("SELECT COUNT(*) FROM graph_paths WHERE path_id='stale_depth4'").fetchone()[0] == 0
        )
    finally:
        conn.close()


@pytest.mark.parametrize(
    "tamper_sql",
    (
        "UPDATE graph_nodes SET label='Tampered canonical label' WHERE node_id='skill_runtime_gate_mesh_design'",
        "UPDATE graph_edges SET rationale='tampered edge rationale' WHERE edge_id=(SELECT edge_id FROM graph_edges ORDER BY edge_id LIMIT 1)",
    ),
    ids=("node-label", "edge-rationale"),
)
@pytest.mark.parametrize("resign_local_metadata", (False, True))
def test_hardening_rejects_canonical_projection_tampering_without_replacement(
    tmp_path: Path,
    tamper_sql: str,
    resign_local_metadata: bool,
) -> None:
    db_path = tmp_path / "tampered.sqlite"
    materialize_augmented_skills_graph_sqlite(repo_root=REPO, db_path=db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(tamper_sql)
        if resign_local_metadata:
            summary = json.loads(conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0])
            summary["sqlite_graph_digest"] = compute_sqlite_graph_digest(conn)
            conn.execute(
                "UPDATE graph_metadata SET graph_count_summary = ?",
                (json.dumps(summary, sort_keys=True),),
            )
        conn.commit()
    finally:
        conn.close()
    before = _sha256(db_path)

    with pytest.raises(ValueError, match="source authority mismatch against canonical rebuild"):
        apply_graphdb_capability_sqlite_hardening(repo_root=REPO, db_path=db_path)

    assert _sha256(db_path) == before
    _assert_no_maintenance_artifacts(db_path)
