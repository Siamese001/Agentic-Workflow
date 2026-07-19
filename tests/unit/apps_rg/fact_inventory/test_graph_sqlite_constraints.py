from __future__ import annotations

# apps-test-model: APP CONTRACT
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

import apps_rg.fact_inventory.apply_graphdb_capability_sqlite_hardening as applicator_module
import apps_rg.fact_inventory.augmented_skills_graph_sqlite as graph_sqlite_module
from apps_rg.fact_inventory.apply_graphdb_capability_sqlite_hardening import (
    apply_graphdb_capability_sqlite_hardening,
)
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    C03_SQLITE_MATERIALIZER_CODE_VERSION,
    DDL_STATEMENTS,
    materialize_augmented_skills_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    GRAPH_INDEX_SCHEMA_VERSION,
    build_graph_sibling_links,
    ensure_graphdb_capability_schema,
    require_graphdb_capability_schema,
)
from apps_rg.fact_inventory.validate_graph_sqlite_path_index import (
    validate_graph_sqlite_path_index,
)


def _create_source_db(db_path: Path, *, orphan_edge: bool = False) -> None:
    conn = sqlite3.connect(db_path)
    try:
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
        conn.executemany(
            "INSERT INTO graph_nodes(node_id,node_type,label) VALUES (?,?,?)",
            (
                ("skill_a", "skill", "Skill A"),
                ("fact_a", "fact", "Fact A"),
                ("metric_a", "metric", "Metric A"),
            ),
        )
        target = "missing_node" if orphan_edge else "fact_a"
        conn.execute(
            "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES (?,?,?,?)",
            ("edge_a", "skill_a", target, "skill_supported_by_fact"),
        )
        conn.execute(
            "INSERT INTO skill_fact_links(skill_id,fact_id) VALUES (?,?)",
            ("skill_a", "fact_a"),
        )
        conn.commit()
    finally:
        conn.close()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _refresh_generated_projection_counts(conn: sqlite3.Connection) -> None:
    summary = json.loads(conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0])
    for key, table_name in (
        ("graph_path_count", "graph_paths"),
        ("graph_neighborhood_count", "graph_neighborhoods"),
        ("graph_sibling_link_count", "graph_sibling_links"),
    ):
        summary[key] = int(conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])
    conn.execute(
        "UPDATE graph_metadata SET graph_count_summary=?",
        (json.dumps(summary, sort_keys=True),),
    )
    conn.commit()


