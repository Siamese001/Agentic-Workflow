#!/usr/bin/env python3
"""
audit_ledger_coverage.py — Health report for the Author-Gate decision ledger.

Measures every known gap in end-to-end meta-learning:
    - Capture completeness (v2 field population per-column)
    - Scope completeness (any row / file_path / layer)
    - Outcome binding rate (executed decisions with outcome_rows)
    - Label distribution and test-signal presence
    - Promotion status (pattern_promotion_eligible, promote_to_pattern)
    - Hash-chain integrity (prev_hash and row_hash coverage)
    - Unreachable-commit count (SHAs no longer in git history)
    - Marker-grammar violation log size

Exit codes (CI-consumable):
    0  OK — all metrics above thresholds
    1  WARN — one or more metrics below recommended threshold but above hard floor
    2  FAIL — one or more metrics below hard floor

USAGE
    python .cursor/scripts/audit_ledger_coverage.py              # prose report, exit 0/1/2
    python .cursor/scripts/audit_ledger_coverage.py --json       # JSON for CI parsing
    python .cursor/scripts/audit_ledger_coverage.py --ci         # machine-readable, exit 2 on FAIL only

THRESHOLDS (adjustable via --min-bind-rate etc.)
    outcome_bind_rate   >=0.80 for OK, >=0.50 for WARN else FAIL
    v2_field_rate       >=0.90 for OK, >=0.70 for WARN else FAIL  (applies to refactor-class rows)
    scope_file_path_rate>=0.90 for OK, >=0.70 for WARN else FAIL
    hash_chain_rate     >=0.99 for OK, >=0.95 for WARN else FAIL
    marker_violations_24h <=5 for OK, <=20 for WARN else FAIL

CONSTITUTIONAL
    No shell, subprocess shell=False, UTF-8 stdio, specific exceptions.
"""

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".cursor" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
VIOLATIONS_PATH = REPO_ROOT / "artifacts" / "cursor" / "author_gate_capture_violations.jsonl"

_REFACTOR_CLASS_TYPES = frozenset({
    "refactor_scope", "architecture_choice", "anti_pattern", "deletion_strategy",
    "dependency_addition", "test_strategy", "error_handling",
})
# Fields required by the v2 marker grammar for refactor-class decisions
_V2_REQUIRED_COLS = ("confidence_top", "confidence_dominance_gap",
                     "selection_latency_ms", "principle_at_stake")


def _q(conn: sqlite3.Connection, sql: str, *params: Any) -> Any:
    return conn.execute(sql, params).fetchone()


def _sha_reachable(sha: str) -> bool:
    if not sha:
        return False
    try:
        r = subprocess.run(
            ["git", "cat-file", "-e", sha],
            cwd=str(REPO_ROOT),
            capture_output=True,
            shell=False,
            timeout=5,
            check=False,
        )
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _classify(value: float, ok: float, warn: float) -> str:
    if value >= ok:
        return "OK"
    if value >= warn:
        return "WARN"
    return "FAIL"


