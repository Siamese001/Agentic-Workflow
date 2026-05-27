#!/usr/bin/env python3
"""Fail-closed audit: claim_text display policy + optional proof_text split (W2.3)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from apps_rg.fact_inventory.candidate_fact_ledger import (  # noqa: E402
    default_ledger_path,
    load_master_candidate_fact_ledger,
)
from apps_rg.fact_inventory.claim_proof_split_policy import (  # noqa: E402
    CLAIM_PROOF_SCHEMA_VERSION,
    claim_text_violates_i0_display_policy,
    validate_claim_proof_row,
)


def _audit_facts(facts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    failures: list[dict[str, Any]] = []
    for row in facts:
        if not isinstance(row, dict):
            failures.append({"row": row, "issues": ["not_a_dict"]})
            continue
        fid = str(row.get("candidate_fact_id") or row.get("fact_id") or "")
        issues: list[str] = []
        if not str(row.get("claim_text") or "").strip():
            issues.append("missing_claim_text")
        elif row.get("proof_text") is not None:
            issues.extend(validate_claim_proof_row(row))
        if issues:
            failures.append({"candidate_fact_id": fid, "issues": issues})
    return failures, len(facts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger",
        type=Path,
        default=None,
        help="Candidate fact ledger JSON (default: master_candidate_skills_fact_ledger)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report on stdout")
    args = parser.parse_args(argv)

    ledger_path = args.ledger or default_ledger_path(REPO_ROOT)
    payload = load_master_candidate_fact_ledger(path=ledger_path)
    facts = payload.get("candidate_facts") or []
    failures, total = _audit_facts(facts)
    report = {
        "schema_version": CLAIM_PROOF_SCHEMA_VERSION,
        "ledger_path": str(ledger_path).replace("\\", "/"),
        "facts_audited": total,
        "failure_count": len(failures),
        "failures": failures[:50],
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"audit_fact_ledger_claim_proof_split: {len(failures)} failures / {total} facts "
            f"(schema={CLAIM_PROOF_SCHEMA_VERSION})",
            file=sys.stderr,
        )
        for item in failures[:20]:
            print(f"  {item['candidate_fact_id']}: {', '.join(item['issues'])}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
