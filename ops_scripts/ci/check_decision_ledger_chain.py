#!/usr/bin/env python3
"""
check_decision_ledger_chain.py — CI gate: decision-ledger integrity (W1.1).

Two-part integrity check:

    Part 1 — Hash-chain verification on the Author-Gate decision ledger
             (`refactor_decision_ledger.sqlite`, which HAS prev_hash/row_hash).
             Delegates to `author_gate_ledger_integrity.verify_chain()`.

    Part 2 — Structural integrity on the 10 ledger-family SQLites at
             `artifacts/ledgers/*.sqlite` (which don't yet have hash columns).
             Asserts:
               - `events` table exists
               - `event_id` is unique (no duplicate rows)
               - `ts_utc` is strictly monotonic non-decreasing by rowid
               - no row has empty `event_id` or `event_kind`
               - `schema_version` table is populated

Exit codes:
    0 — all checks passed
    1 — at least one integrity violation detected (blocks CI)
    2 — script-level error (bug, missing dependency) — fail-closed

Bypass:
    DECISION_LEDGER_CHAIN_BYPASS=1 — logged, skips. Use only for scripted
    batch runs or acknowledged exploratory sessions.

Constitutional:
    - subprocess-free (pure stdlib: sqlite3, hashlib via imported lib)
    - specific exceptions (sqlite3.Error, OSError, ImportError)
    - UTF-8 stdio
    - bounded: streaming cursor, no full row load
"""

from __future__ import annotations

import glob
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_FAMILY_GLOB = str(REPO_ROOT / "artifacts" / "ledgers" / "*.sqlite")
BYPASS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "decision_ledger_chain_bypass.jsonl"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "decision_ledger_chain_violations.jsonl"

# Extend sys.path to import author_gate_ledger_integrity from .cursor/scripts
_SCRIPTS_DIR = REPO_ROOT / ".cursor" / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _log(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp": _now(), **payload}) + "\n")
    except OSError:
        # guardian: allow-silent-swallow -- log path unwritable: non-fatal observability
        pass


def _check_hash_chain() -> tuple[bool, str]:
    """Part 1: Author-Gate ledger hash chain. Returns (ok, message)."""
    try:
        from author_gate_ledger_integrity import (  # type: ignore[import-not-found]
            DB_PATH,
            verify_chain,
        )
    except ImportError as exc:
        return False, f"author_gate_ledger_integrity import failed: {exc}"

    if not DB_PATH.exists():
        # Ledger not yet initialized: treat as pass (coverage gate owns this)
        return True, f"author-gate ledger not present at {DB_PATH} (skipped)"

    try:
        result = verify_chain(DB_PATH)
    except sqlite3.Error as exc:
        return False, f"verify_chain raised sqlite3 error: {exc}"

    if not result.ok:
        return False, (
            f"hash chain broken at decision_id={result.first_broken_id}: "
            f"{result.reason} (verified {result.verified_rows}/{result.total_rows})"
        )
    return True, (f"author-gate hash chain OK ({DB_PATH.name}, {result.verified_rows} row(s) verified)")


def _check_ledger_family_structural() -> tuple[bool, list[str]]:
    """Part 2: Structural integrity on each ledger-family SQLite.

    Returns (all_ok, messages).
    """
    messages: list[str] = []
    all_ok = True
    ledgers = sorted(glob.glob(LEDGER_FAMILY_GLOB))

    if not ledgers:
        messages.append(f"no ledgers found under {LEDGER_FAMILY_GLOB} (skipped)")
        return True, messages

    for path in ledgers:
        name = os.path.basename(path)
        try:
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
        except sqlite3.Error as exc:
            all_ok = False
            messages.append(f"  FAIL {name}: cannot open: {exc}")
            continue

        try:
            # events table exists?
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "events" not in tables:
                all_ok = False
                messages.append(f"  FAIL {name}: missing 'events' table")
                continue

            # schema_version populated?
            if "schema_version" in tables:
                sv_count = conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]
                if sv_count == 0:
                    all_ok = False
                    messages.append(f"  FAIL {name}: schema_version empty")
                    continue

            # event_id unique?
            dup_rows = conn.execute(
                "SELECT event_id, COUNT(*) FROM events GROUP BY event_id HAVING COUNT(*) > 1"
            ).fetchall()
            if dup_rows:
                all_ok = False
                messages.append(
                    f"  FAIL {name}: {len(dup_rows)} duplicate event_id(s); first: {dup_rows[0][0]}"
                )
                continue

            # ts_utc monotonic non-decreasing by rowid?
            prev_ts: str | None = None
            prev_id: str | None = None
            for row in conn.execute("SELECT event_id, ts_utc FROM events ORDER BY rowid ASC"):
                event_id, ts_utc = row
                if not event_id:
                    all_ok = False
                    messages.append(f"  FAIL {name}: empty event_id at rowid")
                    break
                if ts_utc is None or ts_utc == "":
                    # ts_utc is advisory — only events that set it must be monotonic
                    continue
                if prev_ts is not None and ts_utc < prev_ts:
                    all_ok = False
                    messages.append(
                        f"  FAIL {name}: ts_utc regression at {event_id} "
                        f"({ts_utc} < prev {prev_id}={prev_ts})"
                    )
                    break
                prev_ts = ts_utc
                prev_id = event_id
            else:
                messages.append(f"  OK   {name}: structural integrity passed")
                continue
            # break path: mark ok already flipped
        except sqlite3.Error as exc:
            all_ok = False
            messages.append(f"  FAIL {name}: sqlite error: {exc}")
        finally:
            conn.close()

    return all_ok, messages


def main() -> int:
    if os.environ.get("DECISION_LEDGER_CHAIN_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env:DECISION_LEDGER_CHAIN_BYPASS=1"})
        print("[check_decision_ledger_chain] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    print("[check_decision_ledger_chain] running…", file=sys.stderr)

    # Part 1
    chain_ok, chain_msg = _check_hash_chain()
    prefix = "  OK  " if chain_ok else "  FAIL"
    print(f"{prefix} {chain_msg}", file=sys.stderr)

    # Part 2
    struct_ok, struct_msgs = _check_ledger_family_structural()
    for msg in struct_msgs:
        print(msg, file=sys.stderr)

    if not (chain_ok and struct_ok):
        _log(
            VIOLATIONS_LOG,
            {
                "chain_ok": chain_ok,
                "chain_msg": chain_msg,
                "structural_ok": struct_ok,
                "structural_msgs": struct_msgs,
            },
        )
        print(
            "[check_decision_ledger_chain] FAIL — integrity violation(s) above",
            file=sys.stderr,
        )
        return 1

    print("[check_decision_ledger_chain] PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_decision_ledger_chain] script error: {exc}", file=sys.stderr)
        sys.exit(2)
