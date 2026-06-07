#!/usr/bin/env python3
"""
apply_append_only_triggers.py — W4.1 migration.

Installs BEFORE UPDATE / BEFORE DELETE triggers on the decisions-bearing tables
of the author-gate ledger AND the 10 ledger-family SQLites to enforce
append-only semantics at the DB layer.

Idempotent: triggers are DROPPED and recreated on each run, so schema drift
does not accumulate orphan triggers.

Usage:
    python .claude/governance/scripts/apply_append_only_triggers.py           # apply to all
    python .claude/governance/scripts/apply_append_only_triggers.py --check   # verify without changes
    python .claude/governance/scripts/apply_append_only_triggers.py --db <path>  # single DB

Exit codes:
    0 — success (or --check: all triggers present)
    1 — --check found a missing trigger
    2 — script error

Constitutional: pure stdlib; specific exceptions; UTF-8; bounded.
"""

import argparse
import glob
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_FAMILY_GLOB = str(REPO_ROOT / "artifacts" / "ledgers" / "*.sqlite")
AUTHOR_GATE_DB = REPO_ROOT / ".cursor" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"

# Mapping of DB-kind → list of protected tables. We guard only the canonical
# decision/event tables; sqlite_sequence, schema_version, FTS shadow tables,
# etc. remain mutable by design.
AUTHOR_GATE_TABLES = ("decisions", "decision_outcomes", "decision_scope")
FAMILY_TABLES = ("events",)

# Escape hatch: allow controlled writes by a privileged writer that sets
# `PRAGMA user_version = 99999;` before its mutation and resets after. This
# is not used today but leaves room for future "administrative truncation"
# operations without removing the triggers.
BYPASS_PRAGMA_MARKER = 99999


def _trigger_sql(table: str, op: str) -> tuple[str, str]:
    """Return (drop_sql, create_sql) pair for a BEFORE <op> trigger."""
    trig_name = f"trg_{table}_no_{op.lower()}"
    drop = f"DROP TRIGGER IF EXISTS {trig_name};"
    create = (
        f"CREATE TRIGGER {trig_name} BEFORE {op} ON {table} "
        f"WHEN (SELECT user_version FROM pragma_user_version()) != {BYPASS_PRAGMA_MARKER} "
        f"BEGIN "
        f"SELECT RAISE(ABORT, '{table} is append-only (W4.1)'); "
        f"END;"
    )
    return drop, create


def _apply_to_db(db_path: Path, tables: tuple[str, ...], check_only: bool) -> tuple[bool, list[str]]:
    """Return (ok, messages). ok=False means at least one table missing a trigger in --check."""
    messages: list[str] = []
    if not db_path.exists():
        return True, [f"  SKIP {db_path.name}: not present"]
    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
    except sqlite3.Error as exc:
        return False, [f"  ERR  {db_path.name}: {exc}"]

    all_present = True
    try:
        existing_tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        existing_triggers = {
            r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        }
        for table in tables:
            if table not in existing_tables:
                continue
            for op in ("UPDATE", "DELETE"):
                trig = f"trg_{table}_no_{op.lower()}"
                if check_only:
                    if trig not in existing_triggers:
                        all_present = False
                        messages.append(f"  MISS {db_path.name}: {trig}")
                    else:
                        messages.append(f"  OK   {db_path.name}: {trig}")
                else:
                    drop, create = _trigger_sql(table, op)
                    try:
                        conn.execute(drop)
                        conn.execute(create)
                        messages.append(f"  SET  {db_path.name}: {trig}")
                    except sqlite3.Error as exc:
                        all_present = False
                        messages.append(f"  FAIL {db_path.name}: {trig}: {exc}")
        if not check_only:
            conn.commit()
    finally:
        conn.close()
    return all_present, messages


def main() -> int:
    ap = argparse.ArgumentParser(description="Append-only triggers migration (W4.1)")
    ap.add_argument("--check", action="store_true", help="verify without changes")
    ap.add_argument("--db", type=str, help="single DB path")
    args = ap.parse_args()

    targets: list[tuple[Path, tuple[str, ...]]] = []
    if args.db:
        # Auto-pick table list: author-gate DB vs ledger family
        p = Path(args.db)
        if "refactor_decision_ledger" in p.name:
            targets.append((p, AUTHOR_GATE_TABLES))
        else:
            targets.append((p, FAMILY_TABLES))
    else:
        targets.append((AUTHOR_GATE_DB, AUTHOR_GATE_TABLES))
        for path in sorted(glob.glob(LEDGER_FAMILY_GLOB)):
            targets.append((Path(path), FAMILY_TABLES))

    print(
        f"[apply_append_only_triggers] mode={'check' if args.check else 'apply'} targets={len(targets)}",
        file=sys.stderr,
    )

    all_ok = True
    for db_path, tables in targets:
        ok, msgs = _apply_to_db(db_path, tables, args.check)
        for m in msgs:
            print(m, file=sys.stderr)
        if not ok:
            all_ok = False

    if args.check and not all_ok:
        print("[apply_append_only_triggers] CHECK FAIL — missing triggers above", file=sys.stderr)
        return 1

    print(f"[apply_append_only_triggers] {'CHECK OK' if args.check else 'APPLIED'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[apply_append_only_triggers] script error: {exc}", file=sys.stderr)
        sys.exit(2)
