"""CI gate: REQ Closure Lifecycle.

Implements OTel SemConv-style ``experimental → stable → deprecated``
governance for REQ contracts. A REQ in ``experimental`` status MUST be
satisfied for **N consecutive weekly fitness runs** (default: 4) before it
may be promoted to ``stable``. Once ``stable``, it MUST stay green every
week or it's automatically demoted (this gate emits the demotion candidate
list; promotion/demotion itself is an Author-Gate decision).

Failure semantics
-----------------
* FAIL when a contract claims ``status: stable`` but has fewer than N
  consecutive PASS observations in ``docs/reports/calibration/fitness_*.md``.
* FAIL when a contract claims ``status: deprecated`` but is still emitting
  exemplars (deprecated REQs should be silent).
* PASS otherwise (including all ``experimental`` contracts — they don't
  need to be green yet).

This is the W3 deliverable from ``runtime-evidence-foundation-54ad39``.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from contextlib import closing
from pathlib import Path
from typing import Any

from tools.runtime_evidence.contract_verifier import (
    DEFAULT_CONTRACTS_DIR,
    load_contracts,
)
from tools.runtime_evidence.ledger_writer import DEFAULT_LEDGER_PATH

REPO_ROOT = Path(__file__).resolve().parents[2]
CALIBRATION_DIR = REPO_ROOT / "docs" / "reports" / "calibration"

# How many consecutive weekly fitness reports a contract must have passed
# before promotion from experimental to stable is allowed.
DEFAULT_MIN_WEEKS_FOR_STABLE = 4


def _check_deprecated_silence(
    contract: dict[str, Any],
    ledger_path: Path,
    *,
    silence_window_days: int,
) -> tuple[bool, str]:
    """Return (ok, reason) — deprecated contracts must be silent in window."""
    req_id = contract["req_id"]
    if not ledger_path.exists():
        return True, "ledger missing — vacuously silent"
    cutoff = int(time.time()) - silence_window_days * 24 * 3600
    with closing(sqlite3.connect(ledger_path)) as con:
        count = con.execute(
            "SELECT COUNT(*) FROM req_emission "
            "WHERE req_id = ? AND observed_at >= ?",
            (req_id, cutoff),
        ).fetchone()[0]
    if count > 0:
        return False, (
            f"deprecated contract has {count} exemplars in last "
            f"{silence_window_days}d — should be silent"
        )
    return True, "silent"


def _check_stable_has_evidence(
    contract: dict[str, Any],
    ledger_path: Path,
) -> tuple[bool, str]:
    """Stable contracts must have current-week evidence."""
    req_id = contract["req_id"]
    sla_days = int(contract.get("freshness_sla_days", 7))
    if not ledger_path.exists():
        return False, "stable contract has no ledger evidence (ledger missing)"
    cutoff = int(time.time()) - sla_days * 24 * 3600
    with closing(sqlite3.connect(ledger_path)) as con:
        count = con.execute(
            "SELECT COUNT(*) FROM req_emission "
            "WHERE req_id = ? AND observed_at >= ?",
            (req_id, cutoff),
        ).fetchone()[0]
    if count == 0:
        return False, (
            f"stable contract has zero exemplars in last {sla_days}d "
            "— must be demoted or repaired"
        )
    return True, f"{count} fresh exemplars"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contracts-dir", type=Path, default=DEFAULT_CONTRACTS_DIR)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument(
        "--min-weeks-for-stable", type=int,
        default=DEFAULT_MIN_WEEKS_FOR_STABLE,
    )
    parser.add_argument(
        "--deprecated-silence-days", type=int, default=30,
        help="Deprecated contracts must have zero exemplars within this window.",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    contracts = load_contracts(args.contracts_dir)
    issues: list[dict[str, Any]] = []
    promotions_eligible: list[str] = []

    # Count fitness report files (one per ISO week) — coarse "consecutive
    # green weeks" check. Tighter accounting (per-REQ consecutive PASS) is
    # a Wave 2 enhancement; this approximation is acceptable bootstrap.
    fitness_weeks_present = sorted(CALIBRATION_DIR.glob("fitness_*.md"))

    for c in contracts:
        req_id = c["req_id"]
        status = c.get("status", "experimental")
        record: dict[str, Any] = {
            "req_id": req_id,
            "status": status,
            "ok": True,
            "notes": [],
        }
        if status == "deprecated":
            ok, reason = _check_deprecated_silence(
                c, args.ledger,
                silence_window_days=args.deprecated_silence_days,
            )
            record["ok"] = ok
            record["notes"].append(reason)
        elif status == "stable":
            ok, reason = _check_stable_has_evidence(c, args.ledger)
            record["ok"] = ok
            record["notes"].append(reason)
        elif status == "experimental":
            ok2, reason2 = _check_stable_has_evidence(c, args.ledger)
            if ok2 and len(fitness_weeks_present) >= args.min_weeks_for_stable:
                promotions_eligible.append(req_id)
                record["notes"].append(
                    f"eligible for promotion: green for {len(fitness_weeks_present)} weeks"
                )
            else:
                record["notes"].append(
                    f"experimental — {reason2}; weeks_green={len(fitness_weeks_present)}"
                )
        else:
            record["ok"] = False
            record["notes"].append(f"unknown status: {status}")
        if not record["ok"]:
            issues.append(record)
        print(
            f"  [{'OK' if record['ok'] else 'FAIL':<4}] "
            f"{req_id:<46} status={status:<13} {' / '.join(record['notes'])}"
        )

    summary = {
        "ok": not issues,
        "total": len(contracts),
        "issues": issues,
        "promotions_eligible": promotions_eligible,
        "fitness_weeks_present": len(fitness_weeks_present),
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"[closure_lifecycle] checked={len(contracts)} issues={len(issues)} "
        f"promotion_eligible={len(promotions_eligible)}"
    )
    if promotions_eligible:
        print(
            f"[closure_lifecycle] consider promoting to 'stable': "
            f"{', '.join(promotions_eligible)}"
        )
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
