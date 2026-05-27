"""Brown-relevant DRAFT skill promotions — wave 20260527 (18 skills).

Author-Gate scope: brown_relevant_archive_only (skills-graph-hardening-gap-closure-53576c).
Links resume-archive DRAFT skill_rows to candidate facts; sets ACTIVE_CONFIRMED + human confirmation.

Usage::

    python apps_rg/fact_inventory/apply_draft_skill_promotions_20260527.py
    python apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py
    python apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    BLOCKED_EXTERNAL_CLAIM_POLICIES,
    BLOCKED_SUPPORT_LEVELS,
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
CLOSEOUT_JSON = ROOT / "docs/reports/apps_rg/draft_skill_promotions_brown_wave_closeout.json"
CLOSEOUT_MD = ROOT / "docs/reports/apps_rg/draft_skill_promotions_brown_wave_closeout.md"

HUMAN_CONFIRMED_BY = "Amit Ayer"
WAVE_ID = "draft_skill_triage_brown_wave_20260527"
AUTHOR_GATE_SCOPE = "brown_relevant_archive_only"

# skill_id -> candidate fact_id(s) — Brown & Brown SVP IT Strategy relevance batch
BROWN_WAVE_PROMOTIONS: dict[str, list[str]] = {
    "skill_partner_aws_ecosystem": ["fact_partnerships_gtm_002"],
    "skill_partner_cloud_partner_ecosystem": ["fact_partnerships_gtm_002"],
    "skill_partner_partner_motions": ["fact_partnerships_gtm_001"],
    "skill_partner_pre_sales": ["fact_solutions_001"],
    "skill_partner_workshops": ["fact_solutions_001"],
    "skill_partner_enterprise_negotiations": ["fact_partnerships_gtm_005"],
    "skill_partner_gtm_enablement": ["fact_partnerships_gtm_001"],
    "skill_partner_pnl_oversight": ["fact_partnerships_gtm_001"],
    "skill_revops_sales_forecasting_frameworks": ["fact_revenue_ops_001"],
    "skill_revops_multi_channel_gtm_alignment": ["fact_revenue_ops_001"],
    "skill_commercial_board_level_stakeholder_alignment": ["fact_exec_001"],
    "skill_commercial_gtm_investment_pipeline": ["fact_revenue_ops_001"],
    "skill_p2_gtm_commercial_validation_pilots": ["fact_consulting_001"],
    "skill_p2_gtm_presales_delivery_handoff": ["fact_consulting_002"],
    "skill_p2_tech_demoable_accelerator": ["fact_engineering_platform_006"],
    "skill_p2_tech_adoption_derisking": ["fact_solutions_001"],
    "skill_p2_tech_ibm_cloud_portfolio_anchor": ["fact_solutions_002"],
    "skill_sr_regulated_financial_institutions_fluency": ["fact_sales_accounts_003"],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_skill_id(value: str) -> bool:
    return value.startswith("skill_")


def _reject_draft_promotion_reason(
    row: dict[str, Any] | None,
    fact_ids: list[str],
    *,
    registry: dict[str, dict[str, Any]],
) -> str:
    if row is None:
        return "missing_skill_row"
    sid = str(row.get("skill_id") or "")
    activation = str(row.get("activation_status") or "")
    if activation != "DRAFT":
        return f"unexpected_activation_status:{activation}"
    support = str(row.get("support_level") or "")
    if support in BLOCKED_SUPPORT_LEVELS:
        return f"blocked_support_level:{support}"
    policy = str(row.get("external_claim_policy") or "")
    if policy in BLOCKED_EXTERNAL_CLAIM_POLICIES:
        return f"blocked_external_claim_policy:{policy}"
    if not fact_ids:
        return "missing_fact_ids"
    for fid in fact_ids:
        if fid not in registry:
            return f"unknown_candidate_fact:{fid}"
        if _is_skill_id(fid):
            return "invalid_fact_id_links_skill_id_shape"
    snippets = row.get("source_snippets") or []
    if support == "DIRECT_FROM_RESUME_ARCHIVE" and not snippets:
        return "archive_promotion_requires_source_snippet"
    return ""


def apply_brown_wave_draft_promotions(
    payload: dict[str, Any],
    *,
    human_confirmed_by: str = HUMAN_CONFIRMED_BY,
    human_confirmed_at: str | None = None,
) -> dict[str, Any]:
    ts = human_confirmed_at or _utc_now()
    registry = load_candidate_fact_promotion_registry(repo_root=ROOT)
    rows_by_id = build_skill_rows_by_id(payload)
    promoted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    human_records: list[dict[str, Any]] = []

    for skill_id, fact_ids in BROWN_WAVE_PROMOTIONS.items():
        row = rows_by_id.get(skill_id)
        clean_facts = [str(x).strip() for x in fact_ids if str(x).strip()]
        try:
            assert_no_jd_briefing_as_proof_fact_ids(clean_facts)
        except ValueError as exc:
            rejected.append({"skill_id": skill_id, "reason": str(exc)})
            continue

        reason = _reject_draft_promotion_reason(row, clean_facts, registry=registry)
        if reason:
            rejected.append({"skill_id": skill_id, "reason": reason})
            continue

        record = {
            "human_confirmed_by": human_confirmed_by,
            "human_confirmed_at": ts,
            "source_fact_ids": clean_facts,
            "override_reason": WAVE_ID,
            "author_gate_scope": AUTHOR_GATE_SCOPE,
        }
        row = dict(row)
        row["human_confirmed_archive_promotion"] = record
        row["fact_id_links"] = clean_facts
        row["primary_fact_id"] = clean_facts[0]
        row["activation_status"] = "ACTIVE_CONFIRMED"
        row["user_confirmed"] = True
        row["human_confirmation_required"] = False
        row["draft_skill_promotion_applied_at"] = ts
        row.pop("confidence_override_blocked", None)
        row.pop("confidence_grade_override_attempted", None)
        row.pop("confidence_override_blocked_reason", None)

        resolved = resolve_confidence_grade(
            row, has_fact_link=True, candidate_registry=registry
        )
        row["confidence_grade_derived"] = resolved["derived_grade"]
        row["confidence_grade"] = resolved["effective_grade"]

        _sync_skill_row_to_payload_collections(payload, row)
        edge_n = _rewire_skill_fact_edges(payload, skill_id, clean_facts)
        rows_by_id[skill_id] = row

        promoted.append(
            {
                "skill_id": skill_id,
                "fact_id_links": clean_facts,
                "confidence_grade": row["confidence_grade"],
                "activation_status": row["activation_status"],
                "support_level": row.get("support_level"),
                "edges_rewired": edge_n,
            }
        )
        human_records.append({"skill_id": skill_id, **record})

    gm = payload.setdefault("graph_metadata", {})
    if isinstance(gm, dict):
        gm["draft_skill_promotion_brown_wave"] = {
            "applied_at": ts,
            "human_confirmed_by": human_confirmed_by,
            "author_gate_scope": AUTHOR_GATE_SCOPE,
            "promoted_skill_count": len(promoted),
            "rejected_skill_count": len(rejected),
            "promoted_skill_ids": [p["skill_id"] for p in promoted],
        }

    return {
        "promoted": promoted,
        "rejected": rejected,
        "human_confirmation_records": human_records,
    }


def _render_closeout_md(result: dict[str, Any]) -> str:
    lines = [
        "# DRAFT skill promotions — Brown wave (20260527)",
        "",
        f"**STATUS:** {result.get('status', 'UNKNOWN')}",
        f"**Author-Gate scope:** `{AUTHOR_GATE_SCOPE}`",
        "",
        f"Promoted: **{len(result.get('promoted', []))}** | Rejected: **{len(result.get('rejected', []))}**",
        "",
        "## Promoted skills",
        "",
    ]
    for p in result.get("promoted") or []:
        lines.append(
            f"- `{p['skill_id']}` → {p.get('fact_id_links')} "
            f"(grade={p.get('confidence_grade')}, edges={p.get('edges_rewired')})"
        )
    if result.get("rejected"):
        lines.extend(["", "## Rejected", ""])
        for r in result["rejected"]:
            lines.append(f"- `{r.get('skill_id')}`: {r.get('reason')}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ledger_path = default_arsenal_ledger_path(ROOT)
    before = json.loads(ledger_path.read_text(encoding="utf-8"))
    draft_before = sum(
        1
        for r in before.get("skill_rows") or []
        if isinstance(r, dict) and r.get("activation_status") == "DRAFT"
    )

    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    promo = apply_brown_wave_draft_promotions(payload)
    validate_arsenal_ledger_shape(payload)
    ledger_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    draft_after = sum(
        1
        for r in payload.get("skill_rows") or []
        if isinstance(r, dict) and r.get("activation_status") == "DRAFT"
    )
    active_confirmed_after = sum(
        1
        for r in payload.get("skill_rows") or []
        if isinstance(r, dict) and r.get("activation_status") == "ACTIVE_CONFIRMED"
    )

    status = "PASS" if len(promo["promoted"]) == len(BROWN_WAVE_PROMOTIONS) and not promo["rejected"] else "PARTIAL"
    closeout = {
        "generated_at_utc": _utc_now(),
        "status": status,
        "author_gate_scope": AUTHOR_GATE_SCOPE,
        "draft_count_before": draft_before,
        "draft_count_after": draft_after,
        "active_confirmed_count_after": active_confirmed_after,
        **promo,
    }
    CLOSEOUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    CLOSEOUT_JSON.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")
    CLOSEOUT_MD.write_text(_render_closeout_md(closeout), encoding="utf-8")

    print(
        f"DRAFT_PROMOTION status={status} promoted={len(promo['promoted'])} "
        f"rejected={len(promo['rejected'])} draft {draft_before}->{draft_after}"
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
