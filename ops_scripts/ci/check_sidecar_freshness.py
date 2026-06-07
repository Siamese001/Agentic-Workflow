#!/usr/bin/env python3
"""
check_sidecar_freshness.py — CI gate: author_gate_precedent.json freshness (W2.2).

`pre_author_gate.py` writes `artifacts/governance/author_gate_precedent.json`
when a gate fires AND clears it on gate-pass. A stale sidecar indicates a
crashed/killed pre-hook run and can leak precedent from a prior unrelated
decision into the next Author-Gate packet.

This gate fails when:
    - sidecar exists AND
    - generated_at is older than --max-age-minutes (default 60) AND
    - no pre_author_gate run has logged a matching fingerprint since
      (inferred from mtime of the sidecar vs mtime of author_gate_session_state.json)

Bypass:
    SIDECAR_FRESHNESS_BYPASS=1 — logged, skips.

Constitutional: pure stdlib; specific exceptions; UTF-8; bounded.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / "artifacts" / "governance"
SIDECAR = STATE_DIR / "author_gate_precedent.json"
SESSION_STATE = STATE_DIR / "author_gate_session_state.json"
BYPASS_LOG = STATE_DIR / "sidecar_freshness_bypass.jsonl"
VIOLATIONS_LOG = STATE_DIR / "sidecar_freshness_violations.jsonl"


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
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Author-Gate precedent sidecar freshness check")
    ap.add_argument(
        "--max-age-minutes",
        type=int,
        default=240,
        help="Sidecar older than this with no session activity = stale "
        "(default 240min = 4h, enough for a normal work session)",
    )
    args = ap.parse_args()

    if os.environ.get("SIDECAR_FRESHNESS_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env:SIDECAR_FRESHNESS_BYPASS=1"})
        print("[check_sidecar_freshness] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    if not SIDECAR.exists():
        print(f"[check_sidecar_freshness] OK — no sidecar present ({SIDECAR.name})", file=sys.stderr)
        return 0

    try:
        with SIDECAR.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[check_sidecar_freshness] FAIL — sidecar unreadable: {exc}", file=sys.stderr)
        _log(VIOLATIONS_LOG, {"reason": "unreadable", "error": str(exc)})
        return 1

    generated_at = payload.get("generated_at", "")
    gen_dt = _parse_iso(generated_at)
    if gen_dt is None:
        print(
            f"[check_sidecar_freshness] FAIL — sidecar missing/bad generated_at: {generated_at!r}",
            file=sys.stderr,
        )
        _log(VIOLATIONS_LOG, {"reason": "bad_generated_at", "raw": generated_at})
        return 1

    now = datetime.now(timezone.utc)
    age_min = (now - gen_dt).total_seconds() / 60.0

    # Cross-check: has pre_author_gate run since sidecar was written?
    # If session_state.json is newer than the sidecar AND the sidecar is still
    # present, that indicates pre_author_gate passed but forgot to clear —
    # treat as stale.
    session_newer_than_sidecar = False
    if SESSION_STATE.exists():
        try:
            if SESSION_STATE.stat().st_mtime > SIDECAR.stat().st_mtime + 5:
                session_newer_than_sidecar = True
        except OSError:
            pass

    match_count = payload.get("match_count", 0)
    fingerprint = payload.get("fingerprint", "")

    if age_min > args.max_age_minutes:
        reason = (
            f"sidecar age {age_min:.1f}min > max {args.max_age_minutes}min "
            f"(match_count={match_count}, fingerprint={fingerprint[:16]})"
        )
        print(f"[check_sidecar_freshness] FAIL — {reason}", file=sys.stderr)
        _log(
            VIOLATIONS_LOG,
            {
                "reason": "age_exceeded",
                "age_minutes": age_min,
                "max_age_minutes": args.max_age_minutes,
                "match_count": match_count,
                "fingerprint": fingerprint,
                "session_newer_than_sidecar": session_newer_than_sidecar,
            },
        )
        return 1

    if session_newer_than_sidecar:
        print(
            f"[check_sidecar_freshness] FAIL — sidecar present but session_state "
            f"is newer (pre_author_gate should have cleared sidecar on pass); "
            f"age={age_min:.1f}min match_count={match_count}",
            file=sys.stderr,
        )
        _log(
            VIOLATIONS_LOG,
            {
                "reason": "session_newer_uncleared",
                "age_minutes": age_min,
                "match_count": match_count,
            },
        )
        return 1

    print(
        f"[check_sidecar_freshness] OK — sidecar age {age_min:.1f}min, "
        f"match_count={match_count}, fingerprint={fingerprint[:16]}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:
        print(f"[check_sidecar_freshness] script error: {exc}", file=sys.stderr)
        sys.exit(2)
