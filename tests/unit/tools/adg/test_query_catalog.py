"""Executable contracts for canonical ADG SQLite query plans."""

from __future__ import annotations

import sqlite3

from agentic_core.adg.artifact.sqlite_schema import DDL
from tools.adg.core.query_catalog import (
    CORE_QUERY_CATALOG,
    QueryContract,
    validate_query_plans,
)


def _canonical_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(DDL)
    return conn


def test_canonical_schema_satisfies_governed_query_plans() -> None:
    with _canonical_connection() as conn:
        assert validate_query_plans(conn) == ()


def test_missing_required_index_fails_closed() -> None:
    with _canonical_connection() as conn:
        conn.execute("DROP INDEX idx_edges_src_rel")
        issues = validate_query_plans(conn)

    assert any(
        issue.query_id == "edge_fanout"
        and issue.code == "MISSING_INDEX"
        and issue.detail == "idx_edges_src_rel"
        for issue in issues
    )


def test_every_governed_query_is_bounded_and_read_only() -> None:
    assert CORE_QUERY_CATALOG
    for contract in CORE_QUERY_CATALOG:
        normalized = " ".join(contract.sql.upper().split())
        assert normalized.startswith(("SELECT ", "WITH "))
        assert " LIMIT " in f" {normalized} "
        assert contract.max_rows > 0
        assert contract.timeout_ms > 0


def test_contract_rejects_unbounded_sql() -> None:
    try:
        QueryContract(
            query_id="unbounded",
            sql="SELECT * FROM nodes",
            sample_params=(),
            required_indexes=(),
            forbid_full_scan_aliases=("nodes",),
            max_rows=100,
        )
    except ValueError as exc:
        assert "LIMIT" in str(exc)
    else:
        raise AssertionError("unbounded governed SQL was accepted")
