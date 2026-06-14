#!/usr/bin/env python3
"""author_gate_learning_join_report.py — W5.1 calibration join (AG ledger × AUQ × outcomes).

Joins, in the **same** SSOT SQLite (``refactor_decision_ledger.sqlite``):

- ``decisions`` + ``decision_outcomes`` — recommendation vs selection vs ``outcome_label``
- ``ask_user_question_decisions`` — recommended_index vs ``selected_index`` (when table exists)
- **Weak link**: ASK JSON may reference an Author-Gate ``decision_id``; report counts linked pairs

Writes under ``docs/reports/calibration/``:

- ``ag_learning_join_<YYYY-Www>.json``
- ``ag_learning_join_<YYYY-Www>.md``

Usage::

    python ops_scripts/calibration/author_gate_learning_join_report.py
    python ops_scripts/calibration/author_gate_learning_join_report.py --days 14

Constitutional: UTF-8, sqlite3.Error contained, no gated policy changes.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB

DB_PATH = REFACTOR_DECISION_LEDGER_DB
REPORT_DIR = REPO_ROOT / "docs" / "reports" / "calibration"

# SLA: surfaced Author-Gate rows without completed bind (days)
_DEFAULT_SLA_UNBOUND_DAYS = 7


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,)
    ).fetchone()
    return row is not None


def _iso_year_week(dt: datetime) -> str:
    return dt.strftime("%Y-W%V")


def _collect_ag_stats(conn: sqlite3.Connection, since: str, until: str) -> dict[str, Any]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT d.decision_id, d.created_at, d.decision_type, d.status,
               d.recommended_option_id, d.selected_option_id,
               d.override_vs_recommendation,
               o.execution_completed, o.outcome_label
          FROM decisions d
          LEFT JOIN decision_outcomes o ON o.decision_id = d.decision_id
         WHERE d.created_at >= ? AND d.created_at < ?
        """,
        (since, until),
    ).fetchall()
    bound = 0
    took_rec = 0
    rec_and_sel = 0
    by_label: dict[str, int] = {}
    unbound_old = 0
    now = datetime.now(timezone.utc)

    for r in rows:
        ex = bool(r["execution_completed"])
        if ex:
            bound += 1
            ol = r["outcome_label"] or "NULL"
            by_label[ol] = by_label.get(ol, 0) + 1
        rid, sid = r["recommended_option_id"], r["selected_option_id"]
        if rid and sid:
            rec_and_sel += 1
            if rid == sid:
                took_rec += 1
        # SLA-ish: still surfaced / unexecuted and older than SLA window
        try:
            created = datetime.fromisoformat(str(r["created_at"]).replace("Z", "+00:00"))
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
        except ValueError:
            created = now
        age_d = (now - created).days
        st = (r["status"] or "").lower()
        if (not ex) and st == "surfaced" and age_d >= _DEFAULT_SLA_UNBOUND_DAYS:
            unbound_old += 1

    return {
        "decision_rows_in_window": len(rows),
        "bound_with_outcome": bound,
        "both_ids_present": rec_and_sel,
        "selected_equals_recommended_when_both_set": took_rec,
        "recommendation_match_rate": round(took_rec / rec_and_sel, 4) if rec_and_sel else None,
        "outcome_label_histogram": by_label,
        f"surfaced_unbound_>=_{_DEFAULT_SLA_UNBOUND_DAYS}d": unbound_old,
    }


