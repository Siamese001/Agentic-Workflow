"""Phase D materialized views for snapshot baselines and exact current-row diffs.

Phase D keeps the aggregate baseline contract while comparing the current rows
to the immediately preceding Phase D materialization.  A prior state is read
from the current database before DROP/CREATE; for a freshly generated database,
the newest prior ``adg_indexed_*.sqlite`` is used.

``is_new`` is deliberately tri-state:

* ``1``: the stable row key is absent from an available prior snapshot;
* ``0``: the stable row key is present in the prior snapshot;
* ``NULL``: no prior snapshot exists, so newness is not knowable.

This prevents first-run inventory from being mislabeled as regression evidence.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from tools.generate.materialized_views.sqlite_helpers import connect_sqlite_for_mv as _connect_sqlite

_BASELINE_COLS: tuple[str, ...] = (
    "snapshot_id",
    "node_count",
    "edge_count",
    "violation_count",
    "cross_layer_edge_count",
    "provider_surface_count",
    "write_bypass_count",
    "debt_score",
)

_PHASE_D_TABLES: tuple[str, ...] = (
    "mv_snapshot_baseline",
    "mv_snapshot_regression_summary",
    "mv_newly_introduced_critical_paths",
    "mv_new_cross_layer_dependencies",
    "mv_new_provider_surfaces",
    "mv_new_write_bypass_paths",
)

_PREVIOUS_STATE_TABLES: tuple[str, ...] = (
    "_phase_d_prev_critical_paths",
    "_phase_d_prev_cross_layer",
    "_phase_d_prev_provider_surfaces",
    "_phase_d_prev_write_bypass",
    "_phase_d_prev_write_bypass_legacy",
)

_COPY_BATCH_SIZE = 1_000
_CRITICALITY_THRESHOLD = 5.0
_PRIOR_SNAPSHOT_ENV = "ADG_PHASE_D_PRIOR_SNAPSHOT"


def _snapshot_id_expr() -> str:
    return (
        "COALESCE("
        "(SELECT NULLIF(value, '') FROM meta WHERE key='artifact_digest' LIMIT 1), "
        "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1), "
        "'')"
    )


def _baseline_row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    return dict(zip(_BASELINE_COLS, row, strict=True))


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table_name,),
    ).fetchone()
    return row is not None


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    if not _table_exists(conn, table_name):
        return set()
    return {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table_name})")}


def _read_baseline(conn: sqlite3.Connection) -> dict[str, Any]:
    if not _table_exists(conn, "mv_snapshot_baseline"):
        return {}
    row = conn.execute(
        "SELECT snapshot_id, node_count, edge_count, violation_count, "
        "cross_layer_edge_count, provider_surface_count, write_bypass_count, debt_score "
        "FROM mv_snapshot_baseline LIMIT 1"
    ).fetchone()
    if not row or not str(row[0] or "").strip():
        return {}
    return _baseline_row_to_dict(row)


def _prior_snapshot_candidates(current_sqlite: Path) -> list[Path]:
    adg_dir = current_sqlite.parent
    current = current_sqlite.resolve()
    candidates: list[Path] = []

    # A clean worktree has no local prior snapshots. The full-audit wrapper
    # supplies the digest-validated producer handoff snapshot through this
    # environment variable so Phase D can still produce exact temporal diffs.
    external_raw = os.environ.get(_PRIOR_SNAPSHOT_ENV, "").strip()
    if external_raw:
        external = Path(external_raw).expanduser()
        try:
            external = external.resolve(strict=True)
        except OSError:
            external = Path()
        if (
            external.is_file()
            and external.suffix.lower() == ".sqlite"
            and external != current
            and "smoketest" not in external.name
        ):
            candidates.append(external)

    if adg_dir.is_dir():
        local = sorted(
            (
                path
                for path in adg_dir.glob("adg_indexed_*.sqlite")
                if path.resolve() != current and "smoketest" not in path.name
            ),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        candidates.extend(local)

    unique: list[Path] = []
    seen: set[Path] = {current}
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def _open_read_only(sqlite_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{sqlite_path.resolve().as_uri()}?mode=ro", uri=True)


def _create_previous_state_tables(cur: sqlite3.Cursor) -> None:
    for table_name in _PREVIOUS_STATE_TABLES:
        cur.execute(f"DROP TABLE IF EXISTS temp.{table_name}")
    cur.executescript(
        """
        CREATE TEMP TABLE _phase_d_prev_critical_paths (
            adg_name TEXT NOT NULL,
            file TEXT NOT NULL,
            criticality_score REAL NOT NULL,
            PRIMARY KEY (adg_name, file)
        ) WITHOUT ROWID;

        CREATE TEMP TABLE _phase_d_prev_cross_layer (
            src_layer TEXT NOT NULL,
            dst_layer TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            edge_count INTEGER NOT NULL,
            PRIMARY KEY (src_layer, dst_layer, relation_type)
        ) WITHOUT ROWID;

        CREATE TEMP TABLE _phase_d_prev_provider_surfaces (
            caller_file TEXT NOT NULL,
            caller_layer TEXT NOT NULL,
            provider_name TEXT NOT NULL,
            provider_path TEXT NOT NULL,
            invocation_count INTEGER NOT NULL,
            PRIMARY KEY (caller_file, caller_layer, provider_name, provider_path)
        ) WITHOUT ROWID;

        CREATE TEMP TABLE _phase_d_prev_write_bypass (
            writer_file TEXT NOT NULL,
            writer_layer TEXT NOT NULL,
            write_symbol TEXT NOT NULL,
            write_line INTEGER NOT NULL,
            source_file TEXT NOT NULL,
            PRIMARY KEY (writer_file, writer_layer, write_symbol, write_line, source_file)
        ) WITHOUT ROWID;

        CREATE TEMP TABLE _phase_d_prev_write_bypass_legacy (
            writer_file TEXT NOT NULL,
            writer_layer TEXT NOT NULL,
            write_symbol TEXT NOT NULL,
            PRIMARY KEY (writer_file, writer_layer, write_symbol)
        ) WITHOUT ROWID;
        """
    )


def _copy_rows(
    source: sqlite3.Connection,
    target: sqlite3.Connection,
    *,
    select_sql: str,
    insert_sql: str,
) -> bool:
    try:
        source_cur = source.execute(select_sql)
    except sqlite3.OperationalError:
        return False

    while True:
        rows = source_cur.fetchmany(_COPY_BATCH_SIZE)
        if not rows:
            break
        target.executemany(insert_sql, rows)
    return True


def _copy_previous_detail_state(
    source: sqlite3.Connection,
    target: sqlite3.Connection,
    *,
    source_is_current_database: bool,
) -> None:
    _copy_rows(
        source,
        target,
        select_sql=(
            "SELECT adg_name, COALESCE(file, ''), MAX(criticality_score) "
            "FROM mv_newly_introduced_critical_paths "
            "GROUP BY adg_name, COALESCE(file, '')"
        ),
        insert_sql=(
            "INSERT OR REPLACE INTO _phase_d_prev_critical_paths"
            "(adg_name, file, criticality_score) VALUES (?, ?, ?)"
        ),
    )
    _copy_rows(
        source,
        target,
        select_sql=(
            "SELECT COALESCE(src_layer, ''), COALESCE(dst_layer, ''), relation_type, MAX(edge_count) "
            "FROM mv_new_cross_layer_dependencies "
            "GROUP BY COALESCE(src_layer, ''), COALESCE(dst_layer, ''), relation_type"
        ),
        insert_sql=(
            "INSERT OR REPLACE INTO _phase_d_prev_cross_layer"
            "(src_layer, dst_layer, relation_type, edge_count) VALUES (?, ?, ?, ?)"
        ),
    )
    _copy_rows(
        source,
        target,
        select_sql=(
            "SELECT COALESCE(caller_file, ''), COALESCE(caller_layer, ''), "
            "COALESCE(provider_name, ''), COALESCE(provider_path, ''), MAX(invocation_count) "
            "FROM mv_new_provider_surfaces "
            "GROUP BY COALESCE(caller_file, ''), COALESCE(caller_layer, ''), "
            "COALESCE(provider_name, ''), COALESCE(provider_path, '')"
        ),
        insert_sql=(
            "INSERT OR REPLACE INTO _phase_d_prev_provider_surfaces"
            "(caller_file, caller_layer, provider_name, provider_path, invocation_count) "
            "VALUES (?, ?, ?, ?, ?)"
        ),
    )

    phase_d_columns = _table_columns(source, "mv_new_write_bypass_paths")
    exact_columns = {"writer_file", "writer_layer", "write_symbol", "write_line", "source_file"}
    if exact_columns.issubset(phase_d_columns):
        _copy_rows(
            source,
            target,
            select_sql=(
                "SELECT DISTINCT COALESCE(writer_file, ''), COALESCE(writer_layer, ''), "
                "COALESCE(write_symbol, ''), COALESCE(write_line, 0), COALESCE(source_file, '') "
                "FROM mv_new_write_bypass_paths"
            ),
            insert_sql=(
                "INSERT OR REPLACE INTO _phase_d_prev_write_bypass"
                "(writer_file, writer_layer, write_symbol, write_line, source_file) "
                "VALUES (?, ?, ?, ?, ?)"
            ),
        )
        return

    # A fresh database can recover exact prior path locations from the prior
    # snapshot's Phase A source table.  On an in-place refresh Phase A has
    # already been rebuilt for the current snapshot, so it must not be used.
    if not source_is_current_database and _table_exists(source, "mv_write_sovereignty_paths"):
        _copy_rows(
            source,
            target,
            select_sql=(
                "SELECT DISTINCT COALESCE(writer_file, ''), COALESCE(writer_layer, ''), "
                "COALESCE(write_symbol, ''), COALESCE(write_line, 0), COALESCE(source_file, '') "
                "FROM mv_write_sovereignty_paths WHERE is_uwg_routed = 0"
            ),
            insert_sql=(
                "INSERT OR REPLACE INTO _phase_d_prev_write_bypass"
                "(writer_file, writer_layer, write_symbol, write_line, source_file) "
                "VALUES (?, ?, ?, ?, ?)"
            ),
        )
        return

    # Compatibility for one upgrade cycle from the legacy Phase D schema,
    # which omitted source location.  The comparison remains conservative and
    # is explicitly labeled LEGACY_COARSE in the output.
    if {"writer_file", "writer_layer", "write_symbol"}.issubset(phase_d_columns):
        _copy_rows(
            source,
            target,
            select_sql=(
                "SELECT DISTINCT COALESCE(writer_file, ''), COALESCE(writer_layer, ''), "
                "COALESCE(write_symbol, '') FROM mv_new_write_bypass_paths"
            ),
            insert_sql=(
                "INSERT OR REPLACE INTO _phase_d_prev_write_bypass_legacy"
                "(writer_file, writer_layer, write_symbol) VALUES (?, ?, ?)"
            ),
        )


def _load_previous_state(
    current_sqlite: Path,
    conn: sqlite3.Connection,
) -> dict[str, Any]:
    _create_previous_state_tables(conn.cursor())

    current_baseline = _read_baseline(conn)
    if current_baseline:
        _copy_previous_detail_state(
            conn,
            conn,
            source_is_current_database=True,
        )
        return current_baseline

    for prior_path in _prior_snapshot_candidates(current_sqlite):
        try:
            with _open_read_only(prior_path) as prior_conn:
                baseline = _read_baseline(prior_conn)
                if not baseline:
                    continue
                _copy_previous_detail_state(
                    prior_conn,
                    conn,
                    source_is_current_database=False,
                )
                return baseline
        except (OSError, sqlite3.DatabaseError):
            continue
    return {}


def _drop_previous_state_tables(cur: sqlite3.Cursor) -> None:
    for table_name in _PREVIOUS_STATE_TABLES:
        cur.execute(f"DROP TABLE IF EXISTS temp.{table_name}")


def materialize_phase_d(
    sqlite_path: Path,
    *,
    conn: sqlite3.Connection | None = None,
) -> dict[str, int]:
    """Create Phase D tables using exact stable-key membership comparisons."""
    owns_conn = conn is None
    if conn is None:
        conn = _connect_sqlite(sqlite_path)
    cur = conn.cursor()

    previous = _load_previous_state(sqlite_path, conn)
    for table_name in reversed(_PHASE_D_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")

    current_snapshot_row = cur.execute(
        "SELECT COALESCE("
        "(SELECT NULLIF(value, '') FROM meta WHERE key='artifact_digest' LIMIT 1), "
        "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1), "
        "'')"
    ).fetchone()
    current_snapshot_id = str(current_snapshot_row[0] if current_snapshot_row else "")

    cross_layer_count = int(
        cur.execute(
            """
            SELECT COUNT(*) FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE src.layer != dst.layer
              AND e.relation_type IN ('imports', 'calls')
              AND COALESCE(src.layer, '') != ''
              AND COALESCE(dst.layer, '') != ''
            """
        ).fetchone()[0]
    )
    provider_count = int(
        cur.execute(
            "SELECT COUNT(DISTINCT e.id) FROM edges e WHERE e.relation_type='invokes_provider'"
        ).fetchone()[0]
    )
    try:
        bypass_count = int(
            cur.execute(
                "SELECT COUNT(*) FROM mv_write_sovereignty_paths WHERE is_uwg_routed=0"
            ).fetchone()[0]
        )
    except sqlite3.OperationalError:
        bypass_count = 0
    try:
        debt_row = cur.execute(
            "SELECT COALESCE(SUM(total_debt_score), 0) FROM mv_debt_concentration_hotspots"
        ).fetchone()
        debt_score = float(debt_row[0] if debt_row else 0.0)
    except sqlite3.OperationalError:
        debt_score = float(cur.execute("SELECT COUNT(*) FROM violations").fetchone()[0])

    node_count = int(cur.execute("SELECT COUNT(*) FROM nodes").fetchone()[0])
    edge_count = int(cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0])
    violation_count = int(cur.execute("SELECT COUNT(*) FROM violations").fetchone()[0])

    cur.execute(
        """
        CREATE TABLE mv_snapshot_baseline (
            snapshot_id TEXT NOT NULL,
            node_count INTEGER NOT NULL,
            edge_count INTEGER NOT NULL,
            violation_count INTEGER NOT NULL,
            cross_layer_edge_count INTEGER NOT NULL,
            provider_surface_count INTEGER NOT NULL,
            write_bypass_count INTEGER NOT NULL,
            debt_score REAL NOT NULL
        )
        """
    )
    cur.execute(
        "INSERT INTO mv_snapshot_baseline VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            current_snapshot_id,
            node_count,
            edge_count,
            violation_count,
            cross_layer_count,
            provider_count,
            bypass_count,
            debt_score,
        ),
    )
    cur.execute("CREATE INDEX idx_mv_baseline_snap ON mv_snapshot_baseline(snapshot_id)")

    def _previous_int(key: str, default: int) -> int:
        value = previous.get(key)
        return int(value) if value is not None else default

    def _previous_float(key: str, default: float) -> float:
        value = previous.get(key)
        return float(value) if value is not None else default

    previous_snapshot_id = str(previous.get("snapshot_id") or "")
    has_prior_snapshot = bool(previous_snapshot_id)
    previous_nodes = _previous_int("node_count", node_count)
    previous_edges = _previous_int("edge_count", edge_count)
    previous_violations = _previous_int("violation_count", violation_count)
    previous_cross_layer = _previous_int("cross_layer_edge_count", cross_layer_count)
    previous_providers = _previous_int("provider_surface_count", provider_count)
    previous_bypass = _previous_int("write_bypass_count", bypass_count)
    previous_debt = _previous_float("debt_score", debt_score)

    cur.execute(
        """
        CREATE TABLE mv_snapshot_regression_summary (
            snapshot_id TEXT NOT NULL,
            prev_snapshot_id TEXT NOT NULL,
            node_count INTEGER NOT NULL,
            prev_node_count INTEGER NOT NULL,
            node_delta INTEGER NOT NULL,
            edge_count INTEGER NOT NULL,
            prev_edge_count INTEGER NOT NULL,
            edge_delta INTEGER NOT NULL,
            violation_count INTEGER NOT NULL,
            prev_violation_count INTEGER NOT NULL,
            violation_delta INTEGER NOT NULL,
            cross_layer_edge_count INTEGER NOT NULL,
            prev_cross_layer_edge_count INTEGER NOT NULL,
            cross_layer_delta INTEGER NOT NULL,
            provider_surface_count INTEGER NOT NULL,
            prev_provider_surface_count INTEGER NOT NULL,
            provider_delta INTEGER NOT NULL,
            write_bypass_count INTEGER NOT NULL,
            prev_write_bypass_count INTEGER NOT NULL,
            bypass_delta INTEGER NOT NULL,
            debt_score REAL NOT NULL,
            prev_debt_score REAL NOT NULL,
            debt_delta REAL NOT NULL,
            is_first_run INTEGER NOT NULL CHECK (is_first_run IN (0, 1)),
            comparison_status TEXT NOT NULL
                CHECK (comparison_status IN ('EXACT', 'NO_BASELINE'))
        )
        """
    )
    cur.execute(
        "INSERT INTO mv_snapshot_regression_summary VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            current_snapshot_id,
            previous_snapshot_id,
            node_count,
            previous_nodes,
            node_count - previous_nodes,
            edge_count,
            previous_edges,
            edge_count - previous_edges,
            violation_count,
            previous_violations,
            violation_count - previous_violations,
            cross_layer_count,
            previous_cross_layer,
            cross_layer_count - previous_cross_layer,
            provider_count,
            previous_providers,
            provider_count - previous_providers,
            bypass_count,
            previous_bypass,
            bypass_count - previous_bypass,
            round(debt_score, 2),
            round(previous_debt, 2),
            round(debt_score - previous_debt, 2),
            0 if has_prior_snapshot else 1,
            "EXACT" if has_prior_snapshot else "NO_BASELINE",
        ),
    )
    cur.execute("CREATE INDEX idx_mv_reg_summary ON mv_snapshot_regression_summary(snapshot_id)")

    cur.execute(
        f"""
        CREATE TABLE mv_newly_introduced_critical_paths AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            cr.node_id,
            cr.adg_name,
            cr.layer,
            cr.resolved_path AS file,
            cr.criticality_score,
            prev.criticality_score AS prev_score,
            ROUND(cr.criticality_score - COALESCE(prev.criticality_score, 0), 2) AS delta,
            CASE
                WHEN ? = 0 THEN NULL
                WHEN prev.adg_name IS NULL THEN 1
                ELSE 0
            END AS is_new,
            CASE WHEN ? = 0 THEN 'NO_BASELINE' ELSE 'EXACT' END AS comparison_status
        FROM mv_path_criticality_rollup cr
        LEFT JOIN _phase_d_prev_critical_paths prev
          ON prev.adg_name = cr.adg_name
         AND prev.file = COALESCE(cr.resolved_path, '')
        WHERE cr.criticality_score > ?
        ORDER BY is_new DESC, cr.criticality_score DESC, cr.adg_name
        """,
        (int(has_prior_snapshot), int(has_prior_snapshot), _CRITICALITY_THRESHOLD),
    )
    cur.execute(
        "CREATE INDEX idx_mv_new_crit ON "
        "mv_newly_introduced_critical_paths(is_new, criticality_score DESC)"
    )

    cur.execute(
        f"""
        CREATE TABLE mv_new_cross_layer_dependencies AS
        WITH current_dependencies AS (
            SELECT
                COALESCE(src.layer, '') AS src_layer,
                COALESCE(dst.layer, '') AS dst_layer,
                e.relation_type AS relation_type,
                COUNT(DISTINCT e.id) AS edge_count
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE src.layer != dst.layer
              AND e.relation_type IN ('imports', 'calls', 'violates')
              AND COALESCE(src.layer, '') != ''
              AND COALESCE(dst.layer, '') != ''
              AND src.resolved_path NOT LIKE 'tests/%'
            GROUP BY src.layer, dst.layer, e.relation_type
        )
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            current.src_layer,
            current.dst_layer,
            current.relation_type,
            current.edge_count,
            ? AS prev_total_edges,
            prev.edge_count AS prev_edge_count,
            current.edge_count - COALESCE(prev.edge_count, 0) AS edge_delta,
            CASE
                WHEN ? = 0 THEN NULL
                WHEN prev.src_layer IS NULL THEN 1
                ELSE 0
            END AS is_new,
            CASE WHEN ? = 0 THEN 'NO_BASELINE' ELSE 'EXACT' END AS comparison_status
        FROM current_dependencies current
        LEFT JOIN _phase_d_prev_cross_layer prev
          ON prev.src_layer = current.src_layer
         AND prev.dst_layer = current.dst_layer
         AND prev.relation_type = current.relation_type
        ORDER BY is_new DESC, current.edge_count DESC,
                 current.src_layer, current.dst_layer, current.relation_type
        """,
        (previous_edges, int(has_prior_snapshot), int(has_prior_snapshot)),
    )
    cur.execute(
        "CREATE INDEX idx_mv_new_cross ON "
        "mv_new_cross_layer_dependencies(is_new, src_layer, dst_layer, relation_type)"
    )

    cur.execute(
        f"""
        CREATE TABLE mv_new_provider_surfaces AS
        WITH current_surfaces AS (
            SELECT
                COALESCE(src.resolved_path, '') AS caller_file,
                COALESCE(src.layer, '') AS caller_layer,
                COALESCE(dst.adg_name, '') AS provider_name,
                COALESCE(dst.resolved_path, '') AS provider_path,
                COUNT(DISTINCT e.id) AS invocation_count
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            JOIN nodes dst ON dst.id = e.dst_id
            WHERE e.relation_type = 'invokes_provider'
              AND src.resolved_path NOT LIKE 'tests/%'
              AND src.resolved_path NOT LIKE 'tools/%'
            GROUP BY src.resolved_path, src.layer, dst.adg_name, dst.resolved_path
        )
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            current.caller_file,
            current.caller_layer,
            current.provider_name,
            current.provider_path,
            current.invocation_count,
            prev.invocation_count AS prev_invocation_count,
            current.invocation_count - COALESCE(prev.invocation_count, 0) AS invocation_delta,
            CASE
                WHEN ? = 0 THEN NULL
                WHEN prev.caller_file IS NULL THEN 1
                ELSE 0
            END AS is_new,
            CASE WHEN ? = 0 THEN 'NO_BASELINE' ELSE 'EXACT' END AS comparison_status
        FROM current_surfaces current
        LEFT JOIN _phase_d_prev_provider_surfaces prev
          ON prev.caller_file = current.caller_file
         AND prev.caller_layer = current.caller_layer
         AND prev.provider_name = current.provider_name
         AND prev.provider_path = current.provider_path
        ORDER BY is_new DESC, current.invocation_count DESC,
                 current.caller_file, current.provider_name
        """,
        (int(has_prior_snapshot), int(has_prior_snapshot)),
    )
    cur.execute(
        "CREATE INDEX idx_mv_new_providers ON "
        "mv_new_provider_surfaces(is_new, caller_layer, caller_file)"
    )

    cur.execute("DROP TABLE IF EXISTS temp._phase_d_current_write_bypass")
    try:
        cur.execute(
            """
            CREATE TEMP TABLE _phase_d_current_write_bypass AS
            SELECT
                ws.edge_id,
                COALESCE(ws.writer_file, '') AS writer_file,
                COALESCE(ws.writer_layer, '') AS writer_layer,
                COALESCE(ws.write_symbol, '') AS write_symbol,
                COALESCE(ws.write_line, 0) AS write_line,
                COALESCE(ws.source_file, '') AS source_file,
                ws.severity,
                ws.is_uwg_routed,
                ws.is_direct_infra_write
            FROM mv_write_sovereignty_paths ws
            WHERE ws.is_uwg_routed = 0
            """
        )
    except sqlite3.OperationalError:
        cur.execute(
            """
            CREATE TEMP TABLE _phase_d_current_write_bypass AS
            SELECT
                e.id AS edge_id,
                COALESCE(e.source_file, '') AS writer_file,
                COALESCE(src.layer, '') AS writer_layer,
                COALESCE(e.symbol, '') AS write_symbol,
                COALESCE(e.line_no, 0) AS write_line,
                COALESCE(e.source_file, '') AS source_file,
                'unknown' AS severity,
                0 AS is_uwg_routed,
                0 AS is_direct_infra_write
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            WHERE e.relation_type IN ('writes_to', 'writes_through')
              AND e.source_file NOT LIKE 'tests/%'
              AND e.source_file NOT LIKE 'tools/%'
            """
        )

    cur.execute(
        f"""
        CREATE TABLE mv_new_write_bypass_paths AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            current.edge_id,
            current.writer_file,
            current.writer_layer,
            current.write_symbol,
            current.write_line,
            current.source_file,
            current.severity,
            current.is_uwg_routed,
            current.is_direct_infra_write,
            current.writer_file AS src_file,
            current.writer_layer AS src_layer,
            current.write_symbol AS bypass_type,
            current.write_line AS line_no,
            CASE
                WHEN ? = 0 THEN NULL
                WHEN exact.writer_file IS NULL AND legacy.writer_file IS NULL THEN 1
                ELSE 0
            END AS is_new,
            CASE
                WHEN ? = 0 THEN 'NO_BASELINE'
                WHEN exact.writer_file IS NOT NULL THEN 'EXACT'
                WHEN legacy.writer_file IS NOT NULL THEN 'LEGACY_COARSE'
                ELSE 'EXACT'
            END AS comparison_status
        FROM _phase_d_current_write_bypass current
        LEFT JOIN _phase_d_prev_write_bypass exact
          ON exact.writer_file = current.writer_file
         AND exact.writer_layer = current.writer_layer
         AND exact.write_symbol = current.write_symbol
         AND exact.write_line = current.write_line
         AND exact.source_file = current.source_file
        LEFT JOIN _phase_d_prev_write_bypass_legacy legacy
          ON legacy.writer_file = current.writer_file
         AND legacy.writer_layer = current.writer_layer
         AND legacy.write_symbol = current.write_symbol
        ORDER BY is_new DESC, current.severity, current.writer_file,
                 current.write_line, current.write_symbol
        """,
        (int(has_prior_snapshot), int(has_prior_snapshot)),
    )
    cur.execute("DROP TABLE temp._phase_d_current_write_bypass")
    cur.execute(
        "CREATE INDEX idx_mv_new_bypass ON "
        "mv_new_write_bypass_paths(is_new, severity, writer_file, write_line)"
    )

    _drop_previous_state_tables(cur)
    conn.commit()

    counts: dict[str, int] = {}
    try:
        for table_name in _PHASE_D_TABLES:
            row = cur.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            counts[table_name] = int(row[0] if row else 0)
    finally:
        if owns_conn:
            conn.close()
    return counts
