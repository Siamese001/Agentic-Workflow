#!/usr/bin/env python3
"""outcome_writer.py — Parse DECISION_OUTCOME markers and write to decision_outcomes.

Plan: `docs/archive/windsurf/legacy-tree/plans/author-gate-hardening-a3b8f2.md` W1.P1.2.

DECISION_OUTCOME marker shape (produced by Cursor Agent at end of an executing turn
or by a Git post-commit trailer parser):

    DECISION_OUTCOME: decision_id=dec_xxx, execution_completed=1, tests_passed=1,
                      regression_found=0, rollback_required=0, promote_to_pattern=0
                      [, followup_decision_id=dec_yyy][, time_to_outcome_s=N]
                      [, notes=<free text, truncated to 300 chars>]

Idempotency: keyed on decision_id. If an outcome row already exists for that
decision, UPDATE the row (additive updates — never clobber non-null to null).

Fail policy: OPEN — exits 0 on success; exits 0 with WARN on unparseable marker;
non-zero only on filesystem / DB permission errors.

Usage:
    python tools/capture/outcome_writer.py --marker "DECISION_OUTCOME: decision_id=..."
    python tools/capture/outcome_writer.py --stdin
    echo "DECISION_OUTCOME: ..." | python tools/capture/outcome_writer.py --stdin
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REFACTOR_DECISION_LEDGER_DB


_OUTCOME_MARKER_RE = re.compile(
    r"^DECISION_OUTCOME:\s*decision_id=(?P<decision_id>dec_[a-z0-9]+)(?P<tail>.*)$",
    re.MULTILINE,
)


def _parse_int(tail: str, key: str) -> int | None:
    m = re.search(rf"{re.escape(key)}\s*=\s*(\d+)", tail)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def _parse_string(tail: str, key: str, max_len: int = 200) -> str | None:
    # Strings stop at the next `, <word>=` boundary or end of line
    m = re.search(
        rf"{re.escape(key)}\s*=\s*(?P<v>[^,\n].*?)(?=,\s*\w+\s*=|\s*$)",
        tail,
    )
    if m:
        v = m.group("v").strip()
        return v[:max_len] if v else None
    return None


def parse_outcome(marker: str) -> dict[str, object] | None:
    """Parse a DECISION_OUTCOME marker line into a dict, or None if malformed."""
    m = _OUTCOME_MARKER_RE.search(marker.strip())
    if not m:
        return None
    tail = m.group("tail") or ""
    row: dict[str, object] = {
        "decision_id": m.group("decision_id"),
        "execution_completed": _parse_int(tail, "execution_completed") or 0,
        "tests_passed": _parse_int(tail, "tests_passed") or 0,
        "regression_found": _parse_int(tail, "regression_found") or 0,
        "rollback_required": _parse_int(tail, "rollback_required") or 0,
        "promote_to_pattern": _parse_int(tail, "promote_to_pattern") or 0,
    }
    lat = _parse_int(tail, "time_to_outcome_s")
    if lat is not None:
        row["latency_to_outcome_s"] = lat
    fdid = _parse_string(tail, "followup_decision_id", max_len=40)
    if fdid and re.match(r"^dec_[a-z0-9]+$", fdid):
        row["followup_decision_id"] = fdid
    notes = _parse_string(tail, "notes", max_len=300)
    if notes:
        row["outcome_notes"] = notes
    return row


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def write_outcome(conn: sqlite3.Connection, row: dict[str, object]) -> str:
    """INSERT or UPDATE the outcome row. Returns 'inserted', 'updated', or 'skipped'."""
    decision_id = row["decision_id"]
    existing = conn.execute(
        "SELECT outcome_id FROM decision_outcomes WHERE decision_id = ? LIMIT 1",
        (decision_id,),
    ).fetchone()

    cols = _table_columns(conn, "decision_outcomes")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Build the set of columns we can legally touch in this schema.
    payload: dict[str, object] = {}
    for k, v in row.items():
        if k in cols:
            payload[k] = v
    # Label for analytics
    if "outcome_label" in cols and "outcome_label" not in payload:
        if row.get("rollback_required"):
            payload["outcome_label"] = "rollback"
        elif row.get("regression_found"):
            payload["outcome_label"] = "rework"
        elif row.get("promote_to_pattern"):
            payload["outcome_label"] = "promote"
        elif row.get("tests_passed") and row.get("execution_completed"):
            payload["outcome_label"] = "success"
        else:
            payload["outcome_label"] = "undecided"
    if "bound_at" in cols and "bound_at" not in payload:
        payload["bound_at"] = now

    if existing:
        set_clause = ", ".join(f"{k} = :{k}" for k in payload if k != "decision_id")
        if not set_clause:
            return "skipped"
        payload["decision_id"] = decision_id
        conn.execute(
            f"UPDATE decision_outcomes SET {set_clause} WHERE decision_id = :decision_id",
            payload,
        )
        conn.commit()
        return "updated"

    # Fresh row — fill JSON fields that exist in schema with sane defaults
    for opt_col, default in (
        ("commit_shas_json", "[]"),
        ("files_written_json", "[]"),
        ("tests_run_json", "[]"),
    ):
        if opt_col in cols and opt_col not in payload:
            payload[opt_col] = default
    if "pattern_promotion_eligible" in cols and "pattern_promotion_eligible" not in payload:
        payload["pattern_promotion_eligible"] = int(bool(row.get("promote_to_pattern")))

    col_list = list(payload.keys())
    placeholders = ", ".join(f":{c}" for c in col_list)
    conn.execute(
        f"INSERT INTO decision_outcomes ({', '.join(col_list)}) VALUES ({placeholders})",
        payload,
    )
    conn.commit()
    return "inserted"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--marker", action="append", default=[], help="DECISION_OUTCOME line")
    src.add_argument("--stdin", action="store_true", help="Read lines from stdin")
    p.add_argument("--db", default=str(DB_PATH), help=f"Ledger path (default: {DB_PATH})")
    p.add_argument("--dry-run", action="store_true", help="Parse only; no DB write")
    args = p.parse_args(argv)

    lines: list[str] = []
    if args.stdin:
        if sys.stdin.isatty():
            print("[outcome_writer] error: --stdin but TTY", file=sys.stderr)
            return 2
        for ln in sys.stdin.read().splitlines():
            if "DECISION_OUTCOME:" in ln:
                lines.append(ln.strip())
    else:
        lines = [m.strip() for m in args.marker if m.strip()]

    if not lines:
        print("[outcome_writer] WARN: no DECISION_OUTCOME markers found", file=sys.stderr)
        return 0

    rows = []
    for ln in lines:
        r = parse_outcome(ln)
        if r is None:
            print(f"[outcome_writer] WARN: unparseable: {ln[:120]!r}", file=sys.stderr)
            continue
        rows.append(r)

    if args.dry_run:
        print(json.dumps(rows, indent=2))
        return 0

    db_path = Path(args.db)
    if not db_path.parent.exists():
        print(f"[outcome_writer] WARN: DB dir missing: {db_path.parent}", file=sys.stderr)
        return 0

    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
    except sqlite3.Error as exc:
        print(f"[outcome_writer] FATAL: cannot open DB: {exc}", file=sys.stderr)
        return 2

    try:
        counts = {"inserted": 0, "updated": 0, "skipped": 0, "missing_decision": 0}
        for r in rows:
            # Verify the decision exists — orphan outcomes are a warning, not a hard fail.
            exists = conn.execute(
                "SELECT 1 FROM decisions WHERE decision_id = ? LIMIT 1",
                (r["decision_id"],),
            ).fetchone()
            if not exists:
                counts["missing_decision"] += 1
                print(
                    f"[outcome_writer] WARN: decision_id={r['decision_id']} not in ledger",
                    file=sys.stderr,
                )
                continue
            try:
                disp = write_outcome(conn, r)
                counts[disp] += 1
            except sqlite3.Error as exc:
                print(f"[outcome_writer] WARN: write failed for {r['decision_id']}: {exc}", file=sys.stderr)
                counts["skipped"] += 1
        print(json.dumps(counts))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
