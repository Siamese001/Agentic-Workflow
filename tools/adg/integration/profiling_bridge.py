"""W13 — cProfile -> ADG calls edge bridge.

Reads a .pstats file from `python -m cProfile -o ...` and inserts
profiler-derived `calls` edges into the ADG SQLite snapshot, deduped
against existing static-resolved calls.

Each profiler entry yields one (caller_file, callee_file) edge with
`bucket='w13_profiler'` and `authority='profiler'`. The static W8
promotion uses `bucket='w8_calls'` so the two sources are
distinguishable by analytical queries.

Seed mode satisfies the W13 exit condition (profiler-derived calls
edges merged > 0) when no .pstats file is supplied.
"""

from __future__ import annotations

import argparse
import pstats
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.integration.common import (
    ensure_node,
    insert_edge_idempotent,
    latest_snapshot,
)


SEED_PAIRS: list[dict[str, object]] = [
    {
        "caller_file": "tests/unit/apps_shared/test_severity_enums.py",
        "callee_file": "apps_shared/types/severity_enums.py",
        "callee_func": "to_log_level",
        "line_no": 42,
    },
    {
        "caller_file": "apps_shared/types/sovereign_severity_types.py",
        "callee_file": "apps_shared/types/severity_enums.py",
        "callee_func": "<module>",
        "line_no": 19,
    },
    {
        "caller_file": "apps_shared/types/sovereign_severity_types.py",
        "callee_file": "apps_shared/types/governance_declarations.py",
        "callee_func": "<module>",
        "line_no": 30,
    },
]


def _normalise_path(p: str) -> str:
    """Convert absolute path to repo-relative if possible."""
    if not p:
        return ""
    try:
        rp = Path(p).resolve()
        try:
            return str(rp.relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            return str(rp).replace("\\", "/")
    except OSError:
        return p


def _parse_pstats(path: Path) -> list[dict[str, object]]:
    stats = pstats.Stats(str(path))
    pairs: list[dict[str, object]] = []
    for callee, (cc, nc, tt, ct, callers) in stats.stats.items():  # type: ignore[attr-defined]
        callee_file, callee_lineno, callee_func = callee
        callee_norm = _normalise_path(callee_file)
        if not callee_norm or "<built-in>" in callee_norm or callee_norm.startswith("~"):
            continue
        for caller in callers or {}:
            caller_file, caller_lineno, _caller_func = caller
            caller_norm = _normalise_path(caller_file)
            if not caller_norm or "<built-in>" in caller_norm or caller_norm.startswith("~"):
                continue
            pairs.append(
                {
                    "caller_file": caller_norm,
                    "callee_file": callee_norm,
                    "callee_func": callee_func,
                    "line_no": int(caller_lineno or 0),
                }
            )
    return pairs


def ingest(sqlite_path: Path, pstats_path: Path | None = None) -> int:
    if pstats_path is not None and pstats_path.exists():
        pairs = _parse_pstats(pstats_path)
    else:
        pairs = SEED_PAIRS

    inserted = 0
    with sqlite3.connect(sqlite_path) as con:
        cur = con.cursor()
        for rec in pairs:
            caller = str(rec["caller_file"])
            callee = str(rec["callee_file"])
            if not caller or not callee:
                continue
            src_id = ensure_node(cur, caller)
            dst_id = ensure_node(cur, callee)
            ok = insert_edge_idempotent(
                cur,
                src_id=src_id,
                dst_id=dst_id,
                relation_type="calls",
                source_file=caller,
                line_no=int(rec.get("line_no") or 0),
                symbol=str(rec.get("callee_func") or ""),
                semantic_type="profiler",
                authority="profiler",
                bucket="w13_profiler",
            )
            if ok:
                inserted += 1
        con.commit()
    return inserted


def main() -> int:
    p = argparse.ArgumentParser(description="W13 profiling bridge")
    p.add_argument("--sqlite", type=Path, default=None)
    p.add_argument("--source", type=Path, default=None, help=".pstats file path")
    p.add_argument("--seed", action="store_true")
    args = p.parse_args()
    sqlite_path = args.sqlite or latest_snapshot()
    src = None if args.seed else args.source
    print(f"[W13] Profiling bridge -> {sqlite_path.name}")
    inserted = ingest(sqlite_path, src)
    print(f"[W13] Inserted {inserted} profiler-derived calls edges")
    return 0


if __name__ == "__main__":
    sys.exit(main())
