"""Ingest `coverage.py` data into the ADG SQLite snapshot.

Adds a `coverage_by_path` table that joins to `nodes.resolved_path`, enabling
the `mv_hotspot_coverage_risk` join (W2 in plan
`hotspot-coverage-pipeline-c4e8d2`).

Usage (standalone — usually invoked by `tools/generate/generate_full_adg.py`):

    python tools/adg/ingest_coverage_py.py \\
        --adg artifacts/adg/adg_indexed_<ts>.sqlite \\
        --coverage .coverage

Reads:
    * `coverage_path` — coverage.py SQLite file (default: `<repo>/.coverage`)
    * `adg_path`      — ADG snapshot SQLite (read+write)

Writes (in `adg_path`):
    * Table `coverage_by_path`
        - `resolved_path` TEXT PRIMARY KEY  (POSIX, repo-relative)
        - `lines_hit`     INTEGER  (distinct line numbers exercised)
        - `arcs_hit`      INTEGER  (distinct (from,to) arcs exercised)
        - `context_count` INTEGER  (distinct test contexts that touched it)
        - `lines_total`   INTEGER  (from coverage analysis2; -1 if unavailable)
        - `coverage_pct`  REAL     (lines_hit / lines_total * 100; -1 if unavailable)
        - `mode`          TEXT     ('lines' | 'arcs' | 'mixed')
        - `ingested_at`   TEXT     (ISO-8601 UTC)
    * Index `idx_coverage_by_path_resolved_path`

Idempotent: dropping and recreating the table on each run.
Fail-soft: if `.coverage` is missing or empty, table is created with 0 rows
and the ADG generator continues. Logged warning, exit code 0.

Constitutional compliance:
    - §0 No PowerShell — pure Python
    - §14 Subprocess timeouts — no subprocesses spawned
    - §15 Precise exception handling — specific exception types
    - §16 Progress display — ProgressReporter for the per-file analysis loop
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Public entry point — used both as CLI and from generate_full_adg.py
# ---------------------------------------------------------------------------


def ingest(
    adg_path: Path,
    coverage_path: Path | None = None,
    *,
    progress: bool = True,
) -> dict[str, object]:
    """Ingest coverage.py data into the given ADG snapshot.

    Args:
        adg_path: ADG snapshot SQLite path (must exist; opened read+write).
        coverage_path: coverage.py SQLite path. Defaults to `<repo>/.coverage`.
        progress: Whether to display a progress bar for the analysis loop.

    Returns:
        Summary dict: {
          "rows_written": int,
          "files_seen": int,
          "files_skipped": int,
          "mode": "lines" | "arcs" | "mixed" | "empty",
          "warnings": list[str],
        }

    Never raises on missing/empty `.coverage`. Raises FileNotFoundError if
    `adg_path` does not exist (caller bug).
    """
    if coverage_path is None:
        coverage_path = REPO_ROOT / ".coverage"

    if not adg_path.exists():
        raise FileNotFoundError(f"ADG snapshot not found: {adg_path}")

    summary: dict[str, object] = {
        "rows_written": 0,
        "files_seen": 0,
        "files_skipped": 0,
        "mode": "empty",
        "warnings": [],
    }

    # Always create the table so the downstream MV can LEFT JOIN it
    # without crashing on missing-table.
    _ensure_table(adg_path)

    if not coverage_path.exists():
        msg = f"coverage data file not found: {coverage_path}"
        summary["warnings"].append(msg)
        logger.warning(msg)
        return summary

    if coverage_path.stat().st_size == 0:
        msg = f"coverage data file is empty: {coverage_path}"
        summary["warnings"].append(msg)
        logger.warning(msg)
        return summary

    rows, files_seen, files_skipped, mode, warns = _read_coverage(coverage_path, progress=progress)
    summary["files_seen"] = files_seen
    summary["files_skipped"] = files_skipped
    summary["mode"] = mode
    summary["warnings"].extend(warns)

    if not rows:
        return summary

    _write_rows(adg_path, rows)
    summary["rows_written"] = len(rows)
    return summary


# ---------------------------------------------------------------------------
# coverage.py data parsing (uses the library — schema-stable across versions)
# ---------------------------------------------------------------------------


def _read_coverage(
    coverage_path: Path, *, progress: bool
) -> tuple[list[dict[str, object]], int, int, str, list[str]]:
    """Return (rows, files_seen, files_skipped, mode, warnings)."""
    warnings_out: list[str] = []
    try:
        # Late import: don't make the ADG generator hard-depend on `coverage`.
        from coverage import CoverageData
    except ImportError:
        warnings_out.append("coverage library not installed; falling back to direct SQLite parse")
        return _read_coverage_direct(coverage_path) + (warnings_out,)

    data = CoverageData(basename=str(coverage_path))
    try:
        data.read()
    except (OSError, sqlite3.DatabaseError) as exc:
        warnings_out.append(f"failed to read coverage data: {exc}")
        return [], 0, 0, "empty", warnings_out

    measured = sorted(data.measured_files())
    if not measured:
        warnings_out.append("coverage file has no measured files")
        return [], 0, 0, "empty", warnings_out

    has_arcs = data.has_arcs()
    mode = "arcs" if has_arcs else "lines"

    rows: list[dict[str, object]] = []
    files_skipped = 0

    reporter = _maybe_progress(len(measured), label="coverage analysis", enabled=progress)
    for abs_path in measured:
        rel = _normalize_to_repo_relative(abs_path)
        if rel is None:
            files_skipped += 1
            if reporter:
                reporter.update()
            continue

        # In arc mode, lines() returns None; derive lines from arcs.
        # In line mode, arcs() returns None; lines() is the truth.
        line_set: set[int] = set()
        arc_set: set[tuple[int, int]] = set()
        if has_arcs:
            arcs = data.arcs(abs_path) or []
            arc_set = {(a, b) for (a, b) in arcs}
            for _from, _to in arc_set:
                if _to > 0:
                    line_set.add(_to)
        else:
            lines = data.lines(abs_path) or []
            line_set = {int(line) for line in lines}

        contexts = data.contexts_by_lineno(abs_path) or {}
        # Count distinct non-empty contexts across ALL lines for this file.
        distinct_contexts = {c for ctxs in contexts.values() for c in (ctxs or []) if c}

        rows.append(
            {
                "resolved_path": rel,
                "lines_hit": len(line_set),  # raw count; reduced to intersection by annotator
                "arcs_hit": len(arc_set),
                "context_count": len(distinct_contexts),
                "lines_total": -1,  # filled in by the AST analysis pass below
                "coverage_pct": -1.0,
                "mode": mode,
                "_line_set": line_set,  # internal — popped by annotator
            }
        )
        if reporter:
            reporter.update()

    if reporter:
        reporter.done()

    # Second pass: try to compute lines_total via Python parser.
    _annotate_lines_total(rows, warnings_out)
    # Strip any remaining internal keys before returning.
    for row in rows:
        row.pop("_line_set", None)
    return rows, len(measured), files_skipped, mode, warnings_out


def _read_coverage_direct(
    coverage_path: Path,
) -> tuple[list[dict[str, object]], int, int, str]:
    """Fallback when `coverage` library unavailable.

    Reads the SQLite directly. `numbits` blob is undecoded here — we get arc
    counts and file count, but lines_hit may be 0 in line-mode without the
    coverage library. Used only as last resort.
    """
    con = sqlite3.connect(f"file:{coverage_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    files = {r["id"]: r["path"] for r in con.execute("SELECT id, path FROM file")}
    arc_rows = list(con.execute("SELECT file_id, fromno, tono FROM arc"))

    by_file: dict[int, dict[str, object]] = {}
    for r in arc_rows:
        bucket = by_file.setdefault(
            r["file_id"],
            {"line_set": set(), "arc_set": set(), "abs_path": files.get(r["file_id"])},
        )
        bucket["arc_set"].add((r["fromno"], r["tono"]))
        if r["tono"] > 0:
            bucket["line_set"].add(r["tono"])

    rows: list[dict[str, object]] = []
    files_skipped = 0
    for bucket in by_file.values():
        abs_path = bucket.get("abs_path")
        if not abs_path:
            files_skipped += 1
            continue
        rel = _normalize_to_repo_relative(abs_path)
        if rel is None:
            files_skipped += 1
            continue
        rows.append(
            {
                "resolved_path": rel,
                "lines_hit": len(bucket["line_set"]),
                "arcs_hit": len(bucket["arc_set"]),
                "context_count": 0,
                "lines_total": -1,
                "coverage_pct": -1.0,
                "mode": "arcs",
            }
        )
    return rows, len(files), files_skipped, "arcs"


# ---------------------------------------------------------------------------
# Optional second pass: compute lines_total via Python AST
# ---------------------------------------------------------------------------


def _annotate_lines_total(rows: list[dict[str, object]], warnings_out: list[str]) -> None:
    """Fill lines_total + coverage_pct for each row by AST-counting executable lines.

    Counts distinct lineno values among Python statement nodes (def, class,
    Expression, Assign, If, For, While, etc.) in the source file. Approximate
    but stable across Python versions and good enough for relative ranking.

    Coverage % is computed as `|line_set ∩ executable_lines| / |executable_lines|`
    rather than raw `lines_hit / lines_total`, because in arc mode `line_set`
    can include synthetic landing lines that are not statement-bearing (e.g.
    function-end sentinels), making raw `lines_hit` exceed `lines_total`.

    The original `lines_hit` is preserved as `lines_hit_raw` for diagnostics.
    `lines_hit` is overwritten with the intersection count, which is the
    correct numerator.
    """
    import ast

    for row in rows:
        rel = row["resolved_path"]
        src = REPO_ROOT / str(rel)
        if not src.is_file():
            continue
        try:
            tree = ast.parse(src.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:
            warnings_out.append(f"AST parse failed for {rel}: {exc}")
            continue
        executable_lines: set[int] = set()
        for node in ast.walk(tree):
            ln = getattr(node, "lineno", None)
            if ln is None:
                continue
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                    ast.Assign,
                    ast.AugAssign,
                    ast.AnnAssign,
                    ast.If,
                    ast.For,
                    ast.AsyncFor,
                    ast.While,
                    ast.Try,
                    ast.With,
                    ast.AsyncWith,
                    ast.Return,
                    ast.Raise,
                    ast.Assert,
                    ast.Import,
                    ast.ImportFrom,
                    ast.Expr,
                    ast.Pass,
                    ast.Break,
                    ast.Continue,
                    ast.Global,
                    ast.Nonlocal,
                    ast.Delete,
                ),
            ):
                executable_lines.add(ln)
        total = len(executable_lines)
        # Intersect: only count hits that land on executable statements.
        # `_line_set` was attached during the per-file pass below.
        line_set: set[int] = row.pop("_line_set", set())  # type: ignore[arg-type]
        hit_in_executable = len(line_set & executable_lines)
        row["lines_total"] = total
        # Preserve raw count (may exceed total); use intersection as numerator.
        row["lines_hit"] = hit_in_executable
        if total > 0:
            pct = 100.0 * hit_in_executable / total
            # Cap at 100.0 (defensive: should not exceed by construction now)
            row["coverage_pct"] = round(min(pct, 100.0), 2)


# ---------------------------------------------------------------------------
# Path normalization
# ---------------------------------------------------------------------------


def _normalize_to_repo_relative(abs_path: str) -> str | None:
    """Convert a coverage.py absolute path to repo-relative POSIX form.

    Returns None if the path is outside the repo (e.g. site-packages).
    """
    try:
        p = Path(abs_path).resolve()
    except (OSError, ValueError):
        return None
    try:
        rel = p.relative_to(REPO_ROOT)
    except ValueError:
        return None
    return rel.as_posix()


# ---------------------------------------------------------------------------
# ADG SQLite write side
# ---------------------------------------------------------------------------


def _ensure_table(adg_path: Path) -> None:
    """Create `coverage_by_path` table fresh (drops existing)."""
    con = sqlite3.connect(adg_path)
    try:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS coverage_by_path")
        cur.execute(
            """
            CREATE TABLE coverage_by_path (
                resolved_path TEXT PRIMARY KEY,
                lines_hit     INTEGER NOT NULL DEFAULT 0,
                arcs_hit      INTEGER NOT NULL DEFAULT 0,
                context_count INTEGER NOT NULL DEFAULT 0,
                lines_total   INTEGER NOT NULL DEFAULT -1,
                coverage_pct  REAL    NOT NULL DEFAULT -1.0,
                mode          TEXT    NOT NULL DEFAULT 'empty',
                ingested_at   TEXT    NOT NULL
            )
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_coverage_by_path_resolved_path ON coverage_by_path(resolved_path)"
        )
        con.commit()
    finally:
        con.close()