def test_fresh_capability_schema_enforces_safe_row_constraints() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    for ddl in DDL_STATEMENTS[:3]:
        conn.execute(ddl)
    conn.commit()
    try:
        ensure_graphdb_capability_schema(conn)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO graph_paths (
                    path_id,start_node_id,end_node_id,path_depth,path_signature,
                    node_path_json,edge_path_json,edge_types_json,created_at
                ) VALUES ('bad','missing','missing',0,'bad','[]','[]','[]','t')
                """
            )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO graph_sibling_links (node_id,sibling_node_id)
                VALUES ('skill_a','skill_a')
                """
            )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO section_evidence_budget (
                    section_id,role_family_key,max_metric_reuse,max_fact_family_reuse
                ) VALUES ('experience','*',-1,1)
                """
            )
    finally:
        conn.close()


def test_fresh_materializer_schema_declares_expected_foreign_keys() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        for ddl in DDL_STATEMENTS:
            conn.execute(ddl)
        expected = {
            "graph_edges": {
                ("source_node_id", "graph_nodes", "node_id"),
                ("target_node_id", "graph_nodes", "node_id"),
            },
            "skill_fact_links": {
                ("skill_id", "graph_nodes", "node_id"),
                ("fact_id", "graph_nodes", "node_id"),
            },
            "section_eligibility": {("node_id", "graph_nodes", "node_id")},
            "c03_skill_selection_features": {("skill_id", "graph_nodes", "node_id")},
            "c03_role_family_skill_weights": {("skill_id", "graph_nodes", "node_id")},
            "graph_paths": {
                ("start_node_id", "graph_nodes", "node_id"),
                ("end_node_id", "graph_nodes", "node_id"),
            },
            "graph_neighborhoods": {
                ("center_node_id", "graph_nodes", "node_id"),
                ("neighbor_node_id", "graph_nodes", "node_id"),
            },
            "graph_sibling_links": {
                ("node_id", "graph_nodes", "node_id"),
                ("sibling_node_id", "graph_nodes", "node_id"),
                ("shared_parent_node_id", "graph_nodes", "node_id"),
            },
        }
        for table, expected_mappings in expected.items():
            actual = {
                (str(row[3]), str(row[2]), str(row[4]))
                for row in conn.execute(f"PRAGMA foreign_key_list({table})")
            }
            assert actual == expected_mappings
    finally:
        conn.close()


def test_fresh_materializer_schema_uses_context_preserving_sibling_primary_key() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        for ddl in DDL_STATEMENTS:
            conn.execute(ddl)
        primary_key = tuple(
            str(row[1])
            for row in sorted(
                conn.execute("PRAGMA table_info(graph_sibling_links)"),
                key=lambda row: int(row[5]) if int(row[5]) else 999,
            )
            if int(row[5])
        )
        assert primary_key == (
            "node_id",
            "sibling_node_id",
            "shared_parent_node_id",
            "shared_edge_type",
        )
        assert (
            tuple(str(row[2]) for row in conn.execute("PRAGMA index_info(idx_sibling_context_lookup)"))
            == primary_key
        )
    finally:
        conn.close()


def test_graph_health_policy_requires_sibling_parent_foreign_key() -> None:
    policy = json.loads(
        (Path(__file__).resolve().parents[4] / "apps_rg/config/c03_graph_health_policy.v2.json").read_text(
            encoding="utf-8"
        )
    )

    assert policy["policy_version"] == "c03_graph_health_policy.v4.producer_bound_operational_evidence"
    assert {
        "table": "graph_sibling_links",
        "from": "shared_parent_node_id",
        "to_table": "graph_nodes",
        "to": "node_id",
    } in policy["required_foreign_keys"]


def test_require_schema_rejects_legacy_two_column_sibling_primary_key() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    for ddl in DDL_STATEMENTS[:3]:
        conn.execute(ddl)
    conn.commit()
    try:
        ensure_graphdb_capability_schema(conn)
        conn.execute("DROP TABLE graph_sibling_links")
        conn.execute(
            """
            CREATE TABLE graph_sibling_links (
                node_id TEXT NOT NULL,
                sibling_node_id TEXT NOT NULL,
                sibling_reason TEXT NOT NULL DEFAULT '',
                shared_parent_node_id TEXT NOT NULL DEFAULT '',
                shared_edge_type TEXT NOT NULL DEFAULT '',
                sibling_score REAL NOT NULL DEFAULT 0.0,
                PRIMARY KEY (node_id, sibling_node_id),
                CHECK (node_id <> sibling_node_id),
                FOREIGN KEY (node_id) REFERENCES graph_nodes(node_id),
                FOREIGN KEY (sibling_node_id) REFERENCES graph_nodes(node_id)
            )
            """
        )
        conn.execute("CREATE INDEX idx_sibling_node ON graph_sibling_links(node_id)")
        conn.execute("CREATE INDEX idx_sibling_peer ON graph_sibling_links(sibling_node_id)")
        conn.execute(
            "CREATE INDEX idx_sibling_node_score ON graph_sibling_links(node_id, sibling_score DESC)"
        )
        conn.commit()

        with pytest.raises(ValueError, match="graph_sibling_links primary key mismatch"):
            require_graphdb_capability_schema(conn)
    finally:
        conn.close()


def test_legacy_schema_cannot_be_stamped_as_current_and_applicator_rebuilds_it(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "legacy.sqlite"
    _create_source_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        with pytest.raises(ValueError, match="explicit atomic applicator"):
            ensure_graphdb_capability_schema(conn)
        assert "graph_paths" not in {
            str(row[0]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    finally:
        conn.close()

    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)
    conn = sqlite3.connect(db_path)
    try:
        schema = require_graphdb_capability_schema(conn)
        assert schema["graph_index_schema_version"] == GRAPH_INDEX_SCHEMA_VERSION
        graph_edge_sql = "".join(
            str(
                conn.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table' AND name='graph_edges'"
                ).fetchone()[0]
            )
            .lower()
            .split()
        )
        assert "check(weight>=0.0andweight<=1.0)" in graph_edge_sql
        assert {
            (str(row[3]), str(row[2]), str(row[4]))
            for row in conn.execute("PRAGMA foreign_key_list(graph_edges)")
        } == {
            ("source_node_id", "graph_nodes", "node_id"),
            ("target_node_id", "graph_nodes", "node_id"),
        }
        summary = json.loads(conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0])
        assert summary["c03_sqlite_materializer_code_version"] == C03_SQLITE_MATERIALIZER_CODE_VERSION
        assert summary["graph_index_schema_version"] == GRAPH_INDEX_SCHEMA_VERSION
    finally:
        conn.close()


def test_graph_edge_weight_constraint_rejects_out_of_range_values() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        for ddl in DDL_STATEMENTS[:3]:
            conn.execute(ddl)
        conn.executemany(
            """
            INSERT INTO graph_nodes (
                node_id,node_type,label,created_at,updated_at
            ) VALUES (?,?,?,?,?)
            """,
            (("a", "skill", "A", "t", "t"), ("b", "fact", "B", "t", "t")),
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO graph_edges (
                    edge_id,source_node_id,target_node_id,edge_type,weight
                ) VALUES ('bad','a','b','supports',1.01)
                """
            )
    finally:
        conn.close()


