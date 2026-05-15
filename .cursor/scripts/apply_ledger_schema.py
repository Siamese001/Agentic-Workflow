#!/usr/bin/env python3
"""
apply_ledger_schema.py — Idempotent migration for the decision ledger.

Reads canonical DDL from .cursor/schemas/decision_ledger.schema.sql and applies it.
For existing tables, adds any missing columns via ALTER TABLE ADD COLUMN
(SQLite's only supported non-destructive evolution).

Usage:
    python .cursor/scripts/apply_ledger_schema.py           # apply
    python .cursor/scripts/apply_ledger_schema.py --check   # dry-run + diff report
    python .cursor/scripts/apply_ledger_schema.py --force   # recreate FTS index

Exit codes:
    0 = up-to-date or migration succeeded
    1 = drift detected (--check mode)
    2 = migration failed

Constitutional compliance:
    - No PowerShell, no shell=True
    - UTF-8 explicit encoding
    - No bare except; catches sqlite3.Error specifically
    - subprocess unused (pure sqlite3)
"""

import argparse
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".cursor" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
SCHEMA_PATH = REPO_ROOT / ".cursor" / "schemas" / "decision_ledger.schema.sql"


# --------------------------------------------------------------------- #
# Column extraction from canonical DDL                                  #
# --------------------------------------------------------------------- #

_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)\s*\((.*?)\)\s*;",
    re.IGNORECASE | re.DOTALL,
)

_LINE_COMMENT_RE = re.compile(r"--[^\n]*")


def _strip_sql_comments(sql: str) -> str:
    return _LINE_COMMENT_RE.sub("", sql)


def parse_expected_columns(schema_sql: str) -> dict[str, list[tuple[str, str]]]:
    """Extract {table_name: [(col_name, col_def), ...]} from the DDL.

    col_def preserves the raw definition string so ALTER TABLE can replay it.
    """
    result: dict[str, list[tuple[str, str]]] = {}
    for match in _CREATE_TABLE_RE.finditer(schema_sql):
        table = match.group(1)
        body = match.group(2)
        raw_cols: list[str] = []
        # Split on commas that are NOT inside parens (e.g., CHECK(x, y))
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
            # Skip table-level constraints
            upper = raw.upper().lstrip()
            if upper.startswith(("PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK", "CONSTRAINT")):
                continue
            # First token is the column name
            tokens = raw.split(None, 1)
            if not tokens:
                continue
            col_name = tokens[0].strip('"`[]')
            col_def = raw
            parsed.append((col_name, col_def))
        result[table] = parsed
    return result


# --------------------------------------------------------------------- #
# Existing column introspection                                         #
# --------------------------------------------------------------------- #


def get_existing_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') AND name=?",
        (table,),
    )
    return cur.fetchone() is not None


# --------------------------------------------------------------------- #
# Main                                                                  #
# --------------------------------------------------------------------- #


def _strip_constraints_for_alter(col_def: str) -> str:
    """SQLite ALTER TABLE ADD COLUMN forbids NOT NULL without a default,
    forbids PRIMARY KEY, UNIQUE without a default, and forbids REFERENCES
    enforcement. We keep only type + DEFAULT clause."""
    # Drop NOT NULL (ALTER ADD COLUMN with NOT NULL and no default fails)
    safe = re.sub(r"\bNOT\s+NULL\b", "", col_def, flags=re.IGNORECASE)
    # Drop PRIMARY KEY (cannot add primary key via ALTER)
    safe = re.sub(r"\bPRIMARY\s+KEY\b", "", safe, flags=re.IGNORECASE)
    # Drop AUTOINCREMENT
    safe = re.sub(r"\bAUTOINCREMENT\b", "", safe, flags=re.IGNORECASE)
    # Drop inline REFERENCES
    safe = re.sub(r"\bREFERENCES\s+\w+\s*\([^)]*\)", "", safe, flags=re.IGNORECASE)
    return " ".join(safe.split())


def apply(check_only: bool = False) -> int:
    if not SCHEMA_PATH.exists():
        print(f"[apply_ledger_schema] Missing schema file: {SCHEMA_PATH}", file=sys.stderr)
        return 2

    schema_sql_raw = SCHEMA_PATH.read_text(encoding="utf-8")
    schema_sql = _strip_sql_comments(schema_sql_raw)
    expected = parse_expected_columns(schema_sql)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
    except sqlite3.Error as exc:
        print(f"[apply_ledger_schema] Cannot open DB {DB_PATH}: {exc}", file=sys.stderr)
        return 2

    conn.isolation_level = None  # autocommit
    drift: list[str] = []
    applied: list[str] = []

    try:
        # Phase 1: ensure tables exist (CREATE TABLE IF NOT EXISTS only)
        # Extract and run only CREATE TABLE statements first so indexes on new
        # columns don't fail before Phase 2 ALTERs add them.
        create_table_stmts = _CREATE_TABLE_RE.findall(schema_sql)
        for tbl_match in _CREATE_TABLE_RE.finditer(schema_sql):
            if not check_only:
                conn.execute(tbl_match.group(0))

        # Phase 2: compare existing columns vs expected, ALTER as needed
        for table, cols in expected.items():
            if table == "decisions_fts":
                continue  # virtual table; cannot ALTER
            if not table_exists(conn, table):
                drift.append(f"MISSING TABLE: {table}")
                continue
            existing = set(get_existing_columns(conn, table))
            for col_name, col_def in cols:
                if col_name not in existing:
                    safe_def = _strip_constraints_for_alter(col_def)
                    if check_only:
                        drift.append(f"MISSING COLUMN: {table}.{col_name} :: {safe_def}")
                    else:
                        stmt = f"ALTER TABLE {table} ADD COLUMN {safe_def}"
                        try:
                            conn.execute(stmt)
                            applied.append(f"{table}.{col_name}")
                        except sqlite3.Error as exc:
                            print(
                                f"[apply_ledger_schema] ALTER failed on {table}.{col_name}: {exc}",
                                file=sys.stderr,
                            )
                            return 2

        # Phase 3: run full DDL (indexes, virtual tables, inserts) now that
        # every referenced column exists.
        if not check_only:
            conn.executescript(schema_sql)
    finally:
        conn.close()
    _ = create_table_stmts  # silence unused warning (phase 1 uses finditer directly)

    if check_only:
        if drift:
            print("[apply_ledger_schema] Drift detected:")
            for d in drift:
                print(f"  - {d}")
            return 1
        print("[apply_ledger_schema] Schema up-to-date.")
        return 0

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if applied:
        print(f"[apply_ledger_schema] {stamp} Applied {len(applied)} additions:")
        for a in applied:
            print(f"  + {a}")
    else:
        print(f"[apply_ledger_schema] {stamp} No changes — schema up-to-date.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply decision ledger schema (idempotent).")
    parser.add_argument("--check", action="store_true", help="Dry-run: report drift without mutating")
    parser.add_argument("--force", action="store_true", help="(Reserved) full rebuild of FTS index")
    args = parser.parse_args()
    return apply(check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
