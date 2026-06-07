"""Profile ADG MV materialization — per-phase + per-statement timing.

W1 of plan adg-mv-materialization-perf-b3d9f1. Standalone diagnostic; NOT in the
hot path of ``generate_full_adg``. Copies the latest ADG snapshot, opens it
exactly as the production orchestrator does (``connect_sqlite_for_mv``: WAL +
synchronous=NORMAL + temp_store=MEMORY), then runs the real phase functions
(A -> B,C -> D -> E -> F) through a timing-proxy connection so every executed
statement is timed in the true dependency chain. Emits a ranked JSON report.

Usage:
    python -m tools.generate.profile_mv_materialization [--snapshot PATH] [--top 15] [--out PATH]
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.generate.materialized_views.sqlite_helpers import connect_sqlite_for_mv  # noqa: E402
from tools.generate.materialized_views.phase_a_path_authority import materialize_phase_a  # noqa: E402
from tools.generate.materialized_views.phase_b_capability_tool_task import materialize_phase_b  # noqa: E402
from tools.generate.materialized_views.phase_c_trace_drift_debt import materialize_phase_c  # noqa: E402
from tools.generate.materialized_views.phase_d_snapshot_regression import materialize_phase_d  # noqa: E402
from tools.generate.materialized_views.phase_e_graph_intelligence import materialize_phase_e  # noqa: E402
from tools.generate.materialized_views.phase_f_hotspot_coverage import materialize_phase_f  # noqa: E402

_PHASES = (
    ("A_path_authority", materialize_phase_a),
    ("B_capability_tool_task", materialize_phase_b),
    ("C_trace_drift_debt", materialize_phase_c),
    ("D_snapshot_regression", materialize_phase_d),
    ("E_graph_intelligence", materialize_phase_e),
    ("F_hotspot_coverage", materialize_phase_f),
)


def _label_for_sql(sql: str) -> str:
    """Extract a compact label (verb + target object) from a SQL statement."""
    s = " ".join(sql.split())
    up = s.upper()
    for verb in ("CREATE TABLE IF NOT EXISTS", "CREATE TABLE", "DROP TABLE IF EXISTS",
                 "DROP TABLE", "CREATE INDEX IF NOT EXISTS", "CREATE INDEX",
                 "CREATE VIEW IF NOT EXISTS", "CREATE VIEW", "INSERT INTO", "UPDATE", "DELETE FROM"):
        if up.startswith(verb):
            rest = s[len(verb):].strip()
            target = rest.split("(")[0].split(" AS ")[0].split(" ON ")[0].strip().split()[0:1]
            return f"{verb} {target[0] if target else '?'}"
    return (s[:48] + "…") if len(s) > 48 else s


class _TimedCursor:
    """Cursor proxy that records (sql_label, elapsed_ms) into a shared sink."""

    def __init__(self, real: sqlite3.Cursor, sink: list) -> None:
        self._real = real
        self._sink = sink

    def execute(self, sql, parameters=()):  # noqa: ANN001
        t0 = time.perf_counter()
        out = self._real.execute(sql, parameters) if parameters else self._real.execute(sql)
        self._sink.append((_label_for_sql(sql), (time.perf_counter() - t0) * 1000.0))
        return out

    def executescript(self, sql):  # noqa: ANN001
        t0 = time.perf_counter()
        out = self._real.executescript(sql)
        self._sink.append((_label_for_sql(sql), (time.perf_counter() - t0) * 1000.0))
        return out

    def __getattr__(self, name):  # noqa: ANN001 — delegate fetchone/fetchall/rowcount/etc.
        return getattr(self._real, name)


class _TimedConnection:
    """Connection proxy that times execute/executescript and hands out timed cursors."""

    def __init__(self, real: sqlite3.Connection, sink: list) -> None:
        self._real = real
        self._sink = sink

    def execute(self, sql, parameters=()):  # noqa: ANN001
        t0 = time.perf_counter()
        out = self._real.execute(sql, parameters) if parameters else self._real.execute(sql)
        self._sink.append((_label_for_sql(sql), (time.perf_counter() - t0) * 1000.0))
        return out

    def executescript(self, sql):  # noqa: ANN001
        t0 = time.perf_counter()
        out = self._real.executescript(sql)
        self._sink.append((_label_for_sql(sql), (time.perf_counter() - t0) * 1000.0))
        return out

    def cursor(self):
        return _TimedCursor(self._real.cursor(), self._sink)

    def __getattr__(self, name):  # noqa: ANN001 — delegate commit/close/row_factory/etc.
        return getattr(self._real, name)


def _has_nodes_table(p: Path) -> bool:
    """True when the sqlite file has a populated-schema ``nodes`` table.

    Mirrors production ``latest_snapshot(require_nodes_table=True)`` — stub /
    sentinel snapshots (e.g. ``adg_indexed_99999999_9999.sqlite``) carry fresh
    mtimes but no ``nodes`` table and must be skipped.
    """
    try:
        c = sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)
        try:
            return c.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='nodes'"
            ).fetchone()[0] > 0
        finally:
            c.close()
    except sqlite3.Error:
        return False


def _resolve_snapshot(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    adg = _ROOT / "artifacts" / "adg"
    cands = sorted(adg.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    for c in cands:
        if _has_nodes_table(c):
            return c
    raise FileNotFoundError(f"No adg_indexed_*.sqlite with a nodes table under {adg}")


def profile(snapshot: Path, top: int) -> dict:
    tmp = Path(tempfile.gettempdir()) / f"mv_profile_{snapshot.stem}.sqlite"
    shutil.copy2(snapshot, tmp)
    for ext in ("-wal", "-shm"):
        sib = Path(str(snapshot) + ext)
        if sib.exists():
            shutil.copy2(sib, Path(str(tmp) + ext))

    statements: list[tuple[str, str, float]] = []  # (phase, label, ms)
    phase_times: list[tuple[str, float, int]] = []  # (phase, ms, table_count)
    real = connect_sqlite_for_mv(tmp)
    try:
        for name, fn in _PHASES:
            sink: list = []
            proxy = _TimedConnection(real, sink)
            t0 = time.perf_counter()
            counts = fn(tmp, conn=proxy)
            dt_ms = (time.perf_counter() - t0) * 1000.0
            phase_times.append((name, dt_ms, len(counts)))
            for label, ms in sink:
                statements.append((name, label, ms))
            print(f"[profile] phase {name}: {dt_ms / 1000.0:7.1f}s  ({len(counts)} tables)")
    finally:
        real.close()
        tmp.unlink(missing_ok=True)
        for ext in ("-wal", "-shm"):
            Path(str(tmp) + ext).unlink(missing_ok=True)

    total_ms = sum(p[1] for p in phase_times)
    top_stmts = sorted(statements, key=lambda r: r[2], reverse=True)[:top]
    report = {
        "snapshot": snapshot.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_seconds": round(total_ms / 1000.0, 1),
        "phases": [
            {"phase": n, "seconds": round(ms / 1000.0, 1), "pct": round(100 * ms / total_ms, 1),
             "tables": tc}
            for n, ms, tc in phase_times
        ],
        "top_statements": [
            {"phase": p, "label": lbl, "seconds": round(ms / 1000.0, 2),
             "pct": round(100 * ms / total_ms, 1)}
            for p, lbl, ms in top_stmts
        ],
    }
    return report


def _hash_mv_tables(con: sqlite3.Connection) -> dict:
    """Content hash (rows + sha256 over canonically-ordered rows) of every mv_* table."""
    import hashlib
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'mv_%' ORDER BY name"
    ).fetchall()]
    out: dict = {}
    for t in tables:
        cols = [r[1] for r in con.execute(f"PRAGMA table_info('{t}')").fetchall()]
        order = ", ".join(f'"{c}"' for c in cols) if cols else "1"
        h = hashlib.sha256()
        n = 0
        for row in con.execute(f'SELECT * FROM "{t}" ORDER BY {order}'):
            h.update(repr(row).encode("utf-8"))
            h.update(b"\x00")
            n += 1
        out[t] = {"rows": n, "sha256": h.hexdigest()}
    return out


def run_equivalence(snapshot: Path) -> dict:
    """Full materialize on a snapshot copy, then content-hash every mv_* table."""
    from tools.generate.materialized_views.orchestrator import materialize_all_views
    tmp = Path(tempfile.gettempdir()) / f"mv_equiv_{snapshot.stem}.sqlite"
    shutil.copy2(snapshot, tmp)
    for ext in ("-wal", "-shm"):
        sib = Path(str(snapshot) + ext)
        if sib.exists():
            shutil.copy2(sib, Path(str(tmp) + ext))
    t0 = time.perf_counter()
    materialize_all_views(tmp)
    elapsed = time.perf_counter() - t0
    con = sqlite3.connect(f"file:{tmp.as_posix()}?mode=ro", uri=True)
    try:
        hashes = _hash_mv_tables(con)
    finally:
        con.close()
        tmp.unlink(missing_ok=True)
        for ext in ("-wal", "-shm"):
            Path(str(tmp) + ext).unlink(missing_ok=True)
    return {"snapshot": snapshot.name, "elapsed_seconds": round(elapsed, 1),
            "table_count": len(hashes), "tables": hashes}


def _compare(old_path: str, new_path: str) -> int:
    import json
    a = json.loads(Path(old_path).read_text(encoding="utf-8"))
    b = json.loads(Path(new_path).read_text(encoding="utf-8"))
    ta, tb = a["tables"], b["tables"]
    names = sorted(set(ta) | set(tb))
    mism = []
    for nm in names:
        x, y = ta.get(nm), tb.get(nm)
        if x is None or y is None:
            mism.append((nm, "MISSING_IN_OLD" if x is None else "MISSING_IN_NEW"))
        elif x["sha256"] != y["sha256"] or x["rows"] != y["rows"]:
            mism.append((nm, f"DIFF old(rows={x['rows']}) new(rows={y['rows']})"))
    print(f"[equiv] OLD {a.get('elapsed_seconds')}s ({len(ta)} tables) vs "
          f"NEW {b.get('elapsed_seconds')}s ({len(tb)} tables)")
    if not mism:
        print(f"[equiv] EQUIVALENCE_OK: all {len(names)} mv_* tables identical (rows + sha256)")
        return 0
    print(f"[equiv] EQUIVALENCE_MISMATCH: {len(mism)} table(s)")
    for m in mism:
        print("   ", m)
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--snapshot", default=None, help="ADG sqlite (default: latest under artifacts/adg)")
    ap.add_argument("--top", type=int, default=15, help="top-N slowest statements to report")
    ap.add_argument("--out", default=None, help="output JSON path (default: artifacts/adg/mv_phase_profile_<ts>.json)")
    ap.add_argument("--equivalence", action="store_true",
                    help="full materialize on a copy, then content-hash every mv_* table (before/after proof)")
    ap.add_argument("--compare", nargs=2, metavar=("OLD_JSON", "NEW_JSON"),
                    help="compare two --equivalence reports; exit 1 on any mv_* table mismatch")
    args = ap.parse_args(argv)

    if args.compare:
        return _compare(args.compare[0], args.compare[1])

    snap = _resolve_snapshot(args.snapshot)

    if args.equivalence:
        import json
        rep = run_equivalence(snap)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out = Path(args.out) if args.out else (_ROOT / "artifacts" / "adg" / f"mv_equiv_{ts}.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rep, indent=2), encoding="utf-8")
        print(f"[equiv] {rep['snapshot']}  materialize={rep['elapsed_seconds']}s  tables={rep['table_count']}")
        print(f"[equiv] report: {out}")
        return 0

    print(f"[profile] snapshot: {snap.name}")
    report = profile(snap, args.top)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = Path(args.out) if args.out else (_ROOT / "artifacts" / "adg" / f"mv_phase_profile_{ts}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    import json
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\n[profile] TOTAL {report['total_seconds']}s across {len(report['phases'])} phases")
    print("[profile] per-phase:")
    for p in report["phases"]:
        print(f"    {p['phase']:24s} {p['seconds']:7.1f}s  {p['pct']:5.1f}%  ({p['tables']} tables)")
    print(f"[profile] top {args.top} statements:")
    for s in report["top_statements"]:
        print(f"    {s['seconds']:7.2f}s  {s['pct']:5.1f}%  [{s['phase']}] {s['label']}")
    print(f"[profile] report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