def test_validator_rejects_cross_row_corruption(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        conn.execute(
            """
            INSERT INTO graph_paths (
                path_id,start_node_id,end_node_id,path_depth,path_signature,
                node_path_json,edge_path_json,edge_types_json,created_at
            ) VALUES ('orphan','skill_a','missing_node',1,'skill_a->missing_node',
                      '["skill_a","missing_node"]','["missing_edge"]','["bad"]','t')
            """
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(ValueError, match="foreign_key_check|broken_graph_paths"):
        validate_graph_sqlite_path_index(
            repo_root=tmp_path,
            db_path=db_path,
            materialize_if_missing=False,
        )


def test_validator_rejects_missing_direct_edge_path_with_refreshed_count(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) "
            "VALUES ('edge_b','skill_a','metric_a','skill_can_surface_metric')"
        )
        conn.commit()
    finally:
        conn.close()
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "DELETE FROM graph_paths WHERE path_id=("
            "SELECT path_id FROM graph_paths WHERE path_depth=1 LIMIT 1)"
        )
        _refresh_generated_projection_counts(conn)
    finally:
        conn.close()

    with pytest.raises(
        ValueError,
        match="graph_edge_depth1_path_identity_mismatches=1",
    ):
        validate_graph_sqlite_path_index(repo_root=tmp_path, db_path=db_path)


def test_validator_rejects_missing_direct_neighborhood_with_refreshed_count(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "DELETE FROM graph_neighborhoods WHERE rowid=("
            "SELECT rowid FROM graph_neighborhoods WHERE distance=1 LIMIT 1)"
        )
        _refresh_generated_projection_counts(conn)
    finally:
        conn.close()

    with pytest.raises(
        ValueError,
        match="graph_edge_distance1_neighborhood_mismatches=1",
    ):
        validate_graph_sqlite_path_index(repo_root=tmp_path, db_path=db_path)


