#!/usr/bin/env python3
"""
detect_author_gate_ledger_anomalies.py — W4.1 heuristic anomaly signals.

Reads the refactor decision ledger (SSOT) and emits structured findings:
  - Future or skewed decision timestamps
  - outcome bound_at before decision created_at
  - Duplicate normalized_intent clusters (same type)
  - Bursts of promote_to_pattern rows in a short window

Outputs (UTF-8):
  - Append one JSON object per run to:
    artifacts/governance/author_gate_ledger_runs_anomalies.jsonl
  - Overwrite summary:
    artifacts/governance/author_gate_ledger_anomalies_latest.json

Behavior:
  - Default exit 0 (advisory) even when findings exist.
  - AUTHOR_GATE_ANOMALY_FAIL_CLOSED=1 → exit 1 if any **high** severity finding.
  - AUTHOR_GATE_ANOMALY_BYPASS=1 → skip work, exit 0.

Recovery (operator): inspect latest JSON / jsonl, validate rows in SQLite,
fix upstream writers or run hash-chain audit; re-run this detector.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB  # noqa: E402

RUNS_LOG = REPO_ROOT / "artifacts" / "governance" / "author_gate_ledger_runs_anomalies.jsonl"
LATEST_JSON = REPO_ROOT / "artifacts" / "governance" / "author_gate_ledger_anomalies_latest.json"

# Clock skew allowance for "future" decision timestamps
_FUTURE_SKEW = timedelta(minutes=5)
_DEFAULT_DUP_INTENT_MIN = 3
_DEFAULT_PROMO_BURST_HOURS = 24
_DEFAULT_PROMO_BURST_MAX = 15


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts or not str(ts).strip():
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Finding:
    code: str
    severity: str  # high | medium
    detail: str
    decision_id: str | None = None


def _find_future_decisions(conn: sqlite3.Connection, now: datetime) -> list[Finding]:
    out: list[Finding] = []
    try:
        rows = conn.execute(
            "SELECT decision_id, created_at FROM decisions WHERE created_at IS NOT NULL"
        ).fetchall()
    except sqlite3.Error:
        return out
    cutoff = now + _FUTURE_SKEW
    for row in rows:
        dt = _parse_iso(row["created_at"])
        if dt is None:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if dt > cutoff:
            out.append(
                Finding(
                    code="FUTURE_DECISION_TIMESTAMP",
                    severity="high",
                    detail=f"created_at {row['created_at']!r} is after now+skew",
                    decision_id=row["decision_id"],
                )
            )
    return out


def _find_bound_before_surfaced(conn: sqlite3.Connection) -> list[Finding]:
    out: list[Finding] = []
    try:
        rows = conn.execute(
            """
            SELECT d.decision_id, d.created_at, o.bound_at
              FROM decisions d
              JOIN decision_outcomes o ON o.decision_id = d.decision_id
             WHERE o.bound_at IS NOT NULL
               AND d.created_at IS NOT NULL
               AND datetime(o.bound_at) < datetime(d.created_at)
            """
        ).fetchall()
    except sqlite3.Error:
        return out
    for row in rows:
        out.append(
            Finding(
                code="BOUND_BEFORE_SURFACED",
                severity="high",
                detail=f"bound_at={row['bound_at']!r} precedes created_at={row['created_at']!r}",
                decision_id=row["decision_id"],
            )
        )
    return out


def _find_duplicate_intent_clusters(
    conn: sqlite3.Connection, min_count: int
) -> list[Finding]:
    out: list[Finding] = []
    try:
        rows = conn.execute(
            """
            SELECT normalized_intent, decision_type, COUNT(*) AS c
              FROM decisions
             WHERE normalized_intent IS NOT NULL
               AND TRIM(normalized_intent) != ''
             GROUP BY normalized_intent, decision_type
            HAVING c >= ?
            """,
            (min_count,),
        ).fetchall()
    except sqlite3.Error:
        return out
    for row in rows:
        out.append(
            Finding(
                code="DUPLICATE_INTENT_CLUSTER",
                severity="medium",
                detail=f"intent+type count={row['c']} type={row['decision_type']!r}",
                decision_id=None,
            )
        )
    return out


def _find_promotion_burst(
    conn: sqlite3.Connection, hours: int, max_promotions: int
) -> list[Finding]:
    if hours <= 0 or max_promotions <= 0:
        return []
    try:
        row = conn.execute(
            f"""
            SELECT COUNT(*) AS c
              FROM decision_outcomes o
              JOIN decisions d ON d.decision_id = o.decision_id
             WHERE COALESCE(o.promote_to_pattern, 0) = 1
               AND datetime(d.created_at) >= datetime('now', '-{int(hours)} hours')
            """
        ).fetchone()
    except sqlite3.Error:
        return []
    if row is None:
        return []
    c = int(row["c"])
    if c > max_promotions:
        return [
            Finding(
                code="PROMOTION_BURST_WINDOW",
                severity="medium",
                detail=f"promote_to_pattern=1 with decision created in last {hours}h: count={c} (threshold {max_promotions})",
                decision_id=None,
            )
        ]
    return []


def run_detection(
    *,
    dup_intent_min: int = _DEFAULT_DUP_INTENT_MIN,
    promo_hours: int = _DEFAULT_PROMO_BURST_HOURS,
    promo_max: int = _DEFAULT_PROMO_BURST_MAX,
) -> dict[str, Any]:
    now = _utcnow()
    findings: list[Finding] = []
    db_path = REFACTOR_DECISION_LEDGER_DB

    if not db_path.exists():
        payload = {
            "ts": now.isoformat(timespec="seconds"),
            "ledger": str(db_path),
            "findings": [],
            "summary": {"high": 0, "medium": 0, "skipped": "ledger_missing"},
        }
        return payload

    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        return {
            "ts": now.isoformat(timespec="seconds"),
            "ledger": str(db_path),
            "findings": [],
            "summary": {"high": 0, "medium": 0, "error": str(exc)},
        }

    try:
        findings.extend(_find_future_decisions(conn, now))
        findings.extend(_find_bound_before_surfaced(conn))
        findings.extend(_find_duplicate_intent_clusters(conn, dup_intent_min))
        findings.extend(_find_promotion_burst(conn, promo_hours, promo_max))
    finally:
        conn.close()

    high = sum(1 for f in findings if f.severity == "high")
    medium = sum(1 for f in findings if f.severity == "medium")
    return {
        "ts": now.isoformat(timespec="seconds"),
        "ledger": str(db_path),
        "findings": [asdict(f) for f in findings],
        "summary": {"high": high, "medium": medium, "total": len(findings)},
    }


def main() -> int:
    if os.environ.get("AUTHOR_GATE_ANOMALY_BYPASS", "").strip() == "1":
        print("[author_gate_anomalies] BYPASS — AUTHOR_GATE_ANOMALY_BYPASS=1", file=sys.stderr)
        return 0

    payload = run_detection()
    RUNS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RUNS_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    LATEST_JSON.parent.mkdir(parents=True, exist_ok=True)
    with LATEST_JSON.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    high = int(payload.get("summary", {}).get("high") or 0)
    med = int(payload.get("summary", {}).get("medium") or 0)
    print(
        f"[author_gate_anomalies] findings total={payload.get('summary', {}).get('total', 0)} "
        f"high={high} medium={med} latest={LATEST_JSON}",
        file=sys.stderr,
    )

    if os.environ.get("AUTHOR_GATE_ANOMALY_FAIL_CLOSED", "").strip() in ("1", "true", "yes"):
        if high > 0:
            print(
                "[author_gate_anomalies] FAIL — AUTHOR_GATE_ANOMALY_FAIL_CLOSED and high-severity findings",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
