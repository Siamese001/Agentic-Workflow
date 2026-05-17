#!/usr/bin/env python3
"""author_gate_w0_baseline.py — W0 read-only ledger baseline (plan author-gate-feedback-loop-d4e8f1).

Captures schema inventory, null-rate metrics, decision_signals population,
calibration snapshot / confidence_calibrated variance hints, and replay of
lookup_refactor_decisions for a small sample of decisions. **No DB mutations.**

Usage::
    python tools/governance/author_gate_w0_baseline.py
    python tools/governance/author_gate_w0_baseline.py --out-dir artifacts/governance/author_gate_feedback_loop
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB  # noqa: E402

LOOKUP_SCRIPT = REPO_ROOT / ".cursor/skills/refactor-decision-memory/lookup_refactor_decisions.py"

TARGET_TABLES = (
    "decisions",
    "decision_outcomes",
    "decision_signals",
    "decision_calibration_snapshots",
)

W1_PLANNED_DECISION_COLUMNS = (
    "precedent_top_match_ids_json",
    "precedent_lookup_query_digest",
    "precedent_lookup_policy_version",
)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _git_head() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
            shell=False,
        )
        if r.returncode == 0 and r.stdout:
            return r.stdout.strip()[:40]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _table_columns(conn: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    cur = conn.execute(f'PRAGMA table_info("{table}")')
    out = []
    for cid, name, ctype, notnull, default, pk in cur.fetchall():
        out.append(
            {
                "cid": cid,
                "name": name,
                "type": ctype,
                "notnull": bool(notnull),
                "default": default,
                "pk": pk,
            }
        )
    return out


def _has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
    cols = {r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')}
    return col in cols


def _null_count(conn: sqlite3.Connection, table: str, col: str) -> int | None:
    if not _has_column(conn, table, col):
        return None
    row = conn.execute(
        f'SELECT COUNT(*) FROM "{table}" WHERE "{col}" IS NULL'
    ).fetchone()
    return int(row[0]) if row else 0


def _run_lookup(
    decision_type: str,
    normalized_intent: str,
    repo_area: str = "",
    *,
    degraded_scope: bool = False,
) -> dict[str, Any]:
    if not LOOKUP_SCRIPT.is_file():
        return {"error": "lookup_script_missing", "path": str(LOOKUP_SCRIPT)}
    query = {
        "decision_type": decision_type,
        "normalized_intent": normalized_intent,
        "repo_area": repo_area,
        "layer": "",
        "limit": 5,
        "degraded_scope": degraded_scope,
    }
    try:
        proc = subprocess.run(
            [sys.executable, str(LOOKUP_SCRIPT)],
            input=json.dumps(query),
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"error": "lookup_timeout", "query": query}
    except OSError as exc:
        return {"error": f"os_error:{exc}", "query": query}
    out_txt = (proc.stdout or "").strip()
    if proc.returncode != 0:
        return {
            "error": f"exit_{proc.returncode}",
            "stderr": (proc.stderr or "")[:500],
            "query": query,
        }
    try:
        return {"parsed": json.loads(out_txt), "query": query}
    except json.JSONDecodeError as exc:
        return {"error": f"invalid_json:{exc}", "raw": out_txt[:800], "query": query}


def _pick_sample_decisions(conn: sqlite3.Connection, n: int = 5) -> list[dict[str, Any]]:
    """Spread sample: first, last, up to three more from distinct decision_types."""
    total = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
    if total == 0:
        return []
    rows: list[dict[str, Any]] = []
    first = conn.execute(
        "SELECT decision_id, decision_type, normalized_intent, created_at "
        "FROM decisions ORDER BY created_at ASC LIMIT 1"
    ).fetchone()
    last = conn.execute(
        "SELECT decision_id, decision_type, normalized_intent, created_at "
        "FROM decisions ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if first:
        rows.append(
            {
                "decision_id": first[0],
                "decision_type": first[1],
                "normalized_intent": first[2] or "",
                "created_at": first[3],
                "sample_role": "first_by_created_at",
            }
        )
    if last and (not first or last[0] != first[0]):
        rows.append(
            {
                "decision_id": last[0],
                "decision_type": last[1],
                "normalized_intent": last[2] or "",
                "created_at": last[3],
                "sample_role": "last_by_created_at",
            }
        )
    seen_ids = {x["decision_id"] for x in rows}
    for (dtype,) in conn.execute(
        "SELECT DISTINCT decision_type FROM decisions ORDER BY decision_type"
    ).fetchall():
        if len(rows) >= n:
            break
        one = conn.execute(
            "SELECT decision_id, decision_type, normalized_intent, created_at "
            "FROM decisions WHERE decision_type = ? ORDER BY created_at DESC LIMIT 1",
            (dtype,),
        ).fetchone()
        if one and one[0] not in seen_ids:
            seen_ids.add(one[0])
            rows.append(
                {
                    "decision_id": one[0],
                    "decision_type": one[1],
                    "normalized_intent": one[2] or "",
                    "created_at": one[3],
                    "sample_role": f"latest_of_type:{dtype}",
                }
            )
    return rows[:n]


def build_baseline() -> dict[str, Any]:
    db_path = REFACTOR_DECISION_LEDGER_DB
    payload: dict[str, Any] = {
        "w0_receipt": True,
        "plan_id": "author-gate-feedback-loop-d4e8f1",
        "wave": "W0",
        "no_mutation": True,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ledger_path_relative": str(db_path.relative_to(REPO_ROOT).as_posix()),
        "ledger_path_resolved": str(db_path.resolve()),
        "git_head": _git_head(),
    }

    if not db_path.is_file():
        payload["error"] = "ledger_db_missing"
        return payload

    conn = sqlite3.connect(str(db_path.resolve()))
    try:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]
        payload["sqlite_table_inventory"] = tables

        schema: dict[str, Any] = {}
        for t in TARGET_TABLES:
            if t in tables:
                schema[t] = {"columns": _table_columns(conn, t)}
            else:
                schema[t] = {"missing": True}
        payload["target_schema"] = schema

        dcols = {r[1] for r in conn.execute('PRAGMA table_info("decisions")')}
        payload["w1_planned_columns_absent_on_decisions"] = [
            c for c in W1_PLANNED_DECISION_COLUMNS if c not in dcols
        ]

        n_dec = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        n_out = conn.execute("SELECT COUNT(*) FROM decision_outcomes").fetchone()[0]
        n_sig_rows = 0
        if "decision_signals" in tables:
            n_sig_rows = conn.execute(
                "SELECT COUNT(*) FROM decision_signals"
            ).fetchone()[0]
        n_cal_snap = 0
        if "decision_calibration_snapshots" in tables:
            n_cal_snap = conn.execute(
                "SELECT COUNT(*) FROM decision_calibration_snapshots"
            ).fetchone()[0]

        payload["row_counts"] = {
            "decisions": n_dec,
            "decision_outcomes": n_out,
            "decision_signals": n_sig_rows,
            "decision_calibration_snapshots": n_cal_snap,
        }

        null_rates: dict[str, Any] = {}
        for col in ("bind_confidence", "ci_receipt_status"):
            nc = _null_count(conn, "decision_outcomes", col)
            if nc is not None:
                null_rates[f"decision_outcomes.{col}_null"] = nc
            else:
                null_rates[f"decision_outcomes.{col}_null"] = "column_missing"

        for col in ("precedent_match_count", "confidence_top", "confidence_calibrated"):
            nc = _null_count(conn, "decisions", col)
            if nc is not None:
                null_rates[f"decisions.{col}_null"] = nc
            else:
                null_rates[f"decisions.{col}_null"] = "column_missing"

        payload["null_counts"] = null_rates

        sig_breakdown: dict[str, Any] = {"populated": n_sig_rows > 0}
        if "decision_signals" in tables and _has_column(conn, "decision_signals", "signal_name"):
            rows = conn.execute(
                "SELECT signal_name, COUNT(*) FROM decision_signals GROUP BY signal_name ORDER BY COUNT(*) DESC"
            ).fetchall()
            sig_breakdown["by_signal_name"] = {str(a): b for a, b in rows}
        payload["decision_signals"] = sig_breakdown

        cal_var: dict[str, Any] = {"snapshot_rows": n_cal_snap}
        if n_cal_snap:
            snaps = conn.execute(
                "SELECT snapshot_id, created_at, calibrator_version, decision_type, "
                "n_outcomes, brier_score, ece_score FROM decision_calibration_snapshots "
                "ORDER BY created_at"
            ).fetchall()
            cal_var["snapshots"] = [
                {
                    "snapshot_id": s[0],
                    "created_at": s[1],
                    "calibrator_version": s[2],
                    "decision_type": s[3],
                    "n_outcomes": s[4],
                    "brier_score": s[5],
                    "ece_score": s[6],
                }
                for s in snaps
            ]
        if n_dec and _has_column(conn, "decisions", "confidence_calibrated"):
            dist = conn.execute(
                "SELECT confidence_calibrated, COUNT(*) FROM decisions "
                "GROUP BY confidence_calibrated ORDER BY COUNT(*) DESC"
            ).fetchall()
            cal_var["confidence_calibrated_distribution"] = [
                {"value": v, "count": c} for v, c in dist
            ]
        if n_dec and _has_column(conn, "decisions", "confidence_top"):
            tops = conn.execute(
                "SELECT confidence_top, COUNT(*) FROM decisions "
                "GROUP BY confidence_top ORDER BY COUNT(*) DESC"
            ).fetchall()
            cal_var["confidence_top_distribution"] = [
                {"value": v, "count": c} for v, c in tops
            ]
        payload["calibration_variance"] = cal_var

        sample = _pick_sample_decisions(conn, 5)
        payload["lookup_sample_decisions"] = sample
        lookup_runs = []
        for s in sample:
            intent = s.get("normalized_intent") or ""
            dtype = s.get("decision_type") or "unknown"
            # Align with typical emit_packet usage: repo_area often matches normalized_intent path.
            repo_area = intent
            base = _run_lookup(dtype, intent, repo_area=repo_area)
            base["sample_decision_id"] = s.get("decision_id")
            base["sample_role"] = s.get("sample_role")
            lookup_runs.append(base)
        payload["lookup_runs"] = lookup_runs

        # Optional: same intent with degraded_scope=True if we have ≥1 run
        if sample:
            s0 = sample[0]
            degraded = _run_lookup(
                s0.get("decision_type") or "unknown",
                s0.get("normalized_intent") or "",
                "",
                degraded_scope=True,
            )
            degraded["note"] = "degraded_scope_probe"
            payload["lookup_degraded_scope_probe"] = degraded

    finally:
        conn.close()

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="W0 Author-Gate ledger baseline (read-only).")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "governance" / "author_gate_feedback_loop",
        help="Directory for baseline JSON",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Also print JSON to stdout",
    )
    args = parser.parse_args()
    data = build_baseline()
    stamp = _utc_stamp()
    out_base = args.out_dir.resolve() if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_base.mkdir(parents=True, exist_ok=True)
    out_path = out_base / f"{stamp}_w0_baseline.json"
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(out_path.relative_to(REPO_ROOT.resolve())), file=sys.stderr)
    if args.stdout:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
