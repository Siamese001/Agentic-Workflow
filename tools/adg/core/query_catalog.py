"""Governed, bounded SQLite query contracts for canonical ADG reads."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Any


class QueryOutcome(str, Enum):
    """Non-overlapping outcomes for governed ADG reads."""

    OK = "OK"
    EMPTY = "EMPTY"
    UNAVAILABLE = "UNAVAILABLE"
    STALE = "STALE"
    TRUNCATED = "TRUNCATED"


@dataclass(frozen=True)
class QueryContract:
    query_id: str
    sql: str
    sample_params: tuple[Any, ...]
    required_indexes: tuple[str, ...]
    forbid_full_scan_aliases: tuple[str, ...]
    max_rows: int
    timeout_ms: int = 2_000

    def __post_init__(self) -> None:
        normalized = self.sql.lstrip().upper()
        if not normalized.startswith(("SELECT ", "WITH ")):
            raise ValueError(f"{self.query_id}: governed SQL must be read-only")
        if " LIMIT " not in f" {normalized} ":
            raise ValueError(f"{self.query_id}: governed SQL must contain LIMIT")
        if self.max_rows < 1 or self.timeout_ms < 1:
            raise ValueError(f"{self.query_id}: row and time budgets must be positive")


@dataclass(frozen=True)
class QueryPlanIssue:
    query_id: str
    code: str
    detail: str


CORE_QUERY_CATALOG: tuple[QueryContract, ...] = (
    QueryContract(
        query_id="node_by_id",
        sql="SELECT * FROM nodes WHERE id = ? LIMIT 1",
        sample_params=(1,),
        required_indexes=(),
        forbid_full_scan_aliases=("nodes",),
        max_rows=1,
    ),
    QueryContract(
        query_id="nodes_by_layer",
        sql="SELECT * FROM nodes WHERE layer = ? ORDER BY id LIMIT ?",
        sample_params=("L2", 100),
        required_indexes=("idx_nodes_layer",),
        forbid_full_scan_aliases=("nodes",),
        max_rows=1_000,
    ),
    QueryContract(
        query_id="nodes_by_resolved_path",
        sql="SELECT * FROM nodes WHERE resolved_path = ? ORDER BY id LIMIT ?",
        sample_params=("agentic_core/example.py", 100),
        required_indexes=("idx_nodes_resolved_path",),
        forbid_full_scan_aliases=("nodes",),
        max_rows=1_000,
    ),
    QueryContract(
        query_id="node_by_name",
        sql="SELECT * FROM nodes WHERE adg_name = ? ORDER BY id LIMIT ?",
        sample_params=("example", 10),
        required_indexes=("idx_nodes_name",),
        forbid_full_scan_aliases=("nodes",),
        max_rows=1_000,
    ),
    QueryContract(
        query_id="edge_fanout",
        sql=(
            "SELECT id, src_id, dst_id, relation_type, edge_kind, source_file, "
            "line_no, symbol FROM edges WHERE src_id = ? AND relation_type = ? "
            "ORDER BY id LIMIT ?"
        ),
        sample_params=(1, "imports", 30),
        required_indexes=("idx_edges_src_rel",),
        forbid_full_scan_aliases=("edges",),
        max_rows=1_000,
    ),
    QueryContract(
        query_id="edge_fanin",
        sql=(
            "SELECT id, src_id, dst_id, relation_type, edge_kind, source_file, "
            "line_no, symbol FROM edges WHERE dst_id = ? AND relation_type = ? "
            "ORDER BY id LIMIT ?"
        ),
        sample_params=(1, "imports", 30),
        required_indexes=("idx_edges_dst_rel",),
        forbid_full_scan_aliases=("edges",),
        max_rows=1_000,
    ),
    QueryContract(
        query_id="traverse_outbound",
        sql=(
            "SELECT e.id, n.id FROM edges AS e JOIN nodes AS n ON n.id = e.dst_id "
            "WHERE e.src_id = ? AND e.relation_type = ? "
            "AND e.authority_status = ? AND n.entity_type = ? ORDER BY e.id LIMIT ?"
        ),
        sample_params=(1, "imports", "AUTHORITATIVE", "module", 101),
        required_indexes=("idx_edges_src_rel",),
        forbid_full_scan_aliases=("e", "n"),
        max_rows=1_001,
    ),
    QueryContract(
        query_id="traverse_inbound",
        sql=(
            "SELECT e.id, n.id FROM edges AS e JOIN nodes AS n ON n.id = e.src_id "
            "WHERE e.dst_id = ? AND e.relation_type = ? "
            "AND e.authority_status = ? AND n.entity_type = ? ORDER BY e.id LIMIT ?"
        ),
        sample_params=(1, "imports", "AUTHORITATIVE", "module", 101),
        required_indexes=("idx_edges_dst_rel",),
        forbid_full_scan_aliases=("e", "n"),
        max_rows=1_001,
    ),
)


EXPECTED_INDEX_DDL: dict[str, str] = {
    "idx_nodes_layer": "CREATE INDEX IF NOT EXISTS idx_nodes_layer ON nodes(layer)",
    "idx_nodes_name": "CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(adg_name)",
    "idx_nodes_resolved_path": (
        "CREATE INDEX IF NOT EXISTS idx_nodes_resolved_path ON nodes(resolved_path)"
    ),
    "idx_edges_src_rel": (
        "CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, relation_type)"
    ),
    "idx_edges_dst_rel": (
        "CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, relation_type)"
    ),
}


def explain_query_plan(
    conn: sqlite3.Connection,
    contract: QueryContract,
) -> tuple[str, ...]:
    rows = conn.execute(
        f"EXPLAIN QUERY PLAN {contract.sql}",
        contract.sample_params,
    ).fetchall()
    return tuple(str(row[3]) for row in rows)


def _contains_full_scan(detail: str, alias: str) -> bool:
    return bool(
        re.search(
            rf"\bSCAN\s+(?:TABLE\s+)?{re.escape(alias)}(?:\s|$)",
            detail,
            flags=re.IGNORECASE,
        )
    )


def validate_query_plans(
    conn: sqlite3.Connection,
    catalog: tuple[QueryContract, ...] = CORE_QUERY_CATALOG,
) -> tuple[QueryPlanIssue, ...]:
    """Return deterministic contract issues; an empty tuple means PASS."""
    index_rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'index'"
    ).fetchall()
    indexes = {str(row[0]) for row in index_rows}
    issues: list[QueryPlanIssue] = []

    for contract in catalog:
        for index_name in contract.required_indexes:
            if index_name not in indexes:
                issues.append(
                    QueryPlanIssue(
                        contract.query_id,
                        "MISSING_INDEX",
                        index_name,
                    )
                )
        try:
            details = explain_query_plan(conn, contract)
        except sqlite3.Error as exc:
            issues.append(
                QueryPlanIssue(
                    contract.query_id,
                    "EXPLAIN_FAILED",
                    str(exc),
                )
            )
            continue
        for detail in details:
            for alias in contract.forbid_full_scan_aliases:
                if _contains_full_scan(detail, alias):
                    issues.append(
                        QueryPlanIssue(
                            contract.query_id,
                            "FULL_SCAN",
                            detail,
                        )
                    )

    return tuple(issues)
