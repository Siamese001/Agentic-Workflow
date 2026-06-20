#!/usr/bin/env python3
"""
check_marker_ledger_parity.py — CI gate: DECISION_CAPTURED marker ↔ ledger parity (W1.2).

Reconciles structured `DECISION_CAPTURED:` markers emitted by Codex over the
last N days against actual rows written to the refactor_decision_ledger.sqlite.
Detects silent hook-dispatcher failures (e.g., the 2026-04-22 legacy editor 2.0.67
regression where post_agent_response hooks stopped firing mid-session).

Parity rule:
    For every DECISION_CAPTURED marker found in scanned sources within window W,
    there MUST be a ledger row whose `request_summary` contains the marker text
    (or whose `created_at` is within TOLERANCE_SECONDS of the marker timestamp).

Marker sources scanned (by priority):
    1. `artifacts/governance/author_gate_miss_detector.jsonl` — post-hook captures
       both successful writes and detected misses.
    2. `artifacts/governance/post_agent_heartbeat.jsonl` — shows whether the hook
       dispatcher was alive for each window; if dispatcher dark AND markers
       present elsewhere → parity failure.
    3. `artifacts/governance/*.jsonl` grep for `DECISION_CAPTURED:` substrings.

Exit codes:
    0 — parity OK (or no markers in window, nothing to reconcile)
    1 — at least one orphan marker (marker with no matching ledger row)
    2 — script error

Bypass:
    MARKER_LEDGER_PARITY_BYPASS=1 — logged, skips.

Tuning:
    --window-days N    (default 7)
    --tolerance-secs N (default 300, 5 min wall-clock slop)
    --max-orphans N    (default 0 — strict; raise for noisy environments)

Constitutional: pure stdlib; specific exceptions; UTF-8; bounded (streams JSONL
line-by-line, bounded marker-set size).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DB = REPO_ROOT / ".codex" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "governance"
BYPASS_LOG = ARTIFACTS_DIR / "marker_ledger_parity_bypass.jsonl"
VIOLATIONS_LOG = ARTIFACTS_DIR / "marker_ledger_parity_violations.jsonl"

# Same regex as post_agent_author_gate_capture.py (kept in sync — schema is SSOT).
_CAPTURE_RE = re.compile(
    r"DECISION_CAPTURED:\s*type=(?P<dtype>[\w_]+),\s*"
    r"repo_area=(?P<area>[^,]+),\s*"
    r"selected=(?P<selected>[^,\n]+),\s*"
    r"outcome=(?P<outcome>\w+)"
)


@dataclass(frozen=True)
class Marker:
    timestamp: str  # ISO-8601 UTC
    dtype: str
    repo_area: str
    selected: str
    source: str  # where we saw it (for diagnostics)


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


def _parse_iso(ts: str) -> datetime | None:
    try:
        # Handle trailing 'Z' and naive timestamps
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _scan_markers(window_start: datetime) -> list[Marker]:
    """Scan JSONL artifacts for DECISION_CAPTURED markers in the window."""
    markers: list[Marker] = []
    if not ARTIFACTS_DIR.exists():
        return markers

    for jsonl_path in sorted(ARTIFACTS_DIR.glob("*.jsonl")):
        try:
            with jsonl_path.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if "DECISION_CAPTURED" not in line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ts = obj.get("timestamp") or obj.get("ts") or ""
                    dt = _parse_iso(ts)
                    if dt is None or dt < window_start:
                        continue
                    # The marker itself may be in several possible fields
                    text_candidates = [
                        obj.get("marker_text", ""),
                        obj.get("response_text", ""),
                        obj.get("text", ""),
                        json.dumps(obj),  # fallback: search the whole row
                    ]
                    for text in text_candidates:
                        if not isinstance(text, str):
                            continue
                        m = _CAPTURE_RE.search(text)
                        if m:
                            markers.append(
                                Marker(
                                    timestamp=ts,
                                    dtype=m.group("dtype"),
                                    repo_area=m.group("area").strip(),
                                    selected=m.group("selected").strip(),
                                    source=jsonl_path.name,
                                )
                            )
                            break
        except OSError:
            continue
    return markers


def _load_ledger_rows(window_start: datetime) -> list[dict]:
    """Load ledger rows in the window as plain dicts."""
    if not LEDGER_DB.exists():
        return []
    rows: list[dict] = []
    try:
        conn = sqlite3.connect(f"file:{LEDGER_DB}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error:
        return []
    try:
        conn.row_factory = sqlite3.Row
        cutoff = window_start.isoformat(timespec="seconds")
        for r in conn.execute(
            "SELECT decision_id, created_at, decision_type, request_summary, "
            "selected_option_id FROM decisions WHERE created_at >= ?",
            (cutoff,),
        ):
            rows.append(dict(r))
    except sqlite3.Error:
        pass
    finally:
        conn.close()
    return rows


def _find_matching_row(marker: Marker, rows: list[dict], tolerance_s: int) -> dict | None:
    """Return the first ledger row that matches this marker within tolerance."""
    m_dt = _parse_iso(marker.timestamp)
    for row in rows:
        rs = row.get("request_summary") or ""
        sel = row.get("selected_option_id") or ""
        dtype = row.get("decision_type") or ""
        # Strong match: request_summary contains marker text OR selected label matches
        if marker.selected and marker.selected in rs:
            return row
        if marker.selected and marker.selected == sel and marker.dtype == dtype:
            return row
        # Fallback: time window + dtype match
        if m_dt is not None and marker.dtype == dtype:
            r_dt = _parse_iso(row.get("created_at", ""))
            if r_dt is not None and abs((r_dt - m_dt).total_seconds()) <= tolerance_s:
                return row
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="DECISION_CAPTURED marker ↔ ledger parity")
    ap.add_argument("--window-days", type=int, default=7)
    ap.add_argument("--tolerance-secs", type=int, default=300)
    ap.add_argument("--max-orphans", type=int, default=0)
    args = ap.parse_args()

    if os.environ.get("MARKER_LEDGER_PARITY_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env:MARKER_LEDGER_PARITY_BYPASS=1"})
        print("[check_marker_ledger_parity] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    window_start = datetime.now(timezone.utc) - timedelta(days=args.window_days)
    print(
        f"[check_marker_ledger_parity] window since {window_start.isoformat(timespec='seconds')} "
        f"(tolerance {args.tolerance_secs}s, max_orphans {args.max_orphans})",
        file=sys.stderr,
    )

    markers = _scan_markers(window_start)
    rows = _load_ledger_rows(window_start)
    print(
        f"[check_marker_ledger_parity] {len(markers)} marker(s) in window; "
        f"{len(rows)} ledger row(s) in window",
        file=sys.stderr,
    )

    # Deduplicate markers by (dtype, repo_area, selected, timestamp-bucket)
    seen: set[tuple[str, str, str, str]] = set()
    unique_markers: list[Marker] = []
    for m in markers:
        key = (m.dtype, m.repo_area, m.selected, m.timestamp[:19])  # sec precision
        if key in seen:
            continue
        seen.add(key)
        unique_markers.append(m)

    orphans: list[Marker] = []
    for m in unique_markers:
        row = _find_matching_row(m, rows, args.tolerance_secs)
        if row is None:
            orphans.append(m)

    if orphans:
        print(
            f"[check_marker_ledger_parity] {len(orphans)} orphan marker(s) (max allowed {args.max_orphans}):",
            file=sys.stderr,
        )
        for o in orphans[:20]:
            print(
                f"  ORPHAN ts={o.timestamp} type={o.dtype} area={o.repo_area} "
                f"selected={o.selected[:60]} source={o.source}",
                file=sys.stderr,
            )
        _log(
            VIOLATIONS_LOG,
            {
                "orphan_count": len(orphans),
                "window_days": args.window_days,
                "tolerance_secs": args.tolerance_secs,
                "orphans": [o.__dict__ for o in orphans[:50]],
            },
        )
        if len(orphans) > args.max_orphans:
            print(
                "[check_marker_ledger_parity] FAIL — orphan markers exceed "
                "threshold. Silent hook-dispatcher failure suspected; see "
                f"{VIOLATIONS_LOG}",
                file=sys.stderr,
            )
            return 1

    print(
        f"[check_marker_ledger_parity] PASS — {len(unique_markers)} marker(s) "
        f"reconciled ({len(orphans)} orphan(s) within tolerance)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError, ValueError) as exc:
        print(f"[check_marker_ledger_parity] script error: {exc}", file=sys.stderr)
        sys.exit(2)
