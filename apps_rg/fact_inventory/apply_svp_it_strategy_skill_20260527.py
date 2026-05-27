"""Mint skill_svp_it_strategy_innovation — closes jd_inferred_skill_svp_it_strategy admission gap.

Anchors SVP IT Strategy & Innovation targeting (Brown & Brown) to candidate facts;
does not use JD text as proof.

Usage::

    python apps_rg/fact_inventory/apply_svp_it_strategy_skill_20260527.py
    python apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py
    python apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.apply_draft_skill_promotions_20260527 import (
    HUMAN_CONFIRMED_BY,
    _reject_draft_promotion_reason,
    _utc_now,
)
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    _rewire_skill_fact_edges,
    _sync_skill_row_to_payload_collections,
    build_skill_rows_by_id,
    load_candidate_fact_promotion_registry,
    resolve_confidence_grade,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    assert_no_jd_briefing_as_proof_fact_ids,
    default_arsenal_ledger_path,
    validate_arsenal_ledger_shape,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_LEDGER = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
CLOSEOUT_JSON = ROOT / "docs/reports/apps_rg/svp_it_strategy_skill_closeout.json"
CLOSEOUT_MD = ROOT / "docs/reports/apps_rg/svp_it_strategy_skill_closeout.md"

SKILL_ID = "skill_svp_it_strategy_innovation"
FACT_ID_LINKS = [
    "fact_exec_001",
    "fact_consulting_001",
    "fact_partnerships_gtm_005",
]
WAVE_ID = "svp_it_strategy_skill_mint_20260527"


def _new_skill_row() -> dict[str, Any]:
    return {
        "skill_id": SKILL_ID,
        "fact_id_links": [],
        "pillar": "pillar_insurer_it_strategy_ai_enablement",
        "subpillar": "svp_it_strategy_innovation",
        "career_stage": "cross_career",
        "source_resume_files": [
            "AI and Data Governance - Amit Ayer.txt",
            "Strategic Finance - Amit Ayer.txt",
            "Sales - Amit Ayer.txt",
        ],
        "source_snippets": [
            "Partnered with C-suite executives and cross-functional leaders to align AI, analytics, "
            "cloud, risk, and financial strategies with measurable business outcomes.",
            "Directed large-scale regulatory IT transformations and legacy-modernization programs "
            "for major financial institutions across risk, compliance, data, cloud, and architecture domains.",
        ],
        "user_confirmed": True,
        "support_level": "DERIVED_SUPPORTED",
        "role_family_weights": {
            "INSURANCE_BROKERAGE_IT_INNOVATION": 1.0,
            "EXECUTIVE_LEADERSHIP": 1.0,
            "PRODUCT_TECHNICAL_STRATEGY": 0.95,
            "AI_SOLUTIONS_ARCHITECTURE": 0.9,
            "INSURER_IT_AI_ENABLEMENT": 0.95,
        },
        "allowed_phrases": [
            "IT Strategy & Innovation",
            "IT strategy",
            "enterprise architecture",
            "innovation agenda",
            "enterprise innovation",
            "technology direction",
            "CITO",
        ],
        "forbidden_phrases": [
            "Head of Customer Success",
            "Chief Customer Officer",
            "customer success primary",
        ],
        "allowed_sections": [
            "executive_summary",
            "headline",
            "competencies",
            "unify_narrative",
        ],
        "visibility_rule": "role_family_match",
        "evidence_risk": "medium",
        "activation_status": "DRAFT",
        "human_confirmation_required": False,
        "external_claim_policy": "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "projection_behavior": "rank_and_project_facts",
        "career_epoch": "epoch_enterprise_risk_governance",
        "domain_id": "domain_senior_role_w8_w11",
        "domain": "Senior Role W8–W11 Graph",
        "capability": "svp_it_strategy_innovation",
        "source_concepts": [],
        "repo_evidence_files": [],
        "node_type": "skill_row",
        "ats_keywords": [
            "svp_it_strategy_innovation",
            "it_strategy",
            "enterprise_architecture",
        ],
        "achievement_framing_guidance": (
            "Frame SVP IT strategy and innovation with scope, mechanism, and outcome; "
            "metrics only from linked fact_id."
        ),
        "quantification_policy": "No invented numbers; require metric-bound fact_id or approved derivative.",
        "narrative_synthesis_guidance": (
            "Synthesize only from linked fact_id_links and approved bundles; skill_id is not proof."
        ),
        "claim_verification_policy": (
            "External resume claims allowed only when external_claim_policy permits and fact_id backs metrics."
        ),
        "zero_hallucination_guardrail": (
            "Do not claim SVP IT strategy beyond linked facts and archive snippets; fail closed if proof missing."
        ),
        "career_track_id": "TRACK_DATA_TECH_CLOUD_ML",
    }


def _promote_row(
    payload: dict[str, Any],
    row: dict[str, Any],
    *,
    fact_ids: list[str],
    human_confirmed_by: str = HUMAN_CONFIRMED_BY,
) -> dict[str, Any]:
    ts = _utc_now()
    registry = load_candidate_fact_promotion_registry(repo_root=ROOT)
    clean_facts = [str(x).strip() for x in fact_ids if str(x).strip()]
    assert_no_jd_briefing_as_proof_fact_ids(clean_facts)

    reason = _reject_draft_promotion_reason(row, clean_facts, registry=registry)
    if reason:
        raise ValueError(f"promotion rejected for {SKILL_ID}: {reason}")

    record = {
        "human_confirmed_by": human_confirmed_by,
        "human_confirmed_at": ts,
        "source_fact_ids": clean_facts,
        "override_reason": WAVE_ID,
        "targets_jd_inferred_skill": "jd_inferred_skill_svp_it_strategy",
    }
    row = dict(row)
    row["human_confirmed_archive_promotion"] = record
    row["fact_id_links"] = clean_facts
    row["primary_fact_id"] = clean_facts[0]
    row["activation_status"] = "ACTIVE_CONFIRMED"
    row["user_confirmed"] = True
    row["human_confirmation_required"] = False
    row["svp_it_strategy_skill_minted_at"] = ts

    resolved = resolve_confidence_grade(row, has_fact_link=True, candidate_registry=registry)
    row["confidence_grade_derived"] = resolved["derived_grade"]
    row["confidence_grade"] = resolved["effective_grade"]

    _sync_skill_row_to_payload_collections(payload, row)
    edge_n = _rewire_skill_fact_edges(payload, SKILL_ID, clean_facts)

    gm = payload.setdefault("graph_metadata", {})
    if isinstance(gm, dict):
        gm["svp_it_strategy_skill_mint"] = {
            "applied_at": ts,
            "skill_id": SKILL_ID,
            "fact_id_links": clean_facts,
            "replaces_jd_inferred": "jd_inferred_skill_svp_it_strategy",
            "human_confirmed_by": human_confirmed_by,
        }

    return {
        "skill_id": SKILL_ID,
        "fact_id_links": clean_facts,
        "confidence_grade": row["confidence_grade"],
        "activation_status": row["activation_status"],
        "edges_rewired": edge_n,
    }


def apply_svp_it_strategy_skill(payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.setdefault("skill_rows", [])
    existing = build_skill_rows_by_id(payload)
    if SKILL_ID in existing:
        row = dict(existing[SKILL_ID])
        created = False
    else:
        row = _new_skill_row()
        rows.append(row)
        created = True

    promoted = _promote_row(payload, row, fact_ids=FACT_ID_LINKS)
    return {"created_new_row": created, "promoted": promoted}


def main() -> int:
    ledger_path = default_arsenal_ledger_path(ROOT)
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    before_count = len(payload.get("skill_rows") or [])

    result = apply_svp_it_strategy_skill(payload)
    validate_arsenal_ledger_shape(payload)
    ledger_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    after_count = len(payload.get("skill_rows") or [])
    closeout = {
        "generated_at_utc": _utc_now(),
        "status": "PASS",
        "skill_id": SKILL_ID,
        "fact_id_links": FACT_ID_LINKS,
        "created_new_row": result["created_new_row"],
        "skill_rows_before": before_count,
        "skill_rows_after": after_count,
        **result,
    }
    CLOSEOUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    CLOSEOUT_JSON.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")
    CLOSEOUT_MD.write_text(
        "\n".join(
            [
                "# SVP IT Strategy skill mint (20260527)",
                "",
                f"**STATUS:** PASS",
                f"**skill_id:** `{SKILL_ID}`",
                f"**facts:** {FACT_ID_LINKS}",
                f"**created_new_row:** {result['created_new_row']}",
                "",
                "Closes `jd_inferred_skill_svp_it_strategy` admission gap for Brown & Brown targeting.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"SVP_SKILL_MINT status=PASS skill={SKILL_ID} "
        f"created_new_row={result['created_new_row']} grade={result['promoted']['confidence_grade']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