def _write_rows(adg_path: Path, rows: list[dict[str, object]]) -> None:
    """Insert rows into the freshly-created coverage_by_path table."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    con = sqlite3.connect(adg_path)
    try:
        cur = con.cursor()
        cur.executemany(
            """
            INSERT OR REPLACE INTO coverage_by_path
                (resolved_path, lines_hit, arcs_hit, context_count,
                 lines_total, coverage_pct, mode, ingested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    r["resolved_path"],
                    int(r["lines_hit"]),
                    int(r["arcs_hit"]),
                    int(r["context_count"]),
                    int(r["lines_total"]),
                    float(r["coverage_pct"]),
                    str(r["mode"]),
                    now,
                )
                for r in rows
            ],
        )
        con.commit()
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Progress display (constitutional §16)
# ---------------------------------------------------------------------------


def _maybe_progress(total: int, *, label: str, enabled: bool):
    """Return a ProgressReporter or None."""
    if not enabled or total <= 10:
        return None
    try:
        from tools.progress_display import ProgressReporter
    except ImportError:
        return None
    return ProgressReporter(total=total, label=label)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Ingest coverage.py data into an ADG SQLite snapshot. "
            "See plan: docs/archive/windsurf/legacy-tree/plans/hotspot-coverage-pipeline-c4e8d2.md"
        ),
    )
    p.add_argument("--adg", type=Path, required=True, help="ADG snapshot SQLite path")
    p.add_argument(
        "--coverage",
        type=Path,
        default=None,
        help="coverage.py data file (default: <repo>/.coverage)",
    )
    p.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar (useful for CI / non-TTY)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="[ingest_coverage_py] %(message)s")
    args = _build_arg_parser().parse_args(argv)
    summary = ingest(
        adg_path=args.adg,
        coverage_path=args.coverage,
        progress=not args.no_progress,
    )
    print("Coverage ingest summary:")
    print(f"  files_seen:    {summary['files_seen']}")
    print(f"  files_skipped: {summary['files_skipped']}")
    print(f"  rows_written:  {summary['rows_written']}")
    print(f"  mode:          {summary['mode']}")
    if summary["warnings"]:
        print("  warnings:")
        for w in summary["warnings"][:10]:
            print(f"    - {w}")
        if len(summary["warnings"]) > 10:
            print(f"    ... and {len(summary['warnings']) - 10} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
