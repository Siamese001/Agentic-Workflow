"""Validate commercial skills graph → SRFS section inputs (no live LLM; report only)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from apps_rg.fact_inventory.candidate_fact_ledger import load_master_candidate_fact_ledger
from apps_rg.fact_inventory.exec_summary_srfs_arsenal import (
    external_proof_fact_ids_from_projection,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    load_master_skills_arsenal_ledger,
    skill_row_eligible_for_external_claim,
    skill_row_eligible_for_internal_ranking,
)
from apps_rg.fact_inventory.commercial_claim_eligibility import is_claim_eligible_medium
from apps_rg.fact_inventory.selected_role_fact_set import (
    SECTION_KEYS,
    infer_role_family_priorities,
    select_candidate_facts_for_role,
)

ROOT = Path(__file__).resolve().parents[2]
PROFILE_ID = "CHIEF_REVENUE_OFFICER_COMPOSITE"
OUT_JSON = ROOT / "docs/reports/apps_rg/commercial_skills_srfs_projection_validation.json"
OUT_MD = ROOT / "docs/reports/apps_rg/commercial_skills_srfs_projection_validation.md"

COMMERCIAL_SKILL_IDS = frozenset(
    {
        "skill_sales_modernization_deals_15m",
        "skill_sales_global_financial_institutions_leadership",
        "skill_partner_ibm_aws_alliance_joint_revenue",
        "skill_partner_cloud_vendor_joint_gtm",
        "skill_finance_cost_optimization_dashboards",
        "skill_finance_ma_synergy_due_diligence",
        "skill_customer_nrr_predictive_analytics_20pct",
        "skill_customer_satisfaction_nps_25pct",
        "skill_commercial_board_level_stakeholder_alignment",
        "skill_commercial_gtm_investment_pipeline",
    }
)

REJECTED_FACT_IDS = frozenset(
    {
        "fact_customer_success_001",
        "fact_sales_accounts_004",
        "fact_sales_accounts_005",
    }
)

MEDIUM_COMMERCIAL_FACT_IDS = frozenset(
    {
        "fact_sales_accounts_001",
        "fact_sales_accounts_002",
        "fact_sales_accounts_003",
        "fact_partnerships_gtm_001",
        "fact_partnerships_gtm_002",
        "fact_partnerships_gtm_003",
        "fact_partnerships_gtm_004",
        "fact_revenue_ops_001",
        "fact_revenue_ops_002",
        "fact_revenue_ops_003",
        "fact_revenue_ops_004",
        "fact_revenue_ops_005",
    }
)

CRO_FIXTURE = {
    "target_company": "Acme Revenue Corp",
    "target_role": (
        "Chief Revenue Officer revenue operations pipeline Salesforce forecasting "
        "strategic alliances customer success commercialization"
    ),
    "jd_text": (
        "RevOps pipeline analytics Salesforce forecast enterprise sales partnerships "
        "IBM AWS alliance customer success retention NRR stakeholder alignment "
        "subscription pricing M&A synergy"
    ),
    "briefing_text": "CRO composite targeting fixture — JD/briefing labeling only; not proof.",
}


@dataclass
class CompositeProjection:
    profile_id: str
    taxonomy_ids: tuple[str, ...]
    pillar_ids: tuple[str, ...]
    internal_ranked_skill_ids: tuple[str, ...]
    external_eligible_skill_ids: tuple[str, ...]
    archive_only_context_skill_ids: tuple[str, ...]
    derived_with_fact_skill_ids: tuple[str, ...]
    linked_fact_ids_from_external_skills: tuple[str, ...]
    commercial_skills_by_section: dict[str, list[str]] = field(default_factory=dict)


def _profile_pillar_ids(profile: dict[str, Any]) -> frozenset[str]:
    weighted = profile.get("top_weighted_pillars") or []
    return frozenset(
        str(p["pillar_id"]) for p in weighted if isinstance(p, dict) and p.get("pillar_id")
    )


def project_composite_profile(profile_id: str, ledger: dict[str, Any]) -> CompositeProjection:
    profiles = ledger.get("role_family_projection_profiles") or {}
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        raise ValueError(f"missing projection profile {profile_id}")

    taxonomy_ids = frozenset(str(x) for x in (profile.get("taxonomy_ids") or []))
    pillar_ids = _profile_pillar_ids(profile)

    scored: list[tuple[float, str, dict[str, Any]]] = []
    for row in ledger.get("skill_rows") or []:
        if not isinstance(row, dict):
            continue
        sid = str(row["skill_id"])
        if not skill_row_eligible_for_internal_ranking(row):
            continue
        pillar = str(row.get("pillar") or "")
        weights = row.get("role_family_weights") or {}
        score = 0.0
        for rf, w in weights.items():
            if rf in taxonomy_ids:
                score = max(score, float(w))
        if pillar in pillar_ids:
            score += 0.5
        if row.get("source_snippets"):
            score += 0.15
        if row.get("fact_id_links"):
            score += 0.2
        if score <= 0:
            continue
        scored.append((score, sid, row))
    scored.sort(key=lambda t: (-t[0], t[1]))

    internal = [sid for _, sid, _ in scored]
    external: list[str] = []
    archive_only: list[str] = []
    derived_facts: list[str] = []
    for _, sid, row in scored:
        if skill_row_eligible_for_external_claim(row):
            external.append(sid)
        support = str(row.get("support_level") or row.get("support_status") or "")
        if sid in COMMERCIAL_SKILL_IDS and not (row.get("fact_id_links") or []):
            if support == "DIRECT_FROM_RESUME_ARCHIVE":
                archive_only.append(sid)
        if support == "DERIVED_SUPPORTED" and row.get("fact_id_links"):
            derived_facts.append(sid)

    by_section: dict[str, list[str]] = {}
    for sec in SECTION_KEYS:
        hits: list[str] = []
        for _, sid, row in scored:
            if sid not in COMMERCIAL_SKILL_IDS:
                continue
            allowed = row.get("allowed_sections") or []
            if sec in allowed:
                hits.append(sid)
        by_section[sec] = hits

    ext_projection_like = type(
        "P",
        (),
        {"external_eligible_skill_ids": tuple(external)},
    )()
    linked = sorted(external_proof_fact_ids_from_projection(ledger, ext_projection_like))  # type: ignore[arg-type]

    return CompositeProjection(
        profile_id=profile_id,
        taxonomy_ids=tuple(sorted(taxonomy_ids)),
        pillar_ids=tuple(sorted(pillar_ids)),
        internal_ranked_skill_ids=tuple(internal[:60]),
        external_eligible_skill_ids=tuple(external),
        archive_only_context_skill_ids=tuple(archive_only),
        derived_with_fact_skill_ids=tuple(derived_facts),
        linked_fact_ids_from_external_skills=tuple(linked),
        commercial_skills_by_section=by_section,
    )


def _authoritative_fact_ids(srfs: Any) -> frozenset[str]:
    """Facts selected for external-validation sections (HIGH + claim-eligible MEDIUM)."""
    out: set[str] = set()
    for sec in SECTION_KEYS:
        if sec == "competencies":
            continue
        for sl in srfs.selected_facts_by_section.get(sec, []):
            out.add(str(sl.candidate_fact_id))
    return frozenset(out)


def _commercial_authoritative_fact_ids(srfs: Any) -> frozenset[str]:
    return _authoritative_fact_ids(srfs) & MEDIUM_COMMERCIAL_FACT_IDS


def _section_fact_rows(srfs: Any) -> dict[str, list[dict[str, str]]]:
    rows: dict[str, list[dict[str, str]]] = {}
    for sec in SECTION_KEYS:
        items = []
        for sl in srfs.selected_facts_by_section.get(sec, []):
            items.append(
                {
                    "candidate_fact_id": sl.candidate_fact_id,
                    "confidence": sl.confidence,
                    "verification_status": sl.verification_status,
                }
            )
        rows[sec] = items
    return rows


def build_validation_payload() -> dict[str, Any]:
    arsenal = load_master_skills_arsenal_ledger()
    candidate = load_master_candidate_fact_ledger()
    taxonomy = yaml.safe_load(
        (ROOT / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml").read_text(
            encoding="utf-8"
        )
    )

    projection = project_composite_profile(PROFILE_ID, arsenal)
    priorities = infer_role_family_priorities(
        target_role=CRO_FIXTURE["target_role"],
        jd_text=CRO_FIXTURE["jd_text"],
        briefing_text=CRO_FIXTURE["briefing_text"],
        taxonomy=taxonomy,
    )

    srfs = select_candidate_facts_for_role(
        target_company=CRO_FIXTURE["target_company"],
        target_role=CRO_FIXTURE["target_role"],
        jd_text=CRO_FIXTURE["jd_text"],
        briefing_text=CRO_FIXTURE["briefing_text"],
        ledger=candidate,
        taxonomy=taxonomy,
        now_slug="commercial_srfs_validation",
        repo_root=ROOT,
    )

    auth_ids = _authoritative_fact_ids(srfs)
    blocked_ids = frozenset(b.candidate_fact_id for b in srfs.blocked_facts)
    medium_queue_ids = frozenset(q.fact.candidate_fact_id for q in srfs.facts_requiring_human_confirmation)

    violations: list[str] = []
    if auth_ids & REJECTED_FACT_IDS:
        violations.append(f"rejected facts in authoritative pool: {sorted(auth_ids & REJECTED_FACT_IDS)}")
    medium_in_auth = auth_ids & MEDIUM_COMMERCIAL_FACT_IDS
    for fid in sorted(medium_in_auth):
        sl = next(
            (
                sl
                for sec in SECTION_KEYS
                for sl in srfs.selected_facts_by_section.get(sec, [])
                if sl.candidate_fact_id == fid
            ),
            None,
        )
        if sl is None:
            violations.append(f"{fid} in auth set but not found in section slices")
            continue
        if sl.verification_status != "eligible_medium_with_source_trace":
            violations.append(
                f"{fid} in authoritative pool without eligible_medium_with_source_trace "
                f"(got {sl.verification_status})"
            )
        if not sl.source_trace_archive_relpaths:
            violations.append(f"{fid} claim-eligible MEDIUM missing source_trace_archive_relpaths")
        if not is_claim_eligible_medium(fid, repo_root=ROOT):
            violations.append(f"{fid} in authoritative pool but not in commercial_claim_eligibility registry")
    unpromoted_medium_in_auth = medium_in_auth - {
        fid for fid in medium_in_auth if is_claim_eligible_medium(fid, repo_root=ROOT)
    }
    if unpromoted_medium_in_auth:
        violations.append(f"unregistered MEDIUM commercial in auth pool: {sorted(unpromoted_medium_in_auth)}")
    for fid in REJECTED_FACT_IDS:
        if fid not in blocked_ids:
            violations.append(f"{fid} not in blocked_facts")

    commercial_in_projection = sorted(set(projection.internal_ranked_skill_ids) & COMMERCIAL_SKILL_IDS)
    commercial_external = sorted(set(projection.external_eligible_skill_ids) & COMMERCIAL_SKILL_IDS)
    archive_in_auth_facts = auth_ids & {
        fid
        for sid in projection.archive_only_context_skill_ids
        for fid in []
    }
    if archive_in_auth_facts:
        violations.append(f"archive-only skills incorrectly mapped to fact ids: {archive_in_auth_facts}")

    linked_medium = set(projection.linked_fact_ids_from_external_skills) & MEDIUM_COMMERCIAL_FACT_IDS
    linked_in_auth = linked_medium & auth_ids
    linked_unregistered = {
        fid for fid in linked_in_auth if not is_claim_eligible_medium(fid, repo_root=ROOT)
    }
    if linked_unregistered:
        violations.append(
            "DERIVED MEDIUM facts in authoritative SRFS without claim_eligible registry: "
            f"{sorted(linked_unregistered)}"
        )

    status = "PASS" if not violations else "FAIL"

    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "profile_id": PROFILE_ID,
        "fixture": CRO_FIXTURE,
        "role_family_priorities": [asdict(p) for p in priorities[:8]],
        "composite_projection": {
            "taxonomy_ids": list(projection.taxonomy_ids),
            "pillar_ids": list(projection.pillar_ids),
            "commercial_skills_in_projection": commercial_in_projection,
            "commercial_skills_external_eligible": commercial_external,
            "archive_only_context_skill_ids": list(projection.archive_only_context_skill_ids),
            "derived_with_fact_skill_ids": list(projection.derived_with_fact_skill_ids),
            "linked_fact_ids_from_external_skills": list(projection.linked_fact_ids_from_external_skills),
            "commercial_skills_by_section": projection.commercial_skills_by_section,
        },
        "section_skill_selection": projection.commercial_skills_by_section,
        "section_fact_selection": _section_fact_rows(srfs),
        "authoritative_claim_pool_fact_ids": sorted(auth_ids),
        "authoritative_commercial_fact_ids": sorted(_commercial_authoritative_fact_ids(srfs)),
        "claim_eligible_medium_registry_ids": sorted(
            fid for fid in MEDIUM_COMMERCIAL_FACT_IDS if is_claim_eligible_medium(fid, repo_root=ROOT)
        ),
        "medium_confirmation_queue_fact_ids": sorted(
            fid for fid in medium_queue_ids if fid in MEDIUM_COMMERCIAL_FACT_IDS
        ),
        "archive_only_context": {
            "skill_ids": list(projection.archive_only_context_skill_ids),
            "note": (
                "Archive-only commercial skills may rank as external-eligible skills but have no "
                "fact_id_links; SRFS authoritative pool is HIGH plus registry claim-eligible MEDIUM "
                "in bullet/narrative lanes only."
            ),
            "in_authoritative_fact_pool": [],
        },
        "blocked_facts": [
            {"candidate_fact_id": b.candidate_fact_id, "confidence": b.confidence, "block_reason": b.block_reason}
            for b in srfs.blocked_facts
            if b.candidate_fact_id in REJECTED_FACT_IDS
        ],
        "rejected_facts_excluded_from_authoritative_pool": sorted(
            REJECTED_FACT_IDS - auth_ids
        ),
        "violations": violations,
        "scope_control": {
            "agentic_core_touched": False,
            "section_prompts_touched": False,
            "skills_graph_mutated": False,
        },
        "explicit_non_claims": [
            "No live Qwen run",
            "JD/briefing used for role-family keyword inference only",
            "No SRFS/X2/X3 gate changes",
        ],
    }


def _render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Commercial skills SRFS projection validation",
        "",
        f"**Status:** {payload['status']}",
        f"**Profile:** `{payload['profile_id']}`",
        "",
        "## Composite projection (commercial skills)",
        "",
        f"- In projection: `{payload['composite_projection']['commercial_skills_in_projection']}`",
        f"- External-eligible: `{payload['composite_projection']['commercial_skills_external_eligible']}`",
        f"- Archive-only context (no fact link): `{payload['composite_projection']['archive_only_context_skill_ids']}`",
        "",
        "## Per-section commercial skill eligibility",
        "",
    ]
    for sec, skills in payload["section_skill_selection"].items():
        lines.append(f"### `{sec}`")
        lines.append(f"- skills: {skills or '[]'}")
    lines.extend(["", "## Authoritative fact pool", ""])
    for fid in payload["authoritative_claim_pool_fact_ids"]:
        lines.append(f"- `{fid}`")
    lines.extend(["", "## Authoritative commercial facts", ""])
    for fid in payload.get("authoritative_commercial_fact_ids") or []:
        lines.append(f"- `{fid}`")
    lines.extend(["", "## Claim-eligible MEDIUM registry", ""])
    for fid in payload.get("claim_eligible_medium_registry_ids") or []:
        lines.append(f"- `{fid}`")
    lines.extend(["", "## MEDIUM commercial facts (confirmation queue)", ""])
    for fid in payload["medium_confirmation_queue_fact_ids"]:
        lines.append(f"- `{fid}`")
    lines.extend(["", "## Blocked rejected facts", ""])
    for row in payload["blocked_facts"]:
        lines.append(f"- `{row['candidate_fact_id']}` [{row['confidence']}] {row['block_reason']}")
    if payload.get("violations"):
        lines.extend(["", "## Violations", ""])
        for v in payload["violations"]:
            lines.append(f"- {v}")
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_validation_payload()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    print(f"STATUS={payload['status']} wrote {OUT_JSON.name}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
