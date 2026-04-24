"""tools.ledgers.apply_schema — Idempotent multi-ledger migrator.

Applies ledger_base.schema.sql followed by each ledger's per-ledger DDL to
every registered ledger DB under artifacts/ledgers/. Safe to run repeatedly.

Usage:
    python tools/ledgers/apply_schema.py            # migrate all ledgers
    python tools/ledgers/apply_schema.py --check    # dry-run, exit 1 on drift
    python tools/ledgers/apply_schema.py --ledger tool_routing
                                                    # migrate a single ledger

Exit codes:
    0 = up-to-date or migration succeeded
    1 = drift detected (--check mode)
    2 = migration failed
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from tools.ledgers.schema_registry import LEDGER_REGISTRY, LedgerSpec, SCHEMAS_DIR, get

BASE_SCHEMA_PATH = SCHEMAS_DIR / "ledger_base.schema.sql"

_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)\s*\((.*?)\)\s*;",
    re.IGNORECASE | re.DOTALL,
)
_LINE_COMMENT_RE = re.compile(r"--[^\n]*")


def _strip_sql_comments(sql: str) -> str:
    return _LINE_COMMENT_RE.sub("", sql)


def _parse_expected_columns(schema_sql: str) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for match in _CREATE_TABLE_RE.finditer(schema_sql):
        table = match.group(1)
        body = match.group(2)
        raw_cols: list[str] = []
        depth = 0
        buf: list[str] = []
        for ch in body:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch == "," and depth == 0:
                piece = "".join(buf).strip()
                if piece:
                    raw_cols.append(piece)
                buf = []
            else:
                buf.append(ch)
        tail = "".join(buf).strip()
        if tail:
            raw_cols.append(tail)
        parsed: list[tuple[str, str]] = []
        for raw in raw_cols:
            upper = raw.upper().lstrip()
            if upper.startswith(("PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK", "CONSTRAINT")):
                continue
            tokens = raw.split(None, 1)
            if not tokens:
                continue
            col_name = tokens[0].strip('"`[]')
            parsed.append((col_name, raw))
        result[table] = parsed
    return result


def _existing_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name=?",
        (table,),
    )
    return cur.fetchone() is not None


def _strip_constraints_for_alter(col_def: str) -> str:
    safe = re.sub(r"\bNOT\s+NULL\b", "", col_def, flags=re.IGNORECASE)
    safe = re.sub(r"\bPRIMARY\s+KEY\b", "", safe, flags=re.IGNORECASE)
    safe = re.sub(r"\bAUTOINCREMENT\b", "", safe, flags=re.IGNORECASE)
    safe = re.sub(r"\bREFERENCES\s+\w+\s*\([^)]*\)(\s+ON\s+DELETE\s+\w+)?", "", safe, flags=re.IGNORECASE)
    return " ".join(safe.split())


def _load_sql(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Schema file missing: {path}")
    return path.read_text(encoding="utf-8")


def _apply_one(spec: LedgerSpec, check_only: bool) -> tuple[int, list[str], list[str]]:
    """Apply base + per-ledger schema to one DB. Returns (exit_code, applied, drift)."""
    base_sql_raw = _load_sql(BASE_SCHEMA_PATH)
    # Per-ledger schema is optional — may be the base-only for W0 bring-up
    per_sql_raw = ""
    if spec.schema_path.exists():
        per_sql_raw = _load_sql(spec.schema_path)

    full_sql = base_sql_raw + "\n" + per_sql_raw
    stripped = _strip_sql_comments(full_sql)
    expected = _parse_expected_columns(stripped)

    spec.db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(str(spec.db_path), timeout=10)
    except sqlite3.Error as exc:
        print(f"[ledger.apply_schema] {spec.name}: cannot open {spec.db_path}: {exc}", file=sys.stderr)
        return 2, [], []

    conn.isolation_level = None
    drift: list[str] = []
    applied: list[str] = []

    try:
        # Phase 1: CREATE TABLE IF NOT EXISTS for every table
        for tbl_match in _CREATE_TABLE_RE.finditer(stripped):
            if not check_only:
                conn.execute(tbl_match.group(0))

        # Phase 2: ALTER TABLE ADD COLUMN for missing columns
        for table, cols in expected.items():
            if table == "events_fts":
                continue  # virtual FTS table; rebuilt via script below
            if not _table_exists(conn, table):
                drift.append(f"{spec.name}: MISSING TABLE {table}")
                continue
            existing = set(_existing_columns(conn, table))
            for col_name, col_def in cols:
                if col_name not in existing:
                    safe_def = _strip_constraints_for_alter(col_def)
                    if check_only:
                        drift.append(f"{spec.name}: MISSING COLUMN {table}.{col_name} :: {safe_def}")
                    else:
                        try:
                            conn.execute(f"ALTER TABLE {table} ADD COLUMN {safe_def}")
                            applied.append(f"{spec.name}:{table}.{col_name}")
                        except sqlite3.Error as exc:
                            print(
                                f"[ledger.apply_schema] {spec.name}: ALTER failed on {table}.{col_name}: {exc}",
                                file=sys.stderr,
                            )
                            return 2, applied, drift

        # Phase 3: full DDL script (indexes, virtual tables, inserts)
        if not check_only:
            conn.executescript(full_sql)
    finally:
        conn.close()

    return (1 if (check_only and drift) else 0), applied, drift


def apply_all(check_only: bool = False, only: str | None = None) -> int:
    specs: tuple[LedgerSpec, ...]
    if only:
        specs = (get(only),)
    else:
        specs = LEDGER_REGISTRY

    total_applied: list[str] = []
    total_drift: list[str] = []
    worst_rc = 0

    for spec in specs:
        rc, applied, drift = _apply_one(spec, check_only)
        total_applied.extend(applied)
        total_drift.extend(drift)
        worst_rc = max(worst_rc, rc)

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if check_only:
        if total_drift:
            print("[ledger.apply_schema] Drift detected:")
            for d in total_drift:
                print(f"  - {d}")
            return 1
        print(f"[ledger.apply_schema] {stamp} All {len(specs)} ledgers up-to-date.")
        return 0

    if total_applied:
        print(
            f"[ledger.apply_schema] {stamp} Applied {len(total_applied)} additions across {len(specs)} ledger(s):"
        )
        for a in total_applied:
            print(f"  + {a}")
    else:
        print(f"[ledger.apply_schema] {stamp} No changes across {len(specs)} ledger(s).")
    return worst_rc


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply ledger schemas idempotently.")
    parser.add_argument("--check", action="store_true", help="Dry-run, exit 1 on drift")
    parser.add_argument("--ledger", default=None, help="Apply only the named ledger")
    args = parser.parse_args()
    return apply_all(check_only=args.check, only=args.ledger)


if __name__ == "__main__":
    sys.exit(main())
