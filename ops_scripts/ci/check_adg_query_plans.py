#!/usr/bin/env python3
"""Fail closed when governed ADG queries lose required indexes or full-scan."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote

from tools.adg.core.query_catalog import validate_query_plans


def _readonly_uri(path: Path) -> str:
    return f"file:{quote(str(path.resolve()))}?mode=ro"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_adg_query_plans.py PATH_TO_ADG_SQLITE")
        return 2
    sqlite_path = Path(argv[1]).expanduser().resolve()
    if not sqlite_path.is_file():
        print(f"[ERROR] ADG SQLite snapshot not found: {sqlite_path}")
        return 2

    try:
        conn = sqlite3.connect(_readonly_uri(sqlite_path), uri=True)
        try:
            conn.execute("PRAGMA query_only = ON")
            issues = validate_query_plans(conn)
        finally:
            conn.close()
    except sqlite3.Error as exc:
        print(f"[ERROR] unable to inspect ADG SQLite snapshot: {exc}")
        return 2

    if issues:
        for issue in issues:
            print(f"[FAIL] {issue.query_id}: {issue.code}: {issue.detail}")
        return 1
    print(f"[PASS] governed ADG query plans valid: {sqlite_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
