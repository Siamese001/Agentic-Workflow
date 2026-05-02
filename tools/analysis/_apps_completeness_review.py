"""One-shot ADG analysis: apps_* completeness vs stubs.

Reads the latest ADG SQLite snapshot and produces a report on which apps_*
modules look complete vs which still contain stubs.

Heuristics for "stub":
  - functions whose body is just `pass`, `...`, `return None`, `raise NotImplementedError`
  - `TODO` / `FIXME` / `STUB` markers in node names or near defs
  - very small files (< some line threshold) that export only placeholders
  - files where every function/method is a stub

We rely on the `nodes` table (kind, name, file_path, layer, signature/body if
present) and `edges` (imports, calls, flows_to) to triangulate completeness.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

SNAP = Path("artifacts/adg") / "adg_indexed_05022026_1651.sqlite"


def fetch_schema(con: sqlite3.Connection) -> dict:
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    schema = {}
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        schema[t] = [r[1] for r in cur.fetchall()]
    return schema


def main() -> int:
    if not SNAP.exists():
        print(f"SNAPSHOT MISSING: {SNAP}", file=sys.stderr)
        return 2
    con = sqlite3.connect(str(SNAP))
    schema = fetch_schema(con)
    print("=== TABLES & COLUMNS ===")
    for t, cols in schema.items():
        print(f"  {t}: {cols}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