def compute_report(
    db_path: Path = DB_PATH,
    violations_path: Path = VIOLATIONS_PATH,
    min_bind_rate_ok: float = 0.80,
    min_bind_rate_warn: float = 0.50,
    min_v2_rate_ok: float = 0.90,
    min_v2_rate_warn: float = 0.70,
    min_scope_rate_ok: float = 0.90,
    min_scope_rate_warn: float = 0.70,
    min_hash_rate_ok: float = 0.99,
    min_hash_rate_warn: float = 0.95,
    max_violations_24h_ok: int = 5,
    max_violations_24h_warn: int = 20,
) -> dict[str, Any]:
    """Return a structured health report."""
    if not db_path.exists():
        return {"status": "FAIL", "reason": "ledger absent", "db_path": str(db_path)}

    conn = sqlite3.connect(str(db_path), timeout=10)
    try:
        total_d = _q(conn, "SELECT COUNT(*) FROM decisions")[0] or 0
        total_o = _q(conn, "SELECT COUNT(*) FROM decision_outcomes")[0] or 0
        executed = _q(conn, "SELECT COUNT(*) FROM decisions WHERE status='executed'")[0] or 0
        bound_executed = _q(
            conn,
            "SELECT COUNT(*) FROM decisions d "
            "JOIN decision_outcomes o ON o.decision_id=d.decision_id "
            "WHERE d.status='executed'",
        )[0] or 0

        # Capture completeness (refactor-class rows only)
        refactor_types = ",".join(f"'{t}'" for t in _REFACTOR_CLASS_TYPES)
        refactor_rows = _q(
            conn, f"SELECT COUNT(*) FROM decisions WHERE decision_type IN ({refactor_types})"
        )[0] or 0
        v2_complete = 0
        if refactor_rows:
            cond = " AND ".join(f"{c} IS NOT NULL" for c in _V2_REQUIRED_COLS)
            v2_complete = _q(
                conn,
                f"SELECT COUNT(*) FROM decisions WHERE decision_type IN ({refactor_types}) AND {cond}",
            )[0] or 0

        # Scope completeness
        with_scope = _q(
            conn,
            "SELECT COUNT(DISTINCT decision_id) FROM decision_scope",
        )[0] or 0
        with_file_path = _q(
            conn,
            "SELECT COUNT(DISTINCT decision_id) FROM decision_scope "
            "WHERE file_path IS NOT NULL AND file_path!=''",
        )[0] or 0

        # Label + test signal
        with_label = _q(
            conn, "SELECT COUNT(*) FROM decision_outcomes WHERE outcome_label IS NOT NULL"
        )[0] or 0
        with_tests_passed = _q(
            conn, "SELECT COUNT(*) FROM decision_outcomes WHERE tests_passed=1"
        )[0] or 0
        label_dist: dict[str, int] = {}
        for lbl, n in conn.execute(
            "SELECT COALESCE(outcome_label,'NULL'), COUNT(*) "
            "FROM decision_outcomes GROUP BY outcome_label"
        ):
            label_dist[lbl] = n

        # Promotion
        promoted = _q(
            conn, "SELECT COUNT(*) FROM decision_outcomes WHERE promote_to_pattern=1"
        )[0] or 0
        eligible = _q(
            conn,
            "SELECT COUNT(*) FROM decision_outcomes WHERE pattern_promotion_eligible=1",
        )[0] or 0

        # Hash chain
        with_row_hash = _q(
            conn, "SELECT COUNT(*) FROM decisions WHERE row_hash IS NOT NULL"
        )[0] or 0

        # Unreachable commits (executed decisions without outcome whose SHA is gone)
        unreachable = 0
        for (sha,) in conn.execute(
            "SELECT DISTINCT commit_sha FROM decisions d "
            "WHERE d.status='executed' AND d.commit_sha IS NOT NULL "
            "AND NOT EXISTS (SELECT 1 FROM decision_outcomes o WHERE o.decision_id=d.decision_id)"
        ):
            if sha and not _sha_reachable(sha):
                unreachable += 1
    finally:
        conn.close()

    # Violations last 24h
    violations_24h = 0
    if violations_path.exists():
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        try:
            with violations_path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    try:
                        row = json.loads(line)
                        ts_str = row.get("timestamp", "")
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if ts >= cutoff:
                            violations_24h += 1
                    except (ValueError, json.JSONDecodeError):
                        continue
        except OSError:
            pass

    # Rates
    bind_rate = bound_executed / executed if executed else 1.0
    v2_rate = v2_complete / refactor_rows if refactor_rows else 1.0
    scope_rate = with_file_path / total_d if total_d else 1.0
    hash_rate = with_row_hash / total_d if total_d else 1.0

    statuses = {
        "bind_rate": _classify(bind_rate, min_bind_rate_ok, min_bind_rate_warn),
        "v2_rate": _classify(v2_rate, min_v2_rate_ok, min_v2_rate_warn),
        "scope_rate": _classify(scope_rate, min_scope_rate_ok, min_scope_rate_warn),
        "hash_rate": _classify(hash_rate, min_hash_rate_ok, min_hash_rate_warn),
        "violations_24h": (
            "OK" if violations_24h <= max_violations_24h_ok
            else "WARN" if violations_24h <= max_violations_24h_warn
            else "FAIL"
        ),
    }
    if any(s == "FAIL" for s in statuses.values()):
        overall = "FAIL"
    elif any(s == "WARN" for s in statuses.values()):
        overall = "WARN"
    else:
        overall = "OK"

    return {
        "status": overall,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "totals": {
            "decisions": total_d,
            "outcomes": total_o,
            "executed": executed,
            "bound_executed": bound_executed,
            "refactor_class_rows": refactor_rows,
            "v2_complete_rows": v2_complete,
            "scope_any": with_scope,
            "scope_with_file_path": with_file_path,
            "outcomes_with_label": with_label,
            "outcomes_with_tests_passed": with_tests_passed,
            "promoted": promoted,
            "eligible": eligible,
            "with_row_hash": with_row_hash,
            "unreachable_shas": unreachable,
            "capture_violations_24h": violations_24h,
        },
        "rates": {
            "bind_rate": round(bind_rate, 4),
            "v2_rate": round(v2_rate, 4),
            "scope_rate": round(scope_rate, 4),
            "hash_rate": round(hash_rate, 4),
        },
        "statuses": statuses,
        "label_distribution": label_dist,
    }


