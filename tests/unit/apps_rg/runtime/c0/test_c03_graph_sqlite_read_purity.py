"""apps-test-model: APP CONTRACT.

Read-only C0.3 graph inspection stays pure; production assembly may refresh generated state.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

import apps_rg.runtime.c03_graph_sqlite_context as context_module
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    C03_SQLITE_MATERIALIZER_CODE_VERSION,
    materialize_augmented_skills_graph_sqlite,
    open_graph_sqlite,
)
from apps_rg.fact_inventory.graph_sqlite_path_index import (
    compute_sqlite_graph_digest,
)
from apps_rg.runtime.c0.c03_errors import C03GraphProjectionUnavailableError
from apps_rg.runtime.c0.c03_sqlite_graph_selection import (
    select_c03_sqlite_graph_candidates,
)
from apps_rg.runtime.c03_graph_sqlite_context import (
    assemble_c03_graph_sqlite_context,
    ensure_c03_graph_sqlite,
    require_c03_graph_sqlite,
)

REPO = Path(__file__).resolve().parents[5]
ROLE_FAMILY = "SVP_ENGINEERING_AI_PLATFORM"
FACT_ID = "fact_engineering_platform_001"


def _projection_state(db_path: Path) -> tuple[str, tuple[str, ...]]:
    digest = hashlib.sha256(db_path.read_bytes()).hexdigest()
    sidecars = tuple(
        sorted(path.name for path in db_path.parent.iterdir() if path.name.startswith(f"{db_path.name}-"))
    )
    return digest, sidecars


@pytest.fixture(scope="module")
def materialized_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    db_path = tmp_path_factory.mktemp("c03_graph_read_purity") / "template.sqlite"
    materialize_augmented_skills_graph_sqlite(repo_root=REPO, db_path=db_path)
    return db_path


@pytest.fixture
def sqlite_db(tmp_path: Path, materialized_template: Path) -> Path:
    db_path = tmp_path / "c03_graph.sqlite"
    shutil.copy2(materialized_template, db_path)
    return db_path


def _read_only_runtime_readers(db_path: Path) -> list[tuple[str, Callable[[], Any]]]:
    return [
        (
            "require",
            lambda: require_c03_graph_sqlite(REPO, db_path),
        ),
        (
            "select",
            lambda: select_c03_sqlite_graph_candidates(
                section_id="executive_summary",
                selected_fact_ids=[FACT_ID],
                role_family_key=ROLE_FAMILY,
                repo_root=REPO,
                db_path=db_path,
            ),
        ),
    ]


def _assert_runtime_readers_reject_without_mutation(
    db_path: Path,
    *,
    match: str,
) -> None:
    before = _projection_state(db_path)
    for _reader_name, read in _read_only_runtime_readers(db_path):
        with pytest.raises(C03GraphProjectionUnavailableError, match=match):
            read()
        assert _projection_state(db_path) == before


def test_missing_runtime_projection_is_not_created(tmp_path: Path) -> None:
    db_path = tmp_path / "missing" / "c03_graph.sqlite"

    for _reader_name, read in _read_only_runtime_readers(db_path):
        with pytest.raises(
            C03GraphProjectionUnavailableError,
            match="unavailable|missing",
        ) as exc_info:
            read()
        assert str(db_path) in str(exc_info.value)
        assert not db_path.exists()
        assert not db_path.parent.exists()


def test_ensure_remains_the_explicit_projection_setup_writer(tmp_path: Path) -> None:
    db_path = tmp_path / "setup" / "c03_graph.sqlite"

    assert ensure_c03_graph_sqlite(REPO, db_path) == db_path
    assert db_path.is_file()
    assert require_c03_graph_sqlite(REPO, db_path) == db_path


def test_production_assembly_rebuilds_stale_materializer_version(
    sqlite_db: Path,
) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        raw_summary = conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0]
        summary = json.loads(str(raw_summary))
        summary["c03_sqlite_materializer_code_version"] = "stale-materializer-version"
        conn.execute(
            "UPDATE graph_metadata SET graph_count_summary = ?",
            (json.dumps(summary, sort_keys=True),),
        )
        conn.commit()
    finally:
        conn.close()

    bundle = assemble_c03_graph_sqlite_context(
        role_family_key=ROLE_FAMILY,
        section_id="executive_summary",
        selected_fact_ids=[FACT_ID],
        repo_root=REPO,
        db_path=sqlite_db,
    )

    assert bundle["receipt"]["c03_integration_status"] == "SQLITE_CONTEXT_AVAILABLE"
    conn = sqlite3.connect(str(sqlite_db))
    try:
        rebuilt_summary = json.loads(
            str(conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0])
        )
    finally:
        conn.close()
    assert rebuilt_summary["c03_sqlite_materializer_code_version"] == C03_SQLITE_MATERIALIZER_CODE_VERSION
    assert require_c03_graph_sqlite(REPO, sqlite_db) == sqlite_db


def test_stale_runtime_projection_preserves_database_bytes(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        conn.execute("UPDATE graph_metadata SET ledger_hash = ?", ("stale-ledger-digest",))
        conn.commit()
    finally:
        conn.close()
    before = _projection_state(sqlite_db)

    for _reader_name, read in _read_only_runtime_readers(sqlite_db):
        with pytest.raises(C03GraphProjectionUnavailableError, match="stale"):
            read()
        assert _projection_state(sqlite_db) == before


@pytest.mark.parametrize("authority_status", ["", "untrusted_graph_projection"])
def test_runtime_admission_rejects_untrusted_authority_status_without_mutation(
    sqlite_db: Path,
    authority_status: str,
) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        conn.execute(
            "UPDATE graph_metadata SET authority_status = ?",
            (authority_status,),
        )
        conn.commit()
    finally:
        conn.close()

    _assert_runtime_readers_reject_without_mutation(
        sqlite_db,
        match="authority_status is not trusted",
    )


def test_projection_validation_type_error_is_translated_to_typed_unavailable(
    sqlite_db: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = _projection_state(sqlite_db)

    def fail_validation(*_args: Any, **_kwargs: Any) -> None:
        raise TypeError("malformed projection validation input")

    monkeypatch.setattr(
        context_module,
        "validate_graphdb_capability_integrity",
        fail_validation,
    )

    with pytest.raises(
        C03GraphProjectionUnavailableError,
        match="malformed projection validation input",
    ):
        require_c03_graph_sqlite(REPO, sqlite_db)
    assert _projection_state(sqlite_db) == before


@pytest.mark.parametrize(
    "table_name",
    [
        "graph_nodes",
        "graph_paths",
        "graph_neighborhoods",
        "graph_sibling_links",
        "section_evidence_budget",
    ],
)
def test_runtime_reads_reject_population_count_drift_without_mutation(
    sqlite_db: Path,
    table_name: str,
) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        before_count = int(conn.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0])
        assert before_count > 0
        conn.execute(f'DELETE FROM "{table_name}" WHERE rowid = (SELECT rowid FROM "{table_name}" LIMIT 1)')
        conn.commit()
    finally:
        conn.close()
    before = _projection_state(sqlite_db)

    for _reader_name, read in _read_only_runtime_readers(sqlite_db):
        with pytest.raises(
            C03GraphProjectionUnavailableError,
            match=f"{table_name} population count mismatch",
        ):
            read()
        assert _projection_state(sqlite_db) == before


@pytest.mark.parametrize(
    "update_sql",
    [
        """
        UPDATE graph_nodes
        SET label = COALESCE(label, '') || ' [tampered]'
        WHERE rowid = (SELECT rowid FROM graph_nodes ORDER BY node_id LIMIT 1)
        """,
        """
        UPDATE graph_nodes
        SET external_eligible = CASE external_eligible WHEN 1 THEN 0 ELSE 1 END
        WHERE rowid = (SELECT rowid FROM graph_nodes ORDER BY node_id LIMIT 1)
        """,
        """
        UPDATE skill_fact_links
        SET claim_eligibility = CASE claim_eligibility WHEN 1 THEN 0 ELSE 1 END
        WHERE rowid = (
            SELECT rowid FROM skill_fact_links ORDER BY skill_id, fact_id LIMIT 1
        )
        """,
    ],
    ids=("node-label", "node-eligibility", "skill-fact-authority"),
)
def test_runtime_reads_reject_same_count_canonical_row_tampering(
    sqlite_db: Path,
    update_sql: str,
) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        cursor = conn.execute(update_sql)
        assert cursor.rowcount == 1
        conn.commit()
    finally:
        conn.close()

    _assert_runtime_readers_reject_without_mutation(
        sqlite_db,
        match="graph_metadata_sqlite_digest_mismatch",
    )


@pytest.mark.parametrize(
    ("update_sql", "expected_integrity_error"),
    [
        (
            """
            UPDATE graph_paths
            SET node_path_json = json_set(node_path_json, '$[#-1]', start_node_id)
            WHERE rowid = (
                SELECT rowid FROM graph_paths
                WHERE start_node_id <> end_node_id
                ORDER BY path_id LIMIT 1
            )
            """,
            "graph_path_endpoint_mismatches",
        ),
        (
            """
            UPDATE graph_sibling_links
            SET shared_parent_node_id = node_id
            WHERE rowid = (
                SELECT rowid FROM graph_sibling_links
                WHERE shared_parent_node_id <> ''
                  AND shared_parent_node_id <> node_id
                ORDER BY node_id, sibling_node_id LIMIT 1
            )
            """,
            "broken_graph_sibling_parent_edges",
        ),
        (
            """
            UPDATE graph_neighborhoods
            SET connecting_path_json = json_set(
                connecting_path_json,
                '$[#-1]',
                center_node_id
            )
            WHERE rowid = (
                SELECT rowid FROM graph_neighborhoods
                WHERE center_node_id <> neighbor_node_id
                ORDER BY center_node_id, neighbor_node_id LIMIT 1
            )
            """,
            "graph_neighborhood_endpoint_mismatches",
        ),
    ],
    ids=("path", "sibling", "neighborhood"),
)
def test_runtime_reads_reject_same_count_derived_projection_corruption(
    sqlite_db: Path,
    update_sql: str,
    expected_integrity_error: str,
) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        cursor = conn.execute(update_sql)
        assert cursor.rowcount == 1
        conn.commit()
    finally:
        conn.close()

    _assert_runtime_readers_reject_without_mutation(
        sqlite_db,
        match=expected_integrity_error,
    )


def test_runtime_reads_reject_wrong_skill_fact_endpoint_type_even_with_fresh_digest(
    sqlite_db: Path,
) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        skill_id, fact_id = conn.execute(
            """
            SELECT skill_id, fact_id
            FROM skill_fact_links
            ORDER BY skill_id, fact_id
            LIMIT 1
            """
        ).fetchone()
        wrong_endpoint = conn.execute(
            """
            SELECT n.node_id
            FROM graph_nodes n
            WHERE n.node_type = 'skill'
              AND n.node_id <> ?
              AND NOT EXISTS (
                  SELECT 1
                  FROM skill_fact_links l
                  WHERE l.skill_id = ? AND l.fact_id = n.node_id
              )
            ORDER BY n.node_id
            LIMIT 1
            """,
            (skill_id, skill_id),
        ).fetchone()
        assert wrong_endpoint is not None
        cursor = conn.execute(
            """
            UPDATE skill_fact_links
            SET fact_id = ?
            WHERE skill_id = ? AND fact_id = ?
            """,
            (wrong_endpoint[0], skill_id, fact_id),
        )
        assert cursor.rowcount == 1

        raw_summary = conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0]
        summary = json.loads(str(raw_summary))
        summary["sqlite_graph_digest"] = compute_sqlite_graph_digest(conn)
        conn.execute(
            "UPDATE graph_metadata SET graph_count_summary = ?",
            (json.dumps(summary, sort_keys=True),),
        )
        conn.commit()
    finally:
        conn.close()

    _assert_runtime_readers_reject_without_mutation(
        sqlite_db,
        match="broken_skill_fact_links",
    )


def test_runtime_reads_reject_stale_sqlite_graph_digest(sqlite_db: Path) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        raw_summary = conn.execute("SELECT graph_count_summary FROM graph_metadata").fetchone()[0]
        summary = json.loads(str(raw_summary))
        summary["sqlite_graph_digest"] = "stale-sqlite-graph-digest"
        conn.execute(
            "UPDATE graph_metadata SET graph_count_summary = ?",
            (json.dumps(summary, sort_keys=True),),
        )
        conn.commit()
    finally:
        conn.close()

    _assert_runtime_readers_reject_without_mutation(
        sqlite_db,
        match="graph_metadata_sqlite_digest_mismatch",
    )


def test_malformed_role_family_projection_fails_typed_without_mutation(
    sqlite_db: Path,
) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        conn.execute("ALTER TABLE role_family_projection RENAME TO role_family_projection_source")
        conn.execute("CREATE TABLE role_family_projection (role_family_id TEXT PRIMARY KEY)")
        conn.execute(
            "INSERT INTO role_family_projection (role_family_id) "
            "SELECT role_family_id FROM role_family_projection_source"
        )
        conn.commit()
    finally:
        conn.close()
    before = _projection_state(sqlite_db)

    for _reader_name, read in _read_only_runtime_readers(sqlite_db):
        with pytest.raises(
            C03GraphProjectionUnavailableError,
            match="role_family_projection missing columns",
        ):
            read()
        assert _projection_state(sqlite_db) == before


def test_runtime_reads_work_with_read_only_query_only_connections(
    sqlite_db: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = _projection_state(sqlite_db)

    def open_query_only(**kwargs: Any) -> sqlite3.Connection:
        kwargs["read_only"] = True
        conn = open_graph_sqlite(**kwargs)
        conn.execute("PRAGMA query_only = ON")
        return conn

    monkeypatch.setattr(context_module, "open_graph_sqlite", open_query_only)

    assert require_c03_graph_sqlite(REPO, sqlite_db) == sqlite_db
    context = assemble_c03_graph_sqlite_context(
        role_family_key=ROLE_FAMILY,
        section_id="executive_summary",
        selected_fact_ids=[FACT_ID],
        repo_root=REPO,
        db_path=sqlite_db,
    )
    selection = select_c03_sqlite_graph_candidates(
        section_id="executive_summary",
        selected_fact_ids=[FACT_ID],
        role_family_key=ROLE_FAMILY,
        repo_root=REPO,
        db_path=sqlite_db,
    )

    assert context["receipt"]["c03_integration_status"] == "SQLITE_CONTEXT_AVAILABLE"
    assert context["receipt"]["path_index_status"] == "AVAILABLE"
    assert context["receipt"]["canonical_ledger_hash"] == context["receipt"]["graph_hash"]
    assert context["receipt"]["sqlite_logical_digest"]
    assert context["receipt"]["sqlite_schema_digest"]
    assert context["receipt"]["resume_metric_usage_ranking_input_digest"]
    assert selection["selected_candidates"]
    assert _projection_state(sqlite_db) == before


def test_assembly_reuses_one_validated_transaction_for_all_queries(
    sqlite_db: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = _projection_state(sqlite_db)
    real_open = context_module.open_graph_sqlite
    real_validate = context_module._validate_c03_graph_sqlite_connection
    opened_connections: list[Any] = []
    validation_connections: list[Any] = []
    open_modes: list[bool] = []
    traces: dict[int, list[tuple[bool, str]]] = {}

    def recording_open_graph_sqlite(**kwargs: Any) -> Any:
        connection = real_open(**kwargs)
        opened_connections.append(connection)
        open_modes.append(bool(kwargs.get("read_only")))
        return connection

    def recording_validation(
        connection: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        trace: list[tuple[bool, str]] = []
        traces[id(connection)] = trace
        connection.set_trace_callback(
            lambda statement: trace.append((bool(connection.in_transaction), str(statement)))
        )
        validation_connections.append(connection)
        return real_validate(connection, **kwargs)

    monkeypatch.setattr(
        context_module,
        "open_graph_sqlite",
        recording_open_graph_sqlite,
    )
    monkeypatch.setattr(
        context_module,
        "_validate_c03_graph_sqlite_connection",
        recording_validation,
    )

    bundle = assemble_c03_graph_sqlite_context(
        role_family_key=ROLE_FAMILY,
        section_id="executive_summary",
        selected_fact_ids=[FACT_ID],
        repo_root=REPO,
        db_path=sqlite_db,
    )

    assert bundle["receipt"]["c03_integration_status"] == "SQLITE_CONTEXT_AVAILABLE"
    assert open_modes == [True, True]
    assert len(opened_connections) == 2
    assert opened_connections[0] is not opened_connections[1]
    assert validation_connections == opened_connections

    assembly_trace = traces[id(opened_connections[1])]
    assert assembly_trace
    assert all(in_transaction for in_transaction, _statement in assembly_trace)
    assembly_sql = "\n".join(statement.lower() for _state, statement in assembly_trace)
    for required_query_surface in (
        "from role_family_projection",
        "from graph_nodes",
        "from graph_edges",
        "from section_eligibility",
        "from skill_fact_links",
        "from graph_paths",
        "from graph_sibling_links",
        "from section_evidence_budget",
        "from graph_selection_rejections",
        "from v_partner_architecture_competency_candidates",
        "from resume_metric_usage",
    ):
        assert required_query_surface in assembly_sql
    assert _projection_state(sqlite_db) == before


def test_authority_mutation_without_refreshed_metadata_is_rejected(
    sqlite_db: Path,
) -> None:
    conn = sqlite3.connect(str(sqlite_db))
    try:
        conn.execute(
            "UPDATE skill_fact_links SET claim_eligibility = 0 WHERE fact_id = ?",
            (FACT_ID,),
        )
        conn.commit()
    finally:
        conn.close()
    _assert_runtime_readers_reject_without_mutation(
        sqlite_db,
        match="graph_metadata_sqlite_digest_mismatch",
    )


def test_path_index_operational_error_is_not_masked_as_available(
    sqlite_db: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = _projection_state(sqlite_db)

    def fail_path_query(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
        raise context_module.sqlite3.OperationalError("path index unavailable")

    monkeypatch.setattr(context_module, "query_reverse_metric_paths", fail_path_query)
    monkeypatch.setattr(
        context_module,
        "default_graph_sqlite_path",
        lambda _repo_root: sqlite_db,
    )

    with pytest.raises(C03GraphProjectionUnavailableError, match="path index unavailable"):
        assemble_c03_graph_sqlite_context(
            role_family_key=ROLE_FAMILY,
            section_id="executive_summary",
            selected_fact_ids=[FACT_ID],
            repo_root=REPO,
            db_path=sqlite_db,
        )

    enriched = context_module.enrich_c03_bound_with_sqlite_context(
        {"section_id": "executive_summary"},
        role_family_key=ROLE_FAMILY,
        selected_fact_ids=[FACT_ID],
        repo_root=REPO,
    )
    assert enriched["c03_sqlite_attach_status"] == "DEGRADED"
    assert enriched["c03_sqlite_context_status"] == "UNAVAILABLE"
    assert "path index unavailable" in enriched["c03_sqlite_context_error"]
    assert "SQLITE_CONTEXT_AVAILABLE" not in str(enriched)
    assert _projection_state(sqlite_db) == before


def test_partner_view_operational_error_fails_typed_and_unavailable(
    sqlite_db: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = _projection_state(sqlite_db)

    def fail_partner_view(*_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
        raise context_module.sqlite3.OperationalError("partner view unavailable")

    monkeypatch.setattr(
        context_module,
        "query_partner_architecture_competency_candidates",
        fail_partner_view,
    )
    monkeypatch.setattr(
        context_module,
        "default_graph_sqlite_path",
        lambda _repo_root: sqlite_db,
    )

    with pytest.raises(C03GraphProjectionUnavailableError, match="partner view unavailable"):
        assemble_c03_graph_sqlite_context(
            role_family_key=ROLE_FAMILY,
            section_id="executive_summary",
            selected_fact_ids=[FACT_ID],
            repo_root=REPO,
            db_path=sqlite_db,
        )

    enriched = context_module.enrich_c03_bound_with_sqlite_context(
        {"section_id": "executive_summary"},
        role_family_key=ROLE_FAMILY,
        selected_fact_ids=[FACT_ID],
        repo_root=REPO,
    )
    assert enriched["c03_sqlite_attach_status"] == "DEGRADED"
    assert enriched["c03_sqlite_context_status"] == "UNAVAILABLE"
    assert "partner view unavailable" in enriched["c03_sqlite_context_error"]
    assert "SQLITE_CONTEXT_AVAILABLE" not in str(enriched)
    assert _projection_state(sqlite_db) == before
