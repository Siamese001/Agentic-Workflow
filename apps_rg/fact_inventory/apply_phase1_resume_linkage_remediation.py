"""
apply_phase1_resume_linkage_remediation.py

Wave 1 remediation for Phase I resume → graph skills gap.

Actions:
  W1.1 — Populate source_resume_files on 6 DRAFT skills with no source linkage.
  W1.2 — Promote skill_customer_nrr_predictive_analytics_20pct and
          skill_customer_satisfaction_nps_25pct from DRAFT → ACTIVE.

Run:
    python apps_rg/fact_inventory/apply_phase1_resume_linkage_remediation.py
    python apps_rg/fact_inventory/apply_phase1_resume_linkage_remediation.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / "apps_rg" / "fact_inventory" / "master_skills_arsenal_ledger.json"

# ── W1.1: Source linkage fixes ────────────────────────────────────────────────

W1_1_LINKAGE: dict[str, list[str]] = {
    "skill_capital_reserving": [
        "Chief AI Officer - Amit Ayer.docx",
        "CTO Resume - Amit Ayer.docx",
        "Strategic Finance - Amit Ayer.docx",
    ],
    "skill_greeks_delta": [
        "Quantitative Research & Trading - Amit Ayer.docx",
    ],
    "skill_greeks_rho": [
        "Quantitative Research & Trading - Amit Ayer.docx",
    ],
    "skill_greeks_convexity": [
        "Quantitative Research & Trading - Amit Ayer.docx",
    ],
    "skill_insurance_liabilities_embedded_options": [
        "Quantitative Research & Trading - Amit Ayer.docx",
        "Amit Ayer Resume - AI Financial Services.docx",
    ],
    "skill_insurance_liabilities_insurance_liabilities": [
        "Quantitative Research & Trading - Amit Ayer.docx",
    ],
}

# ── W1.2: DRAFT → ACTIVE promotions ──────────────────────────────────────────

W1_2_PROMOTIONS: dict[str, str] = {
    "skill_customer_nrr_predictive_analytics_20pct": "ACTIVE",
    "skill_customer_satisfaction_nps_25pct": "ACTIVE",
}

# Also fix source_resume_files for the promoted skills — update to .docx convention
W1_2_SOURCE_FIX: dict[str, list[str]] = {
    "skill_customer_nrr_predictive_analytics_20pct": [
        "Head of Customer Success - Amit Ayer.docx",
    ],
    "skill_customer_satisfaction_nps_25pct": [
        "Head of Customer Success - Amit Ayer.docx",
    ],
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] would write {path}")
        return
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    print(f"[SAVED] {path}")


def run(dry_run: bool = False) -> None:
    data = _load(LEDGER_PATH)
    skill_rows: list[dict] = data.get("skill_rows", [])

    changed_w11 = 0
    changed_w12 = 0
    report_lines: list[str] = []

    for row in skill_rows:
        sid = row.get("skill_id", "")

        # W1.1 — source linkage
        if sid in W1_1_LINKAGE:
            old_src = row.get("source_resume_files") or []
            new_src = W1_1_LINKAGE[sid]
            row["source_resume_files"] = new_src
            changed_w11 += 1
            report_lines.append(
                f"  W1.1 LINKED  {sid}: {old_src!r} -> {new_src!r}"
            )

        # W1.2 — activation_status promotion + source fix
        if sid in W1_2_PROMOTIONS:
            old_act = row.get("activation_status")
            new_act = W1_2_PROMOTIONS[sid]
            row["activation_status"] = new_act
            changed_w12 += 1
            report_lines.append(
                f"  W1.2 PROMOTE {sid}: {old_act} -> {new_act}"
            )

        if sid in W1_2_SOURCE_FIX:
            row["source_resume_files"] = W1_2_SOURCE_FIX[sid]
            report_lines.append(
                f"  W1.2 SRC_FIX {sid}: -> {W1_2_SOURCE_FIX[sid]!r}"
            )

    print(f"W1.1 source linkages applied: {changed_w11}")
    print(f"W1.2 DRAFT promotions applied: {changed_w12}")
    for line in report_lines:
        print(line)

    # Update metadata timestamp
    meta = data.get("metadata", {})
    if isinstance(meta, dict):
        meta["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        meta["last_updated_by"] = "apply_phase1_resume_linkage_remediation.py"
        data["metadata"] = meta

    _save(LEDGER_PATH, data, dry_run)
    print(f"\nTotal skill_rows: {len(skill_rows)}")
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
