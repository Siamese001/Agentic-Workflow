"""ADG bypass queries for apps_* proof harness.

Each query returns rows scoped to a single ``app_id`` from a known materialized
view or P-view. Column names below are pinned to the
``adg_indexed_04252026_0843.sqlite`` schema and validated by W0 discovery.

Filter predicates intentionally narrow each MV to ITS canonical "unresolved
bypass" condition, so the totals reported by the harness match the prompt's
intent (zero unresolved bypasses required for PASS).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class BypassQuery:
    """One ADG bypass-class query, scoped to a single app_id at run time."""

    name: str
    view: str
    file_col: str  # column name to LIKE-match against ``f"{app_id}/%"``
    predicate: str  # additional WHERE clause for "unresolved" definition
    select_cols: tuple[str, ...]  # columns to surface in the JSON export
    severity: str = "P0"  # P0 / P1 / P2

    def fetch(
        self, cur: sqlite3.Cursor, app_id: str, *, limit: int = 1000
    ) -> tuple[int, list[dict[str, object]]]:
        """Return ``(unresolved_count, sample_rows[:limit])`` for ``app_id``.

        ``sample_rows`` is a list of dicts keyed by ``select_cols`` for export.
        """
        cols_csv = ", ".join(self.select_cols)
        sql = (
            f"SELECT {cols_csv} FROM {self.view} WHERE {self.file_col} LIKE ? AND ({self.predicate}) LIMIT ?"
        )
        rows = cur.execute(sql, (f"{app_id}/%", limit)).fetchall()
        sample = [dict(zip(self.select_cols, r)) for r in rows]
        # Total count (uncapped)
        sql_count = f"SELECT COUNT(*) FROM {self.view} WHERE {self.file_col} LIKE ? AND ({self.predicate})"
        total = cur.execute(sql_count, (f"{app_id}/%",)).fetchone()[0]
        return int(total), sample


# All 12 queries required by the prompt §5 + the v_p0_write_bypass_uwg cross-check.
QUERIES: tuple[BypassQuery, ...] = (
    BypassQuery(
        name="trace_replay_eval_gaps",
        view="mv_trace_replay_eval_gaps",
        file_col="file",
        predicate="gap_type IS NOT NULL",
        select_cols=("node_id", "file", "layer", "has_trace", "has_replay_link", "has_eval", "gap_type"),
        severity="P1",  # Coverage gap, not a P0 bypass
    ),
    BypassQuery(
        name="replay_surface_gaps",
        view="mv_replay_surface_gaps",
        file_col="file",
        predicate="gap_flag = 1",
        select_cols=("node_id", "file", "layer", "mutation_count", "replay_link_count", "gap_flag"),
        severity="P1",
    ),
    BypassQuery(
        name="task_contract_gaps",
        view="mv_task_contract_gaps",
        file_col="file",
        predicate="gap_flag = 1",
        select_cols=(
            "node_id",
            "file",
            "layer",
            "action_edge_count",
            "schema_or_policy_count",
            "contract_impl_count",
            "gap_flag",
        ),
        severity="P0",
    ),
    BypassQuery(
        name="write_sovereignty_paths",
        view="mv_write_sovereignty_paths",
        file_col="writer_file",
        predicate="is_direct_infra_write = 1 AND COALESCE(is_uwg_routed, 0) = 0",
        select_cols=(
            "edge_id",
            "writer_file",
            "writer_layer",
            "write_symbol",
            "write_line",
            "is_uwg_routed",
            "is_direct_infra_write",
            "severity",
        ),
        severity="P0",
    ),
    BypassQuery(
        name="apps_direct_infra",
        view="v_p0_apps_direct_infra",
        file_col="consumer_file",
        predicate="1=1",
        select_cols=(
            "violation_edge_id",
            "consumer_id",
            "consumer_file",
            "consumer_layer",
            "import_symbol",
            "import_line",
            "violation_type",
        ),
        severity="P0",
    ),
    BypassQuery(
        name="gateway_bypass_paths",
        view="mv_gateway_bypass_paths",
        file_col="src_file",
        predicate="1=1",
        select_cols=(
            "edge_id",
            "src_file",
            "src_layer",
            "provider_symbol",
            "source_file",
            "line_no",
            "bypass_type",
        ),
        severity="P0",
    ),
    BypassQuery(
        name="not_on_spine",
        view="v_p1_not_on_spine",
        file_col="adapter_file",
        predicate="1=1",
        select_cols=(
            "adapter_id",
            "adapter_file",
            "adapter_layer",
            "adapter_name",
            "spine_caller_count",
            "violation_type",
        ),
        severity="P1",
    ),
    BypassQuery(
        name="ad_hoc_imports",
        view="v_p1_ad_hoc_imports",
        file_col="consumer_file",
        predicate="1=1",
        select_cols=(
            "violation_edge_id",
            "consumer_id",
            "consumer_file",
            "consumer_layer",
            "import_symbol",
            "import_line",
            "violation_type",
        ),
        severity="P1",
    ),
    BypassQuery(
        name="capability_and_egress_gaps",
        view="mv_capability_and_egress_gaps",
        file_col="file",
        predicate="gap_type IS NOT NULL",
        select_cols=(
            "node_id",
            "file",
            "layer",
            "provider_invoke_count",
            "capability_route_count",
            "egress_gate_count",
            "gap_type",
        ),
        severity="P0",
    ),
    BypassQuery(
        name="prompt_assembly_wiring_gaps",
        view="mv_prompt_assembly_wiring_gaps",
        file_col="target_file",
        predicate="gap_type IS NOT NULL",
        select_cols=(
            "node_id",
            "target_symbol",
            "target_file",
            "layer",
            "total_callers",
            "live_callers",
            "test_callers",
            "gap_type",
        ),
        severity="P1",
    ),
    BypassQuery(
        name="exit_disposition_coverage",
        view="mv_exit_disposition_coverage",
        file_col="file",
        predicate="is_terminal_covered = 0",
        select_cols=(
            "node_id",
            "file",
            "layer",
            "outgoing_terminal_count",
            "is_terminal_covered",
            "gap_type",
        ),
        severity="P0",
    ),
    BypassQuery(
        name="write_bypass_uwg",
        view="v_p0_write_bypass_uwg",
        file_col="writer_file",
        predicate="1=1",
        select_cols=(
            "violation_edge_id",
            "writer_id",
            "writer_file",
            "writer_layer",
            "write_symbol",
            "write_line",
            "violation_type",
        ),
        severity="P0",
    ),
)


@dataclass
class AppBypassReport:
    """Result of running every BypassQuery for a single ``app_id``."""

    app_id: str
    snapshot_path: str
    per_query: dict[str, dict[str, object]] = field(default_factory=dict)
    p0_unresolved_total: int = 0
    p1_unresolved_total: int = 0
    p2_unresolved_total: int = 0

    def is_p0_clean(self) -> bool:
        return self.p0_unresolved_total == 0


def run_bypass_queries(*, snapshot: Path, app_id: str, sample_limit: int = 200) -> AppBypassReport:
    """Run every :data:`QUERIES` against ``snapshot`` for one ``app_id``."""
    if not snapshot.exists():
        raise FileNotFoundError(f"ADG snapshot missing: {snapshot}")

    report = AppBypassReport(app_id=app_id, snapshot_path=str(snapshot))
    con = sqlite3.connect(snapshot)
    try:
        cur = con.cursor()
        for q in QUERIES:
            try:
                total, sample = q.fetch(cur, app_id, limit=sample_limit)
            except sqlite3.Error as exc:  # noqa: BLE001 -- guardian: query may legitimately fail on schema drift
                report.per_query[q.name] = {
                    "view": q.view,
                    "severity": q.severity,
                    "unresolved": -1,
                    "error": str(exc),
                }
                continue
            report.per_query[q.name] = {
                "view": q.view,
                "severity": q.severity,
                "unresolved": total,
                "sample": sample,
            }
            if q.severity == "P0":
                report.p0_unresolved_total += total
            elif q.severity == "P1":
                report.p1_unresolved_total += total
            else:
                report.p2_unresolved_total += total
    finally:
        con.close()
    return report


__all__ = [
    "BypassQuery",
    "QUERIES",
    "AppBypassReport",
    "run_bypass_queries",
]
