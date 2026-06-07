#!/usr/bin/env python3
"""queue_to_ledger.py — Drain the capture queue into the SQLite decision ledger.

Reads ``artifacts/capture/markers.jsonl`` (written by ``append_marker.py``)
and applies each marker to the SQLite ledger by reusing the existing
``post_agent_author_gate_capture`` logic. After a successful drain, the
queue file is rotated to ``markers.<UTC-timestamp>.jsonl.processed`` so a
subsequent run does not re-process the same rows.

Idempotency: the underlying capture hook dedups via ``decision_id``, so
re-processing a queue (e.g., after a partial failure) is safe.

Usage:
    python tools/capture/queue_to_ledger.py            # drain default queue
    python tools/capture/queue_to_ledger.py --dry-run  # parse only, no DB write
    python tools/capture/queue_to_ledger.py --queue path/to/queue.jsonl
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUEUE = REPO_ROOT / "artifacts" / "capture" / "markers.jsonl"

# Make the capture hook importable. It's a script, not a package, so we add
# its directory to sys.path explicitly.
_HOOK_DIR = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"
if str(_HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOK_DIR))

try:
    # pylint: disable=import-error
    from post_agent_author_gate_capture import (  # type: ignore[import-not-found]
        _init_db,
        detect_and_capture,
    )
except ImportError as exc:
    print(f"[queue_to_ledger] FATAL: cannot import capture hook: {exc}", file=sys.stderr)
    sys.exit(2)


def load_queue(path: Path) -> list[dict]:
    """Load JSONL rows from the queue file. Skips malformed lines with WARN."""
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows: list[dict] = []
    for n, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        ln = ln.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
        except json.JSONDecodeError as exc:
            print(f"[queue_to_ledger] WARN line {n}: skipping malformed JSON ({exc})", file=sys.stderr)
            continue
        if not isinstance(obj, dict) or "raw" not in obj:
            print(f"[queue_to_ledger] WARN line {n}: row missing 'raw' field", file=sys.stderr)
            continue
        rows.append(obj)
    return rows


def drain(queue_path: Path, *, dry_run: bool = False) -> dict[str, int]:
    """Drain the queue. Returns counts by disposition.

    Dispositions:
      total            total rows read from queue
      captured         new DECISION_CAPTURED rows written to ledger
      skipped_dup      DECISION_CAPTURED rows already in ledger (decision_id match)
      deferred_scope   DEFERRED_SCOPE markers recognized; forwarding to Notion
                       is a separate pipeline not yet wired into this drain.
                       Markers are preserved in the rotated ``.processed.jsonl``.
      next_step        NEXT_STEP markers, same handling as deferred_scope.
      failed           rows where ledger write raised an exception.
    """
    rows = load_queue(queue_path)
    counts = {
        "total": len(rows),
        "captured": 0,
        "skipped_dup": 0,
        "deferred_scope": 0,
        "next_step": 0,
        "outcome_inserted": 0,
        "outcome_updated": 0,
        "outcome_orphan": 0,
        "failed": 0,
    }
    if not rows:
        return counts

    if dry_run:
        for r in rows:
            print(f"[dry-run] would capture: {r['raw'][:120]}")
        return counts

    conn = _init_db()
    if conn is None:
        print("[queue_to_ledger] FATAL: ledger DB init failed", file=sys.stderr)
        counts["failed"] = len(rows)
        return counts

    try:
        # Progress display per constitutional §16: only emit a bar for >10 items.
        emit_progress = len(rows) > 10
        for i, r in enumerate(rows, start=1):
            raw = r["raw"]
            mtype = r.get("marker_type", "")

            # Non-DECISION_CAPTURED markers are tracked but not forwarded to the
            # SQLite ledger by this drain. DEFERRED_SCOPE / NEXT_STEP have their
            # own Notion pipelines (post_agent_deferred_scope_capture.py /
            # post_agent_next_step_capture.py) that this drain does not yet
            # invoke. Markers remain in the rotated .processed.jsonl so the data
            # is preserved; a later drain extension can forward them.
            if mtype == "DEFERRED_SCOPE":
                counts["deferred_scope"] += 1
                continue
            if mtype == "NEXT_STEP":
                counts["next_step"] += 1
                continue
            if mtype == "DECISION_OUTCOME":
                # plan author-gate-hardening-a3b8f2 W1.P1.2 — drain outcome markers
                # via outcome_writer. Imported lazily so missing module can't break
                # the main decision drain.
                try:
                    # pylint: disable=import-outside-toplevel
                    sys.path.insert(0, str(REPO_ROOT))
                    from tools.capture.outcome_writer import parse_outcome, write_outcome  # type: ignore[import-not-found]
                except ImportError as exc:
                    print(f"[queue_to_ledger] WARN: outcome_writer import: {exc}", file=sys.stderr)
                    counts["failed"] += 1
                    continue
                parsed = parse_outcome(raw)
                if parsed is None:
                    counts["failed"] += 1
                    continue
                existing_dec = conn.execute(
                    "SELECT 1 FROM decisions WHERE decision_id = ? LIMIT 1",
                    (parsed["decision_id"],),
                ).fetchone()
                if not existing_dec:
                    counts["outcome_orphan"] += 1
                    continue
                try:
                    disp = write_outcome(conn, parsed)
                    if disp == "inserted":
                        counts["outcome_inserted"] += 1
                    elif disp == "updated":
                        counts["outcome_updated"] += 1
                except sqlite3.Error as exc:
                    print(f"[queue_to_ledger] WARN: outcome write failed: {exc}", file=sys.stderr)
                    counts["failed"] += 1
                continue

            try:
                captured = detect_and_capture(raw, conn)
            except (sqlite3.Error, ValueError) as exc:
                print(f"[queue_to_ledger] WARN: capture failed for row {i}: {exc}", file=sys.stderr)
                counts["failed"] += 1
                continue
            if captured:
                counts["captured"] += 1
            else:
                counts["skipped_dup"] += 1
            if emit_progress and (i % 5 == 0 or i == len(rows)):
                pct = int(100 * i / len(rows))
                bar_len = 40
                filled = int(bar_len * i / len(rows))
                bar = "\u2588" * filled + "\u2591" * (bar_len - filled)
                # Color: green at 90+, blue 70-89, yellow 40-69, red <40
                if pct >= 90:
                    color = "\033[92m"
                elif pct >= 70:
                    color = "\033[94m"
                elif pct >= 40:
                    color = "\033[93m"
                else:
                    color = "\033[91m"
                print(f"\r[{color}{bar}\033[0m] {pct:3d}% ({i}/{len(rows)}) drained", end="", file=sys.stderr)
        if emit_progress:
            print(file=sys.stderr)
    finally:
        conn.close()

    # Rotate the queue file so future runs don't re-process. All non-failed
    # dispositions count as "handled" for rotation purposes — deferred_scope
    # and next_step markers are preserved in the rotated file for later
    # forwarding to Notion.
    handled = (
        counts["captured"]
        + counts["skipped_dup"]
        + counts["deferred_scope"]
        + counts["next_step"]
    )
    if handled == counts["total"] and counts["failed"] == 0:
        # Microsecond precision plus a collision counter so rapid successive
        # drains (e.g., two invocations in the same second during tests) do
        # not race on the rotation target filename.
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        rotated = queue_path.with_name(f"{queue_path.stem}.{ts}.processed.jsonl")
        counter = 0
        while rotated.exists():
            counter += 1
            rotated = queue_path.with_name(
                f"{queue_path.stem}.{ts}-{counter}.processed.jsonl"
            )
        queue_path.rename(rotated)
        print(f"[queue_to_ledger] queue rotated to: {rotated.name}")
    elif counts["failed"] > 0:
        # Leave queue in place so failed rows can be retried.
        print(
            f"[queue_to_ledger] WARN: {counts['failed']} row(s) failed; queue NOT rotated",
            file=sys.stderr,
        )

    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE, help="Queue file path.")
    parser.add_argument("--dry-run", action="store_true", help="Parse only; no DB write or rotation.")
    args = parser.parse_args(argv)

    print(f"[queue_to_ledger] queue: {args.queue}")
    counts = drain(args.queue, dry_run=args.dry_run)
    print(
        f"[queue_to_ledger] total={counts['total']} "
        f"captured={counts['captured']} skipped_dup={counts['skipped_dup']} "
        f"deferred_scope={counts['deferred_scope']} "
        f"next_step={counts['next_step']} "
        f"failed={counts['failed']}"
    )
    return 0 if counts["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
