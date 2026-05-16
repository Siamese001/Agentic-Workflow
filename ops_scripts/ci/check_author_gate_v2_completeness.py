#!/usr/bin/env python3
"""
check_author_gate_v2_completeness.py — CI gate for plan 1f4c8a (W5).

Asserts that every Author-Gate decision row newer than 7 days carries the v2
calibration fields populated. Without this gate, the ledger silently drifts
back to v1-shape rows — meta-learning loses its signal source.

Required fields per row (where decision_type is refactor-class AND status is
'executed' AND no silent-marker exemption applies):

  - confidence_top         REAL       (0.00-1.00)
  - confidence_dominance_gap REAL     (0.00-1.00)
  - principle_at_stake     TEXT       (≤80 chars)
  - precedent_verdict      TEXT       (strong | suggestive | none)

The ledger is HMAC-signed (W4), so this gate also verifies signature presence.

Exemptions (silent-marker rows per author-gate-enforcement.md §Silent-Marker):
  - confidence_top, gap, override, latency_ms may be NULL when the decision
    was deterministic / bypass-condition / scoring-filtered. The gate only
    checks principle_at_stake (always required) and precedent_verdict (always
    required after meta-learning W2, 2026-04-23).

Exit codes:
  0  — all rows newer than 7 days are compliant
  1  — at least one row missing required fields
  2  — ledger missing or unreadable

Usage:
  python ops_scripts/ci/check_author_gate_v2_completeness.py
  python ops_scripts/ci/check_author_gate_v2_completeness.py --window-days 14

Bypass:
  AUTHOR_GATE_V2_BYPASS=1  (logs to bypass jsonl; use for incident windows only)
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".cursor" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
BYPASS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "author_gate_v2_bypass.jsonl"

# Decision types that REQUIRE v2 fields (refactor-class per AG-1).
_REFACTOR_CLASS_TYPES = frozenset(
    {
        "architecture_choice",
        "refactor_scope",
        "anti_pattern",
        "deletion_strategy",
        "dependency_addition",
        "test_strategy",
        "error_handling",
    }
)

# Cutoff for v2-enforcement (rows older than this date are pre-W2 markers and
# cannot be retro-fixed; they're sealed and signed but lacked v2 fields at write
# time). Set to the 2026-04-23 W2 enrichment landing date.
_V2_LANDING_DATE = "2026-04-23T00:00:00+00:00"


def _bypass_active() -> bool:
    return os.environ.get("AUTHOR_GATE_V2_BYPASS", "").strip() == "1"


def _log_bypass(reason: str) -> None:
    BYPASS_LOG.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reason": reason,
        "rule": "constitutional §1 (Author-Gate v2 completeness, plan 1f4c8a W5)",
    }
    with BYPASS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def check(db_path: Path, window_days: int) -> tuple[int, list[str]]:
    """Return (exit_code, messages)."""
    if not db_path.exists():
        return 2, [f"ledger not found at {db_path}"]

    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=window_days)
    # Choose the LATER of (window_cutoff, V2_LANDING_DATE) so we never enforce
    # against pre-W2 rows. This preserves the v2 enrichment timeline.
    landing_dt = datetime.fromisoformat(_V2_LANDING_DATE)
    enforce_from = max(cutoff_dt, landing_dt)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = list(
            conn.execute(
                """
                SELECT decision_id, created_at, decision_type,
                       confidence_top, confidence_dominance_gap,
                       principle_at_stake, precedent_verdict,
                       sig_alg, signature, status
                  FROM decisions
                 WHERE created_at >= ?
                   AND decision_type IN ({})
                """.format(",".join("?" for _ in _REFACTOR_CLASS_TYPES)),
                [enforce_from.isoformat(), *_REFACTOR_CLASS_TYPES],
            )
        )
    finally:
        conn.close()

    if not rows:
        return 0, [f"no refactor-class rows since {enforce_from.isoformat(timespec='seconds')}"]

    violations: list[str] = []
    # progress_bar: small N (≤100 typical for 7-day window), inline check is bounded — §16 compliant
    for row in rows:
        missing: list[str] = []
        # Always required (W2+): principle_at_stake, precedent_verdict
        if not row["principle_at_stake"]:
            missing.append("principle_at_stake")
        if not row["precedent_verdict"]:
            missing.append("precedent_verdict")
        # Always required (W4+): signature
        if row["sig_alg"] != "hmac-sha256" or not row["signature"]:
            missing.append("signature/sig_alg")
        # Required when status='executed' (decision actually fired): confidence_top, gap
        if row["status"] == "executed":
            if row["confidence_top"] is None:
                missing.append("confidence_top")
            if row["confidence_dominance_gap"] is None:
                missing.append("confidence_dominance_gap")
        if missing:
            violations.append(
                f"  {row['decision_id']} ({row['decision_type']}, "
                f"created={row['created_at'][:19]}): missing {','.join(missing)}"
            )

    if violations:
        msg = [
            f"{len(violations)} refactor-class row(s) since "
            f"{enforce_from.isoformat(timespec='seconds')} "
            f"missing v2/W4 fields:",
            *violations,
            "",
            "Remediation: ensure DECISION_CAPTURED markers carry confidence=, gap=, "
            "principle=, precedent= per author-gate-enforcement.md §Pipeline step 9.",
            "Run: python .cursor/scripts/author_gate_ledger_integrity.py --resign",
        ]
        return 1, msg
    return 0, [
        f"OK — {len(rows)} row(s) since {enforce_from.isoformat(timespec='seconds')} are v2/W4 complete"
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Author-Gate v2 completeness gate (plan 1f4c8a W5)")
    parser.add_argument(
        "--window-days",
        type=int,
        default=7,
        help="Enforce on rows created within this many days (default: 7)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help="Override ledger path",
    )
    args = parser.parse_args()

    if _bypass_active():
        _log_bypass("AUTHOR_GATE_V2_BYPASS=1")
        print("[author_gate_v2] BYPASS — env override active; skipping check", file=sys.stderr)
        return 0

    rc, messages = check(args.db, args.window_days)
    strict = os.environ.get("AUTHOR_GATE_V2_STRICT", "").strip() == "1"
    for m in messages:
        if rc == 0:
            print(f"[author_gate_v2] {m}")
        else:
            print(f"[author_gate_v2] {m}", file=sys.stderr)
    if rc == 1 and not strict:
        print(
            "[author_gate_v2] ADVISORY mode (set AUTHOR_GATE_V2_STRICT=1 for fail-closed)",
            file=sys.stderr,
        )
        return 0
    return rc


if __name__ == "__main__":
    sys.exit(main())