def _collect_auq_stats(conn: sqlite3.Connection, since: str, until: str) -> dict[str, Any]:
    if not _table_exists(conn, "ask_user_question_decisions"):
        return {"table_present": False}
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT decision_id, created_at, recommended_index, selected_index,
               confidence_score, context, packet_json
          FROM ask_user_question_decisions
         WHERE created_at >= ? AND created_at < ?
        """,
        (since, until),
    ).fetchall()
    n = len(rows)
    pending = sum(1 for r in rows if r["selected_index"] is None)
    comparable = 0
    match = 0
    linked_ag_ids = 0
    linked_found_in_decisions = 0

    ag_ids_in_play: set[str] = set()
    for r in rows:
        ri, si = r["recommended_index"], r["selected_index"]
        if ri is not None and si is not None:
            comparable += 1
            if ri == si:
                match += 1
        raw = r["packet_json"]
        if not raw:
            continue
        try:
            pkt = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for key in (
            "author_gate_decision_id",
            "linked_author_gate_decision_id",
            "decision_id",
        ):
            v = pkt.get(key)
            if isinstance(v, str) and v and not v.startswith("auq_"):
                linked_ag_ids += 1
                ag_ids_in_play.add(v)
                break

    if ag_ids_in_play:
        qmarks = ",".join("?" * len(ag_ids_in_play))
        hit = conn.execute(
            f"SELECT COUNT(*) AS c FROM decisions WHERE decision_id IN ({qmarks})",
            tuple(ag_ids_in_play),
        ).fetchone()
        linked_found_in_decisions = int(hit["c"]) if hit else 0

    return {
        "table_present": True,
        "rows_in_window": n,
        "pending_no_selection": pending,
        "comparable_recommend_vs_selected": comparable,
        "selected_index_equals_recommended": match,
        "auq_recommendation_match_rate": round(match / comparable, 4) if comparable else None,
        "packets_with_embedded_non_auq_decision_id": linked_ag_ids,
        "embedded_ids_found_in_decisions_table": linked_found_in_decisions,
    }


def build_payload(days: int) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    since = start.isoformat(timespec="seconds")
    until = now.isoformat(timespec="seconds")

    if not DB_PATH.exists():
        return {
            "generated_at": until,
            "window_days": days,
            "ledger": str(DB_PATH),
            "error": "ledger_missing",
            "advisory_only": True,
            "report_version": "author-gate-learning-join-w4-1",
        }

    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
    except sqlite3.Error as exc:
        return {
            "generated_at": until,
            "window_days": days,
            "ledger": str(DB_PATH),
            "error": str(exc),
            "advisory_only": True,
            "report_version": "author-gate-learning-join-w4-1",
        }

    try:
        ag = _collect_ag_stats(conn, since, until)
        auq = _collect_auq_stats(conn, since, until)
    finally:
        conn.close()

    return {
        "generated_at": until,
        "window_start": since,
        "window_days": days,
        "week_label": _iso_year_week(now),
        "ledger": str(DB_PATH),
        "author_gate": ag,
        "ask_user_question": auq,
        "advisory_only": True,
        "report_version": "author-gate-learning-join-w4-1",
    }


def _render_md(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    wl = payload.get("week_label", "?")
    lines.append(f"# Author-Gate learning join report — {wl}")
    lines.append("")
    lines.append(f"- **Window:** last {payload.get('window_days')} days (UTC)")
    lines.append(f"- **Ledger:** `{payload.get('ledger')}`")
    lines.append("")
    if payload.get("error"):
        lines.append(f"_Error: {payload['error']}_")
        return "\n".join(lines) + "\n"

    ag = payload.get("author_gate") or {}
    lines.append("## Author-Gate decisions × outcomes")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    for k, v in ag.items():
        lines.append(f"| {k} | {v} |")
    lines.append("")

    auq = payload.get("ask_user_question") or {}
    lines.append("## ask_user_question decisions")
    lines.append("")
    if not auq.get("table_present"):
        lines.append("_Table `ask_user_question_decisions` not present._")
    else:
        lines.append("| Metric | Value |")
        lines.append("|---|---:|")
        for k, v in auq.items():
            if k == "table_present":
                continue
            lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("## Operator pointers")
    lines.append("")
    lines.append(
        "- SLA / capture troubleshooting: "
        "`docs/governance/author_gate_capture_outcome_sla_runbook.md`"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="W5 joined AG × AUQ × outcomes calibration report.")
    parser.add_argument("--days", type=int, default=7, help="Rolling window length (days)")
    args = parser.parse_args()

    payload = build_payload(max(1, args.days))
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"ag_learning_join_{payload.get('week_label', 'unknown')}"
    json_path = REPORT_DIR / f"{stem}.json"
    md_path = REPORT_DIR / f"{stem}.md"

    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    md_path.write_text(_render_md(payload), encoding="utf-8")

    print(f"[ag_learning_join] wrote {json_path}\n[ag_learning_join] wrote {md_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
