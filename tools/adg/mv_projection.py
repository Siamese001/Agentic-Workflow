"""ADG Materialized-View Projection — Project SQLite mv_* and v_p* into Redis.

SSOT is SQLite. Redis holds a deterministic read-only projection for sub-ms
top-K hotspot, blast-radius, and P-view membership queries.

Key scheme:
    adg:v1:<snapshot_id>:mv:<mv_name>            ZSET   (member=id, score=ranking metric)
    adg:v1:<snapshot_id>:mv:<mv_name>:meta       HSET   (row_count, metric, projected_at)
    adg:v1:<snapshot_id>:pview:<view_name>       SET    (members=identifying ids)
    adg:v1:<snapshot_id>:pview:<view_name>:meta  HSET   (row_count, key_col, projected_at)
    adg:v1:<snapshot_id>:_mv_hot                 STRING 1  (sentinel — MVs fully projected)

Constitutional refs: §22 graph-layer primary; ADG-canonical-invariants §1 SSOT hierarchy.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Iterable

logger = logging.getLogger(__name__)

CACHE_VERSION = "v1"


@dataclass(frozen=True)
class MVProjectionSpec:
    """Spec for projecting one materialized view into a Redis ZSET."""

    table: str
    member_col: str  # column whose value becomes the ZSET member
    score_expr: str  # SQL expression producing the ranking metric
    score_label: str  # human-readable metric name (stored in :meta)


@dataclass(frozen=True)
class PViewProjectionSpec:
    """Spec for projecting one P-view into a Redis SET."""

    view: str
    key_col: str  # column whose values become SET members


# Canonical projection targets — chosen for top-K utility during T2/T3 refactoring.
# See .windsurf/plans/redis-mv-projections-9262a6.md for rationale.
MV_SPECS: tuple[MVProjectionSpec, ...] = (
    MVProjectionSpec(
        table="mv_hotspot_centrality",
        member_col="node_id",
        score_expr="degree_centrality",
        score_label="degree_centrality",
    ),
    MVProjectionSpec(
        table="mv_graph_reverse_dependency_hotspots",
        member_col="node_id",
        score_expr="reverse_dependency_score * layer_criticality_weight",
        score_label="reverse_dependency_score_weighted",
    ),
    MVProjectionSpec(
        table="mv_graph_critical_path_blast_radius",
        member_col="node_id",
        score_expr="weighted_blast_radius",
        score_label="weighted_blast_radius",
    ),
    MVProjectionSpec(
        table="mv_dependency_cone_risk",
        member_col="node_id",
        score_expr="cone_risk_score",
        score_label="cone_risk_score",
    ),
    MVProjectionSpec(
        table="mv_debt_concentration_hotspots",
        member_col="file",
        score_expr="total_debt_score",
        score_label="total_debt_score",
    ),
)

PVIEW_SPECS: tuple[PViewProjectionSpec, ...] = (
    # P0 — node_id keyed (via writer_id / consumer_id)
    PViewProjectionSpec(view="v_p0_write_bypass_uwg", key_col="writer_id"),
    PViewProjectionSpec(view="v_p0_apps_direct_infra", key_col="consumer_id"),
    PViewProjectionSpec(view="v_p0_l0_raw_execution", key_col="consumer_id"),
    PViewProjectionSpec(view="v_p0_l1_direct_infra", key_col="consumer_id"),
    PViewProjectionSpec(view="v_p0_l6_mutation", key_col="writer_id"),
    PViewProjectionSpec(view="v_p0_provider_bypass", key_col="consumer_id"),
    # P1 — adapter-keyed or consumer-keyed
    PViewProjectionSpec(view="v_p1_mis_layered_infra", key_col="adapter_id"),
    PViewProjectionSpec(view="v_p1_zero_caller_infra", key_col="adapter_id"),
    PViewProjectionSpec(view="v_p1_not_on_spine", key_col="adapter_id"),
    PViewProjectionSpec(view="v_p1_ad_hoc_imports", key_col="consumer_id"),
    PViewProjectionSpec(view="v_p1_raw_http_outside_seam", key_col="consumer_id"),
    # P2 — name/id mix (dup adapters keyed by symbol name)
    PViewProjectionSpec(view="v_p2_duplicated_adapters", key_col="infra_name"),
    PViewProjectionSpec(view="v_p2_dormant_ambiguous", key_col="adapter_id"),
    PViewProjectionSpec(view="v_p2_mixed_usage", key_col="infra_name"),
    # P3 — node_id keyed
    PViewProjectionSpec(view="v_p3_isolated_experimental", key_col="node_id"),
)

BATCH_SIZE = 5000


def _redis_key(snapshot_id: str, base: str) -> str:
    return f"adg:{CACHE_VERSION}:{snapshot_id}:{base}"


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name = ? AND type IN ('table','view')",
        (name,),
    ).fetchone()
    return row is not None


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(c[1] == column for c in cols)


def _project_mv(
    conn: sqlite3.Connection,
    client: Any,
    snapshot_id: str,
    spec: MVProjectionSpec,
) -> dict[str, Any]:
    """Project one materialized view into a Redis ZSET with sidecar meta hash."""
    if not _table_exists(conn, spec.table):
        logger.warning("MV skipped (missing table): %s", spec.table)
        return {"table": spec.table, "status": "missing", "rows": 0}
    if not _column_exists(conn, spec.table, spec.member_col):
        logger.warning("MV skipped (missing member col): %s.%s", spec.table, spec.member_col)
        return {"table": spec.table, "status": "bad_schema", "rows": 0}

    zset_key = _redis_key(snapshot_id, f"mv:{spec.table}")
    meta_key = _redis_key(snapshot_id, f"mv:{spec.table}:meta")

    # Drop any stale projection for this snapshot before writing fresh rows.
    client.delete(zset_key)
    client.delete(meta_key)

    sql = (
        f"SELECT {spec.member_col} AS member, "
        f"CAST({spec.score_expr} AS REAL) AS score "
        f"FROM {spec.table} "
        f"WHERE {spec.member_col} IS NOT NULL AND {spec.score_expr} IS NOT NULL"
    )
    cursor = conn.execute(sql)
    row_count = 0
    pipe = client.pipeline(transaction=False)
    mapping: dict[str, float] = {}

    while True:
        batch = cursor.fetchmany(BATCH_SIZE)
        if not batch:
            break
        for member, score in batch:
            if member is None or score is None:
                continue
            mapping[str(member)] = float(score)
            row_count += 1
            if len(mapping) >= BATCH_SIZE:
                pipe.zadd(zset_key, mapping)
                mapping = {}
        if mapping:
            pipe.zadd(zset_key, mapping)
            mapping = {}
        pipe.execute()
        pipe = client.pipeline(transaction=False)

    if mapping:
        pipe.zadd(zset_key, mapping)

    # hmset for Redis 3.x compat (multi-field HSET requires Redis 4+)
    pipe.hmset(
        meta_key,
        {
            "table": spec.table,
            "member_col": spec.member_col,
            "metric": spec.score_label,
            "row_count": str(row_count),
            "projected_at": str(int(time.time())),
        },
    )
    pipe.execute()
    return {"table": spec.table, "status": "ok", "rows": row_count}


def _project_pview(
    conn: sqlite3.Connection,
    client: Any,
    snapshot_id: str,
    spec: PViewProjectionSpec,
) -> dict[str, Any]:
    """Project one P-view into a Redis SET with sidecar meta hash."""
    if not _table_exists(conn, spec.view):
        logger.warning("P-view skipped (missing): %s", spec.view)
        return {"view": spec.view, "status": "missing", "rows": 0}
    if not _column_exists(conn, spec.view, spec.key_col):
        logger.warning("P-view skipped (missing key col): %s.%s", spec.view, spec.key_col)
        return {"view": spec.view, "status": "bad_schema", "rows": 0}

    set_key = _redis_key(snapshot_id, f"pview:{spec.view}")
    meta_key = _redis_key(snapshot_id, f"pview:{spec.view}:meta")

    client.delete(set_key)
    client.delete(meta_key)

    cursor = conn.execute(f"SELECT {spec.key_col} FROM {spec.view} WHERE {spec.key_col} IS NOT NULL")
    members: list[str] = []
    row_count = 0
    pipe = client.pipeline(transaction=False)
    while True:
        batch = cursor.fetchmany(BATCH_SIZE)
        if not batch:
            break
        for (value,) in batch:
            if value is None:
                continue
            members.append(str(value))
            row_count += 1
        if members:
            pipe.sadd(set_key, *members)
            members = []
        pipe.execute()
        pipe = client.pipeline(transaction=False)

    # hmset for Redis 3.x compat (multi-field HSET requires Redis 4+)
    pipe.hmset(
        meta_key,
        {
            "view": spec.view,
            "key_col": spec.key_col,
            "row_count": str(row_count),
            "projected_at": str(int(time.time())),
        },
    )
    pipe.execute()
    return {"view": spec.view, "status": "ok", "rows": row_count}


def project_all(
    conn: sqlite3.Connection,
    client: Any,
    snapshot_id: str,
    mv_specs: Iterable[MVProjectionSpec] = MV_SPECS,
    pview_specs: Iterable[PViewProjectionSpec] = PVIEW_SPECS,
) -> dict[str, Any]:
    """Project all configured MVs and P-views; return summary dict."""
    sentinel_key = _redis_key(snapshot_id, "_mv_hot")
    # Always drop sentinel first so an interrupted run is never misread as hot.
    client.delete(sentinel_key)

    t0 = time.monotonic()
    mv_results = [_project_mv(conn, client, snapshot_id, s) for s in mv_specs]
    pview_results = [_project_pview(conn, client, snapshot_id, s) for s in pview_specs]
    elapsed = time.monotonic() - t0

    total_mv_rows = sum(r["rows"] for r in mv_results)
    total_pview_rows = sum(r["rows"] for r in pview_results)

    # Sentinel only after both blocks complete.
    client.set(sentinel_key, "1")

    return {
        "status": "ok",
        "snapshot_id": snapshot_id,
        "mv_results": mv_results,
        "pview_results": pview_results,
        "mv_total_rows": total_mv_rows,
        "pview_total_rows": total_pview_rows,
        "elapsed_seconds": round(elapsed, 3),
    }


def is_mv_hot(client: Any, snapshot_id: str) -> bool:
    """Return True if MV projection sentinel is set for this snapshot."""
    return bool(client.exists(_redis_key(snapshot_id, "_mv_hot")))
