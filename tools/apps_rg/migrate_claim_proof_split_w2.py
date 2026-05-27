#!/usr/bin/env python3
"""Apply W2.2 claim/proof split to offending facts in candidate + SRFS ledgers."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from apps_rg.fact_inventory.claim_proof_split_policy import (  # noqa: E402
    CLAIM_PROOF_SCHEMA_VERSION,
    apply_w2_offending_fact_migrations,
    validate_claim_proof_row,
)

CANDIDATE_LEDGER = REPO_ROOT / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
SRFS_ACTIVE = REPO_ROOT / "artifacts/apps_rg/fact_inventory/selected_role_fact_set_active.json"
OFFENDING = frozenset({"fact_engineering_platform_001", "fact_quant_hpc_003"})


def _migrate_rows(rows: list[dict[str, Any]]) -> tuple[int, list[str]]:
    changed = 0
    errors: list[str] = []
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        fid = str(row.get("candidate_fact_id") or row.get("fact_id") or "")
        if fid not in OFFENDING:
            continue
        migrated = apply_w2_offending_fact_migrations(row)
        issues = validate_claim_proof_row(migrated)
        if issues:
            errors.append(f"{fid}: {issues}")
            continue
        if migrated != row:
            rows[idx] = migrated
            changed += 1
    return changed, errors


def main() -> int:
    if not CANDIDATE_LEDGER.is_file():
        print(f"ERROR: missing {CANDIDATE_LEDGER}", file=sys.stderr)
        return 1
    candidate = json.loads(CANDIDATE_LEDGER.read_text(encoding="utf-8"))
    facts = candidate.get("candidate_facts") or []
    changed_c, errors = _migrate_rows(facts)
    candidate["candidate_facts"] = facts
    md = candidate.setdefault("metadata", {})
    if isinstance(md, dict):
        md["claim_proof_split_schema_version"] = CLAIM_PROOF_SCHEMA_VERSION
    CANDIDATE_LEDGER.write_text(json.dumps(candidate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    changed_s = 0
    if SRFS_ACTIVE.is_file():
        srfs = json.loads(SRFS_ACTIVE.read_text(encoding="utf-8"))
        by_section = srfs.get("selected_facts_by_section")
        if isinstance(by_section, dict):
            for section_rows in by_section.values():
                if isinstance(section_rows, list):
                    delta, err_s = _migrate_rows(section_rows)
                    changed_s += delta
                    errors.extend(err_s)
        pool = srfs.get("candidate_facts") or srfs.get("facts")
        if isinstance(pool, list):
            delta, err_s = _migrate_rows(pool)
            changed_s += delta
            errors.extend(err_s)
        SRFS_ACTIVE.write_text(json.dumps(srfs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(
        f"OK: migrated candidate_ledger={changed_c} srfs_active={changed_s} "
        f"facts={','.join(sorted(OFFENDING))}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
