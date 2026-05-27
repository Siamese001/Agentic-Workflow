"""Generate DRAFT skill triage report for human review.

Outputs: docs/reports/apps_rg/draft_skill_triage_report_20260527.md

For each DRAFT skill: shows skill_id, support_level, fact_id_links (existing or empty),
and suggested candidate fact IDs that could anchor it.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER_PATH = REPO / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
CANDIDATE_PATH = REPO / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
OUT_MD = REPO / "docs/reports/apps_rg/draft_skill_triage_report_20260527.md"


def main() -> None:
    ledger = json.loads(LEDGER_PATH.read_text())
    candidate = json.loads(CANDIDATE_PATH.read_text()) if CANDIDATE_PATH.exists() else {}
    candidate_facts = {
        f["candidate_fact_id"]: f
        for f in candidate.get("facts", [])
        if isinstance(f, dict) and f.get("candidate_fact_id")
    }

    skill_rows = ledger.get("skill_rows", [])
    drafts = [r for r in skill_rows if isinstance(r, dict) and r.get("activation_status") == "DRAFT"]

    lines: list[str] = [
        f"# DRAFT Skill Triage Report — {date.today().isoformat()}",
        "",
        f"Total DRAFT skills: **{len(drafts)}**  ",
        "Action required: for each row select PROMOTE | DEFER | BLOCK",
        "",
        "## Column Guide",
        "- **PROMOTE**: provide a `linked_fact_id` and mark `ACTIVE_CONFIRMED`",
        "- **DEFER**: skill is real but no source evidence yet — leave DRAFT",
        "- **BLOCK**: skill is not externally claimable — set `activation_status: BLOCKED`",
        "",
        "---",
        "",
        "## Triage Table",
        "",
        "| # | skill_id | pillar | support_level | has_facts | suggested_fact | Decision |",
        "|---|----------|--------|---------------|-----------|----------------|----------|",
    ]

    for i, row in enumerate(drafts, 1):
        sid = row.get("skill_id", "?")
        pillar = (row.get("pillar") or "").replace("pillar_", "")
        support = row.get("support_level", "?")
        facts = row.get("fact_id_links") or []
        has_facts = "✓" if facts else "✗"
        # Suggest a candidate fact by domain family overlap
        allowed = [str(p).lower() for p in (row.get("allowed_phrases") or [])]
        suggestion = ""
        for cfid, cf in candidate_facts.items():
            tags = [str(t).lower() for t in (cf.get("capability_tags") or [])]
            claim = str(cf.get("claim_text", "")).lower()
            if any(phrase and (phrase in claim or any(phrase in t for t in tags)) for phrase in allowed[:3]):
                suggestion = cfid
                break
        lines.append(f"| {i} | `{sid}` | {pillar[:25]} | {support} | {has_facts} | {suggestion or '—'} | ? |")

    lines += [
        "",
        "---",
        "",
        "## Instructions",
        "",
        "1. Fill the Decision column for each row.",
        "2. For PROMOTE rows: add `linked_fact_id` to the `apply_draft_skill_promotions_20260527.py` script.",
        "3. Run `python apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py` after promotions.",
        "4. Run `python apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py` to rebuild SQLite.",
        "",
        "Human confirmation required: `human_confirmed_by: Amit Ayer` with timestamp on each promoted skill.",
    ]

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written: {OUT_MD}")
    print(f"DRAFT skills: {len(drafts)}")


if __name__ == "__main__":
    main()