def _print_report(rep: dict[str, Any]) -> None:
    print(f"=== LEDGER HEALTH: {rep['status']} ({rep['generated_at']}) ===\n")
    t = rep["totals"]
    print(f"  decisions={t['decisions']}  outcomes={t['outcomes']}  executed={t['executed']}")
    print()
    r = rep["rates"]
    s = rep["statuses"]
    print(f"  [{s['bind_rate']:4}] outcome_bind_rate     = {r['bind_rate']:.2%}  "
          f"({t['bound_executed']}/{t['executed']})")
    print(f"  [{s['v2_rate']:4}] v2_field_completeness = {r['v2_rate']:.2%}  "
          f"({t['v2_complete_rows']}/{t['refactor_class_rows']} refactor-class rows)")
    print(f"  [{s['scope_rate']:4}] scope_file_path_rate  = {r['scope_rate']:.2%}  "
          f"({t['scope_with_file_path']}/{t['decisions']})")
    print(f"  [{s['hash_rate']:4}] hash_chain_rate       = {r['hash_rate']:.2%}  "
          f"({t['with_row_hash']}/{t['decisions']})")
    print(f"  [{s['violations_24h']:4}] capture_violations_24h = {t['capture_violations_24h']}")
    print()
    print(f"  label distribution: {rep['label_distribution']}")
    print(f"  tests_passed=1 rows: {t['outcomes_with_tests_passed']}  "
          f"<-- 0 today; needs W3.2 pytest hook")
    print(f"  promoted patterns  : {t['promoted']}  (eligible={t['eligible']})")
    print(f"  unreachable SHAs   : {t['unreachable_shas']}  "
          f"(orphan decisions lost to git history mutation)")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--json", action="store_true", help="Emit JSON instead of prose")
    p.add_argument("--ci", action="store_true",
                   help="Exit 2 only on FAIL (not WARN). For pre-commit / CI.")
    args = p.parse_args()

    rep = compute_report()
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        _print_report(rep)

    if args.ci:
        return 2 if rep.get("status") == "FAIL" else 0
    return {"OK": 0, "WARN": 1, "FAIL": 2}.get(rep.get("status", "FAIL"), 2)


if __name__ == "__main__":
    sys.exit(main())