def test_validator_rejects_missing_reciprocal_sibling_context_set(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.executemany(
            "INSERT INTO graph_nodes(node_id,node_type,label) VALUES (?,?,?)",
            (
                ("parent_a", "capability_domain", "Parent A"),
                ("skill_b", "skill", "Skill B"),
            ),
        )
        conn.executemany(
            "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES (?,?,?,?)",
            (
                (
                    "edge_parent_skill",
                    "parent_a",
                    "skill_a",
                    "capability_domain_contains_skill",
                ),
                (
                    "edge_parent_skill_b",
                    "parent_a",
                    "skill_b",
                    "capability_domain_contains_skill",
                ),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    try:
        deleted = conn.execute(
            "DELETE FROM graph_sibling_links WHERE shared_parent_node_id='parent_a' "
            "AND shared_edge_type='capability_domain_contains_skill'"
        ).rowcount
        assert deleted == 2
        _refresh_generated_projection_counts(conn)
    finally:
        conn.close()

    with pytest.raises(
        ValueError,
        match="graph_sibling_context_set_mismatches=2",
    ):
        validate_graph_sqlite_path_index(repo_root=tmp_path, db_path=db_path)


def test_validator_rejects_malformed_json_projection_data(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA ignore_check_constraints=ON")
        conn.execute(
            """
            UPDATE section_evidence_budget
            SET required_node_types_json = 'not-json'
            WHERE section_id = 'executive_summary' AND role_family_key = '*'
            """
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(ValueError, match="malformed_section_evidence_budget_json"):
        validate_graph_sqlite_path_index(
            repo_root=tmp_path,
            db_path=db_path,
            materialize_if_missing=False,
        )


def test_validator_rejects_path_edge_continuity_corruption(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO graph_edges (
                edge_id,source_node_id,target_node_id,edge_type
            ) VALUES ('edge_b','skill_a','metric_a','skill_can_surface_metric')
            """
        )
        conn.execute(
            """
            UPDATE graph_paths
            SET edge_path_json='["edge_b"]',
                edge_types_json='["skill_can_surface_metric"]'
            WHERE path_depth=1
            """
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(ValueError, match="graph_path_edge_continuity_mismatches"):
        validate_graph_sqlite_path_index(repo_root=tmp_path, db_path=db_path)


def test_validator_rejects_neighborhood_hop_corruption(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "UPDATE graph_neighborhoods "
            "SET edge_types_json='[\"not_an_edge_type\"]' "
            "WHERE rowid=(SELECT rowid FROM graph_neighborhoods LIMIT 1)"
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(ValueError, match="graph_neighborhood_hop_continuity_mismatches"):
        validate_graph_sqlite_path_index(repo_root=tmp_path, db_path=db_path)


def test_validator_rejects_reverse_view_multiset_drift(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    try:
        original_sql = str(
            conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='view' AND name='graph_edges_reverse'"
            ).fetchone()[0]
        )
        conn.execute("DROP VIEW graph_edges_reverse")
        conn.execute(original_sql + " WHERE 0")
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(ValueError, match="reverse_view_multiset_mismatches"):
        validate_graph_sqlite_path_index(repo_root=tmp_path, db_path=db_path)


def test_validator_requires_graph_metadata(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DELETE FROM graph_metadata")
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(ValueError, match="graph_metadata_row_count=0"):
        validate_graph_sqlite_path_index(repo_root=tmp_path, db_path=db_path)


def test_atomic_applicator_cas_rejects_committed_concurrent_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    original_materializer = applicator_module.materialize_graphdb_capability_indexes

    def materialize_then_race(conn: sqlite3.Connection) -> dict[str, object]:
        result = original_materializer(conn)
        writer = sqlite3.connect(db_path)
        try:
            writer.execute(
                "INSERT INTO graph_nodes(node_id,node_type,label) VALUES (?,?,?)",
                ("concurrent_node", "fact", "Concurrent node"),
            )
            writer.commit()
        finally:
            writer.close()
        return result

    monkeypatch.setattr(
        applicator_module,
        "materialize_graphdb_capability_indexes",
        materialize_then_race,
    )

    with pytest.raises(RuntimeError, match="changed during maintenance"):
        apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    conn = sqlite3.connect(db_path)
    try:
        assert (
            conn.execute("SELECT COUNT(*) FROM graph_nodes WHERE node_id='concurrent_node'").fetchone()[0]
            == 1
        )
        assert "graph_paths" not in {
            str(row[0]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    finally:
        conn.close()


def test_isolated_temp_writer_refuses_canonical_target(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"

    with pytest.raises(RuntimeError, match="unique sibling temp path.*refuses"):
        graph_sqlite_module._open_isolated_temp_graph_sqlite(
            temp_path=db_path,
            canonical_target=db_path,
        )

    assert not db_path.exists()


def test_applicator_writes_only_sibling_temp_before_atomic_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    events: list[tuple[str, Path, Path]] = []
    original_open = applicator_module._open_isolated_temp_graph_sqlite
    original_replace = applicator_module._replace_sqlite_projection_if_unchanged

    def record_open(
        *,
        temp_path: Path,
        canonical_target: Path,
    ) -> sqlite3.Connection:
        events.append(("open", temp_path, canonical_target))
        conn = original_open(
            temp_path=temp_path,
            canonical_target=canonical_target,
        )
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        return conn

    def record_replace(
        *,
        target: Path,
        replacement: Path,
        expected_digest: str | None,
    ) -> None:
        events.append(("replace", replacement, target))
        original_replace(
            target=target,
            replacement=replacement,
            expected_digest=expected_digest,
        )

    monkeypatch.setattr(
        applicator_module,
        "_open_isolated_temp_graph_sqlite",
        record_open,
    )
    monkeypatch.setattr(
        applicator_module,
        "_replace_sqlite_projection_if_unchanged",
        record_replace,
    )

    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    assert [event[0] for event in events] == ["open", "open", "replace"]
    opened_temp_paths: list[Path] = []
    for _kind, temp_path, canonical_target in events[:2]:
        assert canonical_target == db_path
        assert temp_path != db_path
        assert temp_path.parent == db_path.parent
        assert temp_path.name.startswith(f".{db_path.name}.")
        assert temp_path.name.endswith(".tmp")
        opened_temp_paths.append(temp_path)
    assert len(set(opened_temp_paths)) == 2
    assert events[2][1:] == (opened_temp_paths[1], db_path)


def test_materializer_writes_only_sibling_temp_before_atomic_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    events: list[tuple[str, Path, Path]] = []
    original_open = graph_sqlite_module._open_isolated_temp_graph_sqlite
    original_replace = graph_sqlite_module._replace_sqlite_projection_if_unchanged

    def record_open(
        *,
        temp_path: Path,
        canonical_target: Path,
    ) -> sqlite3.Connection:
        events.append(("open", temp_path, canonical_target))
        conn = original_open(
            temp_path=temp_path,
            canonical_target=canonical_target,
        )
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        return conn

    def record_replace(
        *,
        target: Path,
        replacement: Path,
        expected_digest: str | None,
    ) -> None:
        events.append(("replace", replacement, target))
        original_replace(
            target=target,
            replacement=replacement,
            expected_digest=expected_digest,
        )

    monkeypatch.setattr(
        graph_sqlite_module,
        "_open_isolated_temp_graph_sqlite",
        record_open,
    )
    monkeypatch.setattr(
        graph_sqlite_module,
        "_replace_sqlite_projection_if_unchanged",
        record_replace,
    )

    materialize_augmented_skills_graph_sqlite(
        repo_root=Path(__file__).resolve().parents[4],
        db_path=db_path,
    )

    assert [event[0] for event in events] == ["open", "replace"]
    _kind, temp_path, canonical_target = events[0]
    assert canonical_target == db_path
    assert temp_path != db_path
    assert temp_path.parent == db_path.parent
    assert temp_path.name.startswith(f".{db_path.name}.")
    assert temp_path.name.endswith(".tmp")
    assert events[1][1:] == (temp_path, db_path)


def test_atomic_applicator_preserves_original_database_when_validation_fails(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "malformed.sqlite"
    _create_source_db(db_path, orphan_edge=True)
    before = _sha256(db_path)

    with pytest.raises(ValueError, match="broken_graph_edges"):
        apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)

    assert _sha256(db_path) == before
    conn = sqlite3.connect(db_path)
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "graph_paths" not in tables
    finally:
        conn.close()


def test_atomic_materializer_preserves_target_when_sidecar_blocks_replace(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "graph.sqlite"
    sidecar = Path(f"{db_path}-wal")
    db_path.write_bytes(b"existing-projection")
    sidecar.write_bytes(b"active-writer")

    with pytest.raises(RuntimeError, match="sidecars exist"):
        materialize_augmented_skills_graph_sqlite(
            repo_root=Path.cwd(),
            db_path=db_path,
        )

    assert db_path.read_bytes() == b"existing-projection"
    assert sidecar.read_bytes() == b"active-writer"
    assert list(tmp_path.glob(f".{db_path.name}.*.tmp")) == []


def test_sibling_materialization_receipt_reports_persisted_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    _create_source_db(db_path)
    apply_graphdb_capability_sqlite_hardening(repo_root=tmp_path, db_path=db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.executemany(
            """
            INSERT INTO graph_nodes(
                node_id,node_type,label,created_at,updated_at
            ) VALUES (?,?,?,'t','t')
            """,
            (
                ("parent_a", "capability_domain", "Parent A"),
                ("parent_b", "career_epoch", "Parent B"),
                ("skill_b", "skill", "Skill B"),
            ),
        )
        conn.executemany(
            "INSERT INTO graph_edges(edge_id,source_node_id,target_node_id,edge_type) VALUES (?,?,?,?)",
            (
                ("edge_parent_a", "parent_a", "skill_a", "contains"),
                ("edge_parent_b", "parent_a", "skill_b", "contains"),
                ("edge_parent_a_alt", "parent_b", "skill_a", "supports"),
                ("edge_parent_b_alt", "parent_b", "skill_b", "supports"),
            ),
        )
        conn.commit()
        receipt = build_graph_sibling_links(conn)
        persisted = int(conn.execute("SELECT COUNT(*) FROM graph_sibling_links").fetchone()[0])
        contexts = {
            tuple(row)
            for row in conn.execute(
                """
                SELECT node_id,sibling_node_id,shared_parent_node_id,shared_edge_type
                FROM graph_sibling_links
                """
            )
        }
    finally:
        conn.close()

    assert persisted == 4
    assert receipt["graph_sibling_links_materialized"] == persisted
    assert contexts == {
        ("skill_a", "skill_b", "parent_a", "contains"),
        ("skill_b", "skill_a", "parent_a", "contains"),
        ("skill_a", "skill_b", "parent_b", "supports"),
        ("skill_b", "skill_a", "parent_b", "supports"),
    }
