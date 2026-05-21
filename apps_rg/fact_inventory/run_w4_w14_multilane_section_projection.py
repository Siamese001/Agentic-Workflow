"""W4/W14 — multilane section projection per senior-role archetype (offline analysis only).

Combines W14b track-weighted traversal (no manifest weight_override) with SRFS section
fact allocation and graph skill allowed_sections. Not runtime generation proof.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from apps_rg.fact_inventory.augmented_skills_graph import (
    SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
    assert_skills_not_broad_ledger_authority,
    load_augmented_skills_graph,
)
from apps_rg.fact_inventory.candidate_fact_ledger import load_master_candidate_fact_ledger
from apps_rg.fact_inventory.commercial_claim_eligibility import (
    CLAIM_ELIGIBLE_MEDIUM_SECTIONS,
    is_claim_eligible_medium,
    registry_fact_entry,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    skill_row_eligible_for_external_claim,
    skill_row_eligible_for_internal_ranking,
)
from apps_rg.fact_inventory.run_w14_senior_role_offline_traversal import (
    GLOBAL_EXCLUDED_SKILL_IDS,
    MANIFEST_PATH,
    PLAN_ID,
    _evaluate_archetype,
    _read_text,
    _skill_rows_by_id,
    _target_role_from_jd,
)
from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS, select_candidate_facts_for_role
from apps_rg.fact_inventory.track_balanced_section_projection import (
    project_competencies_grouped_by_track,
    project_track_balanced_executive_summary,
)
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    build_track_weighted_expansion,
    infer_projection_role_family_key,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "docs/reports/apps_rg/phase2_w4_w14_multilane_section_projection_receipt.json"
OUT_MD = ROOT / "docs/reports/apps_rg/phase2_w4_w14_multilane_section_projection_receipt.md"
PER_ARCHETYPE_DIR = ROOT / "docs/reports/apps_rg/fixtures/senior_roles/section_projection"

SECTIONS: tuple[str, ...] = SECTION_KEYS

NON_EXTERNAL_STATUSES = frozenset(
    {"DRAFT", "INTERNAL_ONLY", "DO_NOT_PROMOTE", "BLOCKED", "USER_CONFIRMED_PENDING_SOURCE"}
)

SECTION_POSTURE: dict[str, str] = {
    "headline": "concise_HIGH_confidence_only",
    "executive_summary": "HIGH_or_human_confirmed_no_auto_MEDIUM",
    "unify_bullets": "unify_lane_HIGH_plus_claim_eligible_MEDIUM",
    "unify_narrative": "unify_lane_HIGH_plus_claim_eligible_MEDIUM",
    "ibm_bullets": "ibm_lane_only_no_unrelated_domain",
    "ibm_narrative": "ibm_lane_only_no_unrelated_domain",
    "competencies": "broader_domain_skills_with_claim_tier_separation",
}

ARCHETYPE_LABELS: dict[str, str] = {
    "aig_carrier_agentic": "insurance carrier agentic transformation",
    "lincoln_insurer_it_ai": "insurer IT strategy / AI enablement",
    "citi_banking_platform_ai": "banking platform responsible AI",
    "brown_brokerage_it": "insurance brokerage IT innovation",
    "anthropic_partner_applied_ai": "partner applied AI architecture",
    "gtm_presales_baseline": "GTM/pre-sales technical accelerators",
    "ai_data_platform_professional_services": "AI/data platform professional services",
}


def _classify_skill_row(row: dict[str, Any]) -> str:
    support = str(row.get("support_level") or "")
    status = str(row.get("activation_status") or "")
    if support in NON_EXTERNAL_STATUSES or status in NON_EXTERNAL_STATUSES:
        return "DRAFT_INTERNAL_ONLY_DO_NOT_PROMOTE"
    if skill_row_eligible_for_external_claim(row):
        if row.get("fact_id_links"):
            return "claim_eligible_evidence_backed"
        return "directional_snippet_only"
    if skill_row_eligible_for_internal_ranking(row):
        return "directional_internal_only"
    return "blocked"


def _facts_for_skill_ids(
    skill_ids: set[str], rows_by_id: dict[str, dict[str, Any]]
) -> set[str]:
    out: set[str] = set()
    for sid in skill_ids:
        row = rows_by_id.get(sid, {})
        for fid in row.get("fact_id_links") or []:
            if str(fid).strip():
                out.add(str(fid))
    return out


def _srfs_fact_ids_by_section(srfs: Any) -> dict[str, list[str]]:
    return {
        sec: [sl.candidate_fact_id for sl in srfs.selected_facts_by_section.get(sec, [])]
        for sec in SECTIONS
    }


def _srfs_fact_detail(srfs: Any, fid: str) -> dict[str, str] | None:
    for sec in SECTIONS:
        for sl in srfs.selected_facts_by_section.get(sec, []) or []:
            if sl.candidate_fact_id == fid:
                return {
                    "confidence": sl.confidence,
                    "verification_status": sl.verification_status,
                    "company_lane": sl.company_lane,
                    "section": sec,
                }
    for sl in srfs.blocked_facts:
        if sl.candidate_fact_id == fid:
            return {
                "confidence": sl.confidence,
                "verification_status": sl.verification_status,
                "company_lane": "",
                "section": "blocked",
            }
    return None


def _policy_violations(
    *,
    section: str,
    srfs_fact_ids: list[str],
    claim_eligible: list[str],
    ledger_rows: dict[str, dict[str, Any]],
) -> list[str]:
    violations: list[str] = []
    for fid in srfs_fact_ids:
        row = ledger_rows.get(fid, {})
        conf = str(row.get("confidence") or "").upper()
        if section in ("headline", "executive_summary") and conf == "MEDIUM":
            violations.append(f"MEDIUM_fact_in_{section}:{fid}")
        if section == "executive_summary" and conf == "MEDIUM" and is_claim_eligible_medium(fid):
            violations.append(f"claim_eligible_MEDIUM_leaked_to_executive_summary:{fid}")
        if section in ("ibm_bullets", "ibm_narrative"):
            company = str(row.get("company") or "").lower()
            if company and "ibm" not in company and "international business machines" not in company:
                violations.append(f"non_ibm_fact_in_{section}:{fid}")
    for fid in claim_eligible:
        if section == "executive_summary" and is_claim_eligible_medium(fid):
            violations.append(f"medium_marked_claim_eligible_in_executive_summary:{fid}")
    return violations


def _skills_for_section(
    *,
    section: str,
    selected_skill_ids: set[str],
    rows_by_id: dict[str, dict[str, Any]],
) -> tuple[list[str], list[str], list[str]]:
    """Return (eligible_skills, blocked_for_section, internal_only)."""
    eligible: list[str] = []
    blocked: list[str] = []
    internal: list[str] = []
    for sid in sorted(selected_skill_ids):
        row = rows_by_id.get(sid, {})
        allowed = set(row.get("allowed_sections") or [])
        tier = _classify_skill_row(row)
        if tier == "DRAFT_INTERNAL_ONLY_DO_NOT_PROMOTE":
            blocked.append(sid)
            continue
        if section not in allowed and section != "competencies":
            blocked.append(sid)
            continue
        if section == "competencies" or section in allowed:
            if tier == "claim_eligible_evidence_backed":
                eligible.append(sid)
            elif tier in ("directional_snippet_only", "directional_internal_only"):
                internal.append(sid)
            else:
                blocked.append(sid)
    return eligible, blocked, internal


def _special_risks(
    slug: str,
    *,
    traversal: dict[str, Any],
    section_cells: dict[str, dict[str, Any]],
    manifest_entry: dict[str, Any],
) -> tuple[list[str], list[str]]:
    over: list[str] = []
    under: list[str] = []
    selected_skills = {
        str(s["skill_id"]) for s in traversal.get("selected_skills_ranked") or [] if s.get("skill_id")
    }
    forbidden = list(manifest_entry.get("forbidden_claims") or [])

    if slug == "aig_carrier_agentic":
        risky = {s for s in selected_skills if "underwriting" in s or "claims" in s or "policy_admin" in s}
        if risky:
            over.append(f"carrier_underwriting_claims_skill_risk:{sorted(risky)}")
        exec_facts = section_cells.get("executive_summary", {}).get("selected_fact_ids") or []
        if not exec_facts:
            under.append("executive_summary_may_undermatch_carrier_HIGH_facts_by_design")

    if slug == "lincoln_insurer_it_ai":
        if "full_svp_it_strategy" in " ".join(forbidden):
            over.append("guardrail:do_not_claim_full_insurer_IT_strategy_ownership_without_facts")

    if slug == "citi_banking_platform_ai":
        payment_skills = {s for s in selected_skills if any(x in s for x in ("payments", "liquidity", "trade", "fraud"))}
        if payment_skills:
            over.append(f"banking_product_ownership_skill_risk:{sorted(payment_skills)}")

    if slug == "brown_brokerage_it":
        if traversal.get("brokerage_evidence_gap_documented"):
            under.append("documented_brokerage_pillar_evidence_gap_no_fabrication")
        if "pillar_insurance_brokerage_distribution" in str(traversal.get("graph_gap_notes")):
            under.append("brokerage_pillar_deferred_use_interop_gtm_only")

    if slug == "anthropic_partner_applied_ai":
        blocked_partner = {
            s
            for s in selected_skills
            if s in ("skill_partner_partner_engineering", "skill_partner_product_feedback_loops")
        }
        if blocked_partner:
            over.append(f"partner_external_skill_should_not_surface:{sorted(blocked_partner)}")
        for pat in ("marketplace", "snowflake", "gsi"):
            hits = [s for s in selected_skills if pat in s.lower()]
            if hits:
                over.append(f"partner_{pat}_exclusive_claim_risk:{hits}")

    if slug == "gtm_presales_baseline":
        if "skill_p2_anchor_major_airline_devops_aws" in selected_skills:
            over.append("airline_anchor_blocked_skill_in_selection")
        if "skill_p2_tech_estimation_sizing_directional" in selected_skills:
            over.append("estimation_sizing_INTERNAL_ONLY_in_selection")
        exec_medium = section_cells.get("executive_summary", {}).get("claim_eligible_facts") or []
        medium_in_exec = [f for f in exec_medium if _srfs_fact_detail_is_medium(f)]
        if medium_in_exec:
            over.append(f"gtm_exec_MEDIUM_leak:{medium_in_exec}")

    if slug == "ai_data_platform_professional_services":
        for sid in (
            "skill_customer_nrr_predictive_analytics_20pct",
            "skill_customer_satisfaction_nps_25pct",
            "skill_partner_product_feedback_loops",
        ):
            if sid in selected_skills:
                over.append(f"services_archetype_excluded_skill:{sid}")

    return over, under


def _srfs_fact_detail_is_medium(fid: str) -> bool:
    return fid.startswith("fact_") and is_claim_eligible_medium(fid)


def _build_section_cell(
    *,
    section: str,
    traversal: dict[str, Any],
    expansion: dict[str, Any],
    srfs: Any,
    rows_by_id: dict[str, dict[str, Any]],
    ledger_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    selected_skill_ids = {
        str(s["skill_id"]) for s in traversal.get("selected_skills_ranked") or [] if s.get("skill_id")
    }
    selected_pillars = [p["pillar_id"] for p in traversal.get("selected_pillars_ranked") or []][:12]

    eligible_skills, blocked_skills, internal_skills = _skills_for_section(
        section=section,
        selected_skill_ids=selected_skill_ids,
        rows_by_id=rows_by_id,
    )

    traversal_facts = set(traversal.get("selected_fact_ids") or [])
    skill_linked_facts = _facts_for_skill_ids(set(eligible_skills), rows_by_id)
    srfs_facts = _srfs_fact_ids_by_section(srfs).get(section, [])

    claim_eligible: list[str] = []
    blocked_facts: list[str] = []
    draft_exclusions: list[str] = []

    for fid in sorted(set(srfs_facts) | traversal_facts | skill_linked_facts):
        row = ledger_rows.get(fid, {})
        conf = str(row.get("confidence") or "").upper()
        detail = _srfs_fact_detail(srfs, fid)
        if conf == "LOW" or (detail and detail.get("verification_status", "").startswith("blocked")):
            blocked_facts.append(fid)
            continue
        if conf == "MEDIUM":
            if section in CLAIM_ELIGIBLE_MEDIUM_SECTIONS and is_claim_eligible_medium(fid):
                if fid in srfs_facts:
                    claim_eligible.append(fid)
            elif section in ("headline", "executive_summary"):
                blocked_facts.append(fid)
                draft_exclusions.append(f"MEDIUM_blocked_from_{section}:{fid}")
            else:
                blocked_facts.append(fid)
        elif conf == "HIGH":
            if fid in srfs_facts or fid in traversal_facts or fid in skill_linked_facts:
                claim_eligible.append(fid)

    for sid in blocked_skills:
        row = rows_by_id.get(sid, {})
        tier = _classify_skill_row(row)
        if tier == "DRAFT_INTERNAL_ONLY_DO_NOT_PROMOTE":
            draft_exclusions.append(sid)

    violations = _policy_violations(
        section=section,
        srfs_fact_ids=srfs_facts,
        claim_eligible=claim_eligible,
        ledger_rows=ledger_rows,
    )
    eligibility = "PASS"
    if violations:
        eligibility = "FAIL"
    elif section == "executive_summary" and not claim_eligible and not srfs_facts:
        eligibility = "PARTIAL"
    elif section == "competencies" and not eligible_skills and not internal_skills:
        eligibility = "PARTIAL"

    allowed_source_candidates = []
    if section in CLAIM_ELIGIBLE_MEDIUM_SECTIONS:
        allowed_source_candidates = [
            fid
            for fid in sorted(skill_linked_facts)
            if is_claim_eligible_medium(fid) and fid not in claim_eligible
        ]

    exec_track_proj = None
    comp_track_proj = None
    if section == "executive_summary":
        exec_track_proj = project_track_balanced_executive_summary(expansion, repo_root=ROOT)
    if section == "competencies":
        comp_track_proj = project_competencies_grouped_by_track(expansion, repo_root=ROOT)

    return {
        "section": section,
        "expected_output_posture": SECTION_POSTURE.get(section, ""),
        "section_eligibility_decision": eligibility,
        "policy_violations": violations,
        "selected_pillars": selected_pillars,
        "selected_skills": eligible_skills[:25],
        "directional_internal_only_skills": internal_skills[:15],
        "blocked_skills": blocked_skills[:15],
        "selected_fact_ids": sorted(set(srfs_facts) | (traversal_facts & set(claim_eligible)) | set(claim_eligible))[:30],
        "claim_eligible_facts": claim_eligible,
        "blocked_facts": sorted(set(blocked_facts)),
        "DRAFT_INTERNAL_ONLY_DO_NOT_PROMOTE_exclusions": draft_exclusions,
        "allowed_source_fact_candidates": allowed_source_candidates[:12],
        "srfs_selected_fact_ids": srfs_facts,
        "track_balanced_exec_projection_present": bool(exec_track_proj),
        "competencies_grouped_by_track_present": bool(comp_track_proj),
        "section_policy_conservative": section in ("headline", "executive_summary"),
    }


def _ledger_index(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(r["candidate_fact_id"]): r
        for r in ledger.get("candidate_facts") or []
        if isinstance(r, dict) and r.get("candidate_fact_id")
    }


def run_w4_w14_multilane_section_projection(*, repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or ROOT
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    taxonomy = yaml.safe_load(
        (root / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml").read_text(encoding="utf-8")
    )
    graph = load_augmented_skills_graph(repo_root=root)
    ledger = load_master_candidate_fact_ledger(repo_root=root)
    ledger_rows = _ledger_index(ledger)
    rows_by_id = _skill_rows_by_id(graph)

    matrix: dict[str, dict[str, Any]] = {}
    overclaim_register: list[dict[str, Any]] = []
    undermatch_register: list[dict[str, Any]] = []
    cells_total = 0
    cells_pass = 0

    traversal_w14b = []
    for entry in manifest.get("archetypes") or []:
        trav = _evaluate_archetype(
            entry=entry,
            graph=graph,
            taxonomy=taxonomy,
            repo_root=root,
            use_manifest_weight_override=False,
        )
        traversal_w14b.append(trav)
        slug = str(entry["slug"])
        jd = _read_text(root, str(entry["jd_path"]))
        brief = _read_text(root, str(entry["brief_path"]))
        target_role = _target_role_from_jd(jd)
        proj_key = infer_projection_role_family_key(
            target_role=target_role,
            jd_text=jd,
            briefing_text=brief,
            taxonomy=taxonomy,
        )
        expansion = build_track_weighted_expansion(
            graph=graph,
            role_family_key=proj_key,
            jd_text=jd,
            briefing_text=brief,
            weight_override=None,
            enforce_hybrid_contract=False,
            min_tracks_with_facts=1,
            bind_c03=False,
            repo_root=root,
        )
        assert_skills_not_broad_ledger_authority(expansion)

        srfs = select_candidate_facts_for_role(
            target_company=f"W4W14-FIXTURE-{slug}",
            target_role=target_role,
            jd_text=jd,
            briefing_text=brief,
            ledger=ledger,
            taxonomy=taxonomy,
            now_slug=f"w4w14_{slug}",
            repo_root=root,
        )

        section_cells: dict[str, dict[str, Any]] = {}
        for section in SECTIONS:
            cell = _build_section_cell(
                section=section,
                traversal=trav,
                expansion=expansion,
                srfs=srfs,
                rows_by_id=rows_by_id,
                ledger_rows=ledger_rows,
            )
            section_cells[section] = cell
            cells_total += 1
            if cell["section_eligibility_decision"] == "PASS":
                cells_pass += 1

        over, under = _special_risks(slug, traversal=trav, section_cells=section_cells, manifest_entry=entry)
        if over:
            overclaim_register.append({"archetype": slug, "risks": over})
        if under:
            undermatch_register.append({"archetype": slug, "risks": under})

        matrix[slug] = {
            "label": ARCHETYPE_LABELS.get(slug, entry.get("label")),
            "traversal_status_w14b": trav.get("status"),
            "projection_role_family_key": proj_key,
            "sections": section_cells,
            "overclaim_risks": over,
            "undermatch_risks": under,
        }

        PER_ARCHETYPE_DIR.mkdir(parents=True, exist_ok=True)
        (PER_ARCHETYPE_DIR / f"{slug}_section_projection.json").write_text(
            json.dumps(matrix[slug], indent=2) + "\n",
            encoding="utf-8",
        )

    w14b_pass = all(str(t.get("status", "")).startswith("PASS") for t in traversal_w14b)
    pass_rate = round(cells_pass / max(cells_total, 1), 4)

    exec_policy_ok = all(
        not any(
            "MEDIUM" in v or "medium" in v
            for v in matrix[s]["sections"]["executive_summary"].get("policy_violations") or []
        )
        for s in matrix
    )

    medium_in_exec_srfs = {}
    for slug, data in matrix.items():
        exec_ids = data["sections"]["executive_summary"].get("srfs_selected_fact_ids") or []
        medium_in_exec_srfs[slug] = [
            fid for fid in exec_ids if str(ledger_rows.get(fid, {}).get("confidence", "")).upper() == "MEDIUM"
        ]

    ibm_scope_ok = all(
        not matrix[s]["sections"]["ibm_bullets"].get("policy_violations")
        and not matrix[s]["sections"]["ibm_narrative"].get("policy_violations")
        for s in matrix
    )

    status = "PASS"
    if not w14b_pass or pass_rate < 1.0 or not exec_policy_ok:
        status = "PARTIAL" if w14b_pass and pass_rate >= 0.9 else "FAIL"

    aggregate: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "STATUS": status,
        "PLAN_ID": PLAN_ID,
        "WAVE": "W4/W14",
        "SCOPE_MATCH": True,
        "FILES_CHANGED": [
            "apps_rg/fact_inventory/run_w4_w14_multilane_section_projection.py",
        ],
        "COMMANDS_RUN": [],
        "ARTIFACTS_WRITTEN": [
            "docs/reports/apps_rg/phase2_w4_w14_multilane_section_projection_receipt.json",
            "docs/reports/apps_rg/phase2_w4_w14_multilane_section_projection_receipt.md",
            "docs/reports/apps_rg/fixtures/senior_roles/section_projection/",
        ],
        "ARCHETYPE_SECTION_MATRIX": matrix,
        "SECTION_PROJECTION_PASS_RATE": pass_rate,
        "SECTION_CELLS_PASS": cells_pass,
        "SECTION_CELLS_TOTAL": cells_total,
        "SELECTED_FACTS_BY_ARCHETYPE_SECTION": {
            slug: {sec: matrix[slug]["sections"][sec].get("selected_fact_ids") for sec in SECTIONS}
            for slug in matrix
        },
        "CLAIM_ELIGIBLE_FACTS_BY_ARCHETYPE_SECTION": {
            slug: {sec: matrix[slug]["sections"][sec].get("claim_eligible_facts") for sec in SECTIONS}
            for slug in matrix
        },
        "BLOCKED_FACTS_BY_ARCHETYPE_SECTION": {
            slug: {sec: matrix[slug]["sections"][sec].get("blocked_facts") for sec in SECTIONS}
            for slug in matrix
        },
        "DRAFT_INTERNAL_ONLY_EXCLUSIONS": {
            slug: {
                sec: matrix[slug]["sections"][sec].get("DRAFT_INTERNAL_ONLY_DO_NOT_PROMOTE_exclusions")
                for sec in SECTIONS
            }
            for slug in matrix
        },
        "EXEC_SUMMARY_POLICY_STATUS": {
            "blocks_MEDIUM_as_designed": exec_policy_ok,
            "MEDIUM_in_srfs_executive_summary_by_archetype": medium_in_exec_srfs,
            "policy_note": "commercial_claim_eligibility excludes executive_summary for MEDIUM facts",
        },
        "COMPETENCIES_POLICY_STATUS": {
            "broader_skills_allowed_with_tier_separation": True,
            "track_grouped_projection_used": True,
        },
        "IBM_SECTION_SCOPE_STATUS": {
            "ibm_lane_scope_ok": ibm_scope_ok,
            "note": "ibm_bullets/ibm_narrative use ibm_only company lane from SRFS",
        },
        "OVERCLAIM_RISK_REGISTER": overclaim_register,
        "UNDERMATCH_RISK_REGISTER": undermatch_register,
        "BROAD_SKILLS_LEDGER_STATUS": "not_used_as_authority",
        "SKILLS_AUTHORITY": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "W14B_INTEGRITY_STATUS": {
            "all_archetypes_pass_without_weight_override": w14b_pass,
            "traversal_by_slug": {t["slug"]: t["status"] for t in traversal_w14b},
        },
        "PROOF_CLASSIFICATION": "offline_section_projection_and_srfs_allocation_not_runtime_proof",
        "EXPLICIT_NON_CLAIMS": [
            "JD_and_briefing_targeting_only_not_proof",
            "no_runtime_section_generation",
            "no_prompt_or_graph_edits",
            "no_auto_promotion_of_MEDIUM_to_executive_summary",
            "broad_skills_ledger_not_authority",
        ],
        "NEXT_RECOMMENDED_WAVE": "W1_human_confirmation_packet_or_W4_runtime_per_lane_minimum",
    }
    return aggregate


def _write_md(agg: dict[str, Any]) -> None:
    lines = [
        "# Phase 2 W4/W14 — Multilane section projection per archetype",
        "",
        f"**STATUS:** {agg['STATUS']}",
        f"**PLAN_ID:** {agg['PLAN_ID']}",
        f"**WAVE:** {agg['WAVE']}",
        f"**SCOPE_MATCH:** {agg['SCOPE_MATCH']}",
        f"**SECTION_PROJECTION_PASS_RATE:** {agg['SECTION_PROJECTION_PASS_RATE']} "
        f"({agg['SECTION_CELLS_PASS']}/{agg['SECTION_CELLS_TOTAL']} cells)",
        f"**PROOF_CLASSIFICATION:** {agg['PROOF_CLASSIFICATION']}",
        "",
        "## Archetype × section summary",
        "",
        "| Archetype | Traversal (W14b) | headline | exec_summary | unify_bullets | competencies |",
        "|-----------|-------------------|----------|--------------|---------------|--------------|",
    ]
    for slug, data in (agg.get("ARCHETYPE_SECTION_MATRIX") or {}).items():
        secs = data.get("sections") or {}
        lines.append(
            f"| `{slug}` | {data.get('traversal_status_w14b')} | "
            f"{secs.get('headline', {}).get('section_eligibility_decision')} | "
            f"{secs.get('executive_summary', {}).get('section_eligibility_decision')} | "
            f"{secs.get('unify_bullets', {}).get('section_eligibility_decision')} | "
            f"{secs.get('competencies', {}).get('section_eligibility_decision')} |"
        )
    lines.extend(
        [
            "",
            "## Policy gates",
            "",
            f"- **EXEC_SUMMARY blocks MEDIUM:** {agg.get('EXEC_SUMMARY_POLICY_STATUS', {}).get('blocks_MEDIUM_as_designed')}",
            f"- **IBM lane scope OK:** {agg.get('IBM_SECTION_SCOPE_STATUS', {}).get('ibm_lane_scope_ok')}",
            f"- **W14b integrity:** {agg.get('W14B_INTEGRITY_STATUS')}",
            "",
            f"**NEXT_RECOMMENDED_WAVE:** {agg.get('NEXT_RECOMMENDED_WAVE')}",
            "",
            "Receipt JSON: [phase2_w4_w14_multilane_section_projection_receipt.json]"
            "(docs/reports/apps_rg/phase2_w4_w14_multilane_section_projection_receipt.json)",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    agg = run_w4_w14_multilane_section_projection()
    try:
        from ops_scripts.apps_rg.l6_benchmarks.receipt_links import enrich_manifest_links  # guardian: allow-layer-violation -- optional manifest link enrichment

        agg = enrich_manifest_links(agg)
    except ImportError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
        pass
    OUT_JSON.write_text(json.dumps(agg, indent=2) + "\n", encoding="utf-8")
    agg["COMMANDS_RUN"] = [
        {
            "command": "python apps_rg/fact_inventory/run_w4_w14_multilane_section_projection.py",
            "exit_code": 0 if agg["STATUS"] == "PASS" else 1,
        }
    ]
    OUT_JSON.write_text(json.dumps(agg, indent=2) + "\n", encoding="utf-8")
    _write_md(agg)
    print(
        json.dumps(
            {
                "STATUS": agg["STATUS"],
                "SECTION_PROJECTION_PASS_RATE": agg["SECTION_PROJECTION_PASS_RATE"],
                "W14B_INTEGRITY": agg["W14B_INTEGRITY_STATUS"],
            },
            indent=2,
        )
    )
    return 0 if agg["STATUS"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
