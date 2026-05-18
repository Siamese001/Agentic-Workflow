"""Executive-summary skill/fact projection from arsenal ledger (graph-aware; no live generation)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    skill_row_eligible_for_external_claim,
    skill_row_eligible_for_internal_ranking,
)

ROLE_FAMILY_PROFILE_KEYS = frozenset(
    {
        "SVP_ENGINEERING_AI_PLATFORM",
        "AI_FINANCIAL_SERVICES",
        "ANTHROPIC_PARTNERSHIPS_APPLIED_AI",
        "FIELD_CTO",
        "CHIEF_AI_OFFICER",
        "STRATEGIC_FINANCE",
        "QUANT_TRADING",
        "GOVERNANCE_RISK",
    }
)

SVP_PILLAR_IDS = frozenset(
    {
        "pillar_agentic_ai_platforms",
        "pillar_cloud_data_aws",
        "pillar_executive_leadership",
        "pillar_revenue_commercialization",
        "pillar_regulatory_governance",
        "pillar_actuarial_foundation",
    }
)

AI_FIN_SERV_PILLAR_IDS = frozenset(
    {
        "pillar_regulatory_governance",
        "pillar_enterprise_risk_controls",
        "pillar_risk_management",
        "pillar_actuarial_foundation",
        "pillar_greeks_hedging",
        "pillar_derivatives_structured",
        "pillar_agentic_ai_platforms",
        "pillar_revenue_commercialization",
    }
)

ANTHROPIC_PARTNERSHIPS_PILLAR_IDS = frozenset(
    {
        "pillar_partner_gtm_alliances",
        "pillar_cosell_partner_engineering",
        "pillar_presales_solutioning",
        "pillar_cloud_data_aws",
        "pillar_agentic_ai_platforms",
        "pillar_customer_stakeholder",
        "pillar_revenue_commercialization",
    }
)

ACTUARIAL_PILLAR_ID = "pillar_actuarial_foundation"

GOVERNANCE_RISK_PILLAR_IDS = frozenset(
    {
        "pillar_regulatory_governance",
        "pillar_enterprise_risk_controls",
        "pillar_risk_management",
    }
)

PARTNER_GTM_SKILL_PREFIXES = ("skill_partner_",)

# Capability-domain emphasis (primary taxonomy — not source-doc buckets).
PROFILE_DOMAIN_HIGH: dict[str, frozenset[str]] = {
    "SVP_ENGINEERING_AI_PLATFORM": frozenset(
        {
            "domain_agentic_systems_architecture",
            "domain_routing_triage_workflow",
            "domain_orchestration_managed_workflows",
            "domain_context_engineering_grounding",
            "domain_runtime_gates_exit",
            "domain_security_governance_compliance",
            "domain_productization_enterprise_adoption",
            "domain_replay_observability_audit",
            "domain_execution_tool_sandbox",
            "domain_learning_calibration",
            "domain_hitl_escalation",
        }
    ),
    "CHIEF_AI_OFFICER": frozenset(
        {
            "domain_agentic_systems_architecture",
            "domain_security_governance_compliance",
            "domain_runtime_gates_exit",
            "domain_learning_calibration",
            "domain_productization_enterprise_adoption",
            "domain_routing_triage_workflow",
            "domain_context_engineering_grounding",
            "domain_hitl_escalation",
            "domain_replay_observability_audit",
        }
    ),
    "AI_FINANCIAL_SERVICES": frozenset(
        {
            "domain_security_governance_compliance",
            "domain_context_engineering_grounding",
            "domain_runtime_gates_exit",
            "domain_replay_observability_audit",
            "domain_execution_tool_sandbox",
            "domain_hitl_escalation",
            "domain_agentic_systems_architecture",
            "domain_productization_enterprise_adoption",
        }
    ),
    "ANTHROPIC_PARTNERSHIPS_APPLIED_AI": frozenset(
        {
            "domain_productization_enterprise_adoption",
            "domain_hitl_escalation",
            "domain_context_engineering_grounding",
            "domain_security_governance_compliance",
            "domain_agentic_systems_architecture",
            "domain_prompt_assembly_boundaries",
        }
    ),
    "FIELD_CTO": frozenset(
        {
            "domain_agentic_systems_architecture",
            "domain_context_engineering_grounding",
            "domain_prompt_assembly_boundaries",
            "domain_execution_tool_sandbox",
            "domain_productization_enterprise_adoption",
            "domain_runtime_gates_exit",
            "domain_replay_observability_audit",
            "domain_security_governance_compliance",
        }
    ),
}


@dataclass(frozen=True)
class ExecutiveSummaryArsenalProjection:
    role_family_key: str
    selected_pillar_ids: tuple[str, ...]
    internal_ranked_skill_ids: tuple[str, ...]
    external_eligible_skill_ids: tuple[str, ...]
    linked_fact_ids: tuple[str, ...]
    actuarial_differentiator_included: bool
    partner_gtm_included: bool
    governance_risk_included: bool
    notes: tuple[str, ...] = field(default_factory=tuple)
    identity_node: str = "identity_amit_ayer_governed_ai_platform_leader"
    selected_epoch_nodes: tuple[str, ...] = field(default_factory=tuple)
    selected_pillar_nodes: tuple[str, ...] = field(default_factory=tuple)
    selected_domain_nodes: tuple[str, ...] = field(default_factory=tuple)
    blocked_or_pending_skill_ids: tuple[str, ...] = field(default_factory=tuple)
    section_projection_notes: tuple[str, ...] = field(default_factory=tuple)
    external_claim_policy_summary: tuple[str, ...] = field(default_factory=tuple)
    ats_keyword_candidates: tuple[str, ...] = field(default_factory=tuple)
    achievement_framing_candidates: tuple[str, ...] = field(default_factory=tuple)
    narrative_synthesis_candidates: tuple[str, ...] = field(default_factory=tuple)
    claim_verification_summary: tuple[str, ...] = field(default_factory=tuple)


def _profile_pillar_ids(role_family_key: str, ledger: dict[str, Any]) -> list[str]:
    profiles = ledger.get("role_family_projection_profiles") or {}
    profile = profiles.get(role_family_key)
    if not isinstance(profile, dict):
        return []
    weighted = profile.get("top_weighted_pillars") or []
    return [str(p["pillar_id"]) for p in weighted if isinstance(p, dict) and p.get("pillar_id")]


def _row_score(
    row: dict[str, Any],
    taxonomy_ids: frozenset[str],
    pillar_ids: frozenset[str],
    domain_high: frozenset[str],
) -> float:
    weights = row.get("role_family_weights") or {}
    score = 0.0
    for rf, w in weights.items():
        if rf in taxonomy_ids:
            score = max(score, float(w))
    pillar = str(row.get("pillar") or "")
    if pillar in pillar_ids:
        score += 0.5
    domain_id = str(row.get("domain_id") or "")
    if domain_id in domain_high:
        score += 0.85
    if row.get("source_snippets"):
        score += 0.2
    if row.get("fact_id_links"):
        score += 0.15
    sections = row.get("allowed_sections") or []
    if "executive_summary" in sections:
        score += 0.25
    return score


def _collect_graph_candidates(
    scored: list[tuple[float, str, dict[str, Any]]],
) -> tuple[list[str], list[str], list[str]]:
    epochs: list[str] = []
    pillars: list[str] = []
    domains: list[str] = []
    for _, _, row in scored[:40]:
        ep = str(row.get("career_epoch") or "")
        if ep and ep not in epochs:
            epochs.append(ep)
        pil = str(row.get("pillar") or "")
        if pil and pil not in pillars:
            pillars.append(pil)
        dom = str(row.get("domain_id") or "")
        if dom and dom not in domains:
            domains.append(dom)
    return epochs, pillars, domains


def project_executive_summary_arsenal(
    role_family_key: str,
    *,
    ledger: dict[str, Any],
) -> ExecutiveSummaryArsenalProjection:
    if role_family_key not in ROLE_FAMILY_PROFILE_KEYS:
        raise ValueError(f"unknown role_family_key: {role_family_key}")

    profiles = ledger.get("role_family_projection_profiles") or {}
    profile = profiles.get(role_family_key) or {}
    taxonomy_ids = frozenset(str(x) for x in (profile.get("taxonomy_ids") or []))
    profile_pillars = frozenset(_profile_pillar_ids(role_family_key, ledger))
    domain_high = PROFILE_DOMAIN_HIGH.get(role_family_key, frozenset())

    if role_family_key == "SVP_ENGINEERING_AI_PLATFORM":
        pillar_focus = SVP_PILLAR_IDS | profile_pillars
    elif role_family_key == "AI_FINANCIAL_SERVICES":
        pillar_focus = AI_FIN_SERV_PILLAR_IDS | profile_pillars
    elif role_family_key == "ANTHROPIC_PARTNERSHIPS_APPLIED_AI":
        pillar_focus = ANTHROPIC_PARTNERSHIPS_PILLAR_IDS | profile_pillars
    else:
        pillar_focus = profile_pillars

    scored: list[tuple[float, str, dict[str, Any]]] = []
    blocked_pending: list[str] = []
    ats_kw: list[str] = []
    achieve: list[str] = []
    narrative: list[str] = []
    verify: list[str] = []

    for row in ledger.get("skill_rows") or []:
        if not isinstance(row, dict):
            continue
        sid = str(row["skill_id"])
        if not skill_row_eligible_for_internal_ranking(row):
            continue
        if not skill_row_eligible_for_external_claim(row):
            blocked_pending.append(sid)
        pillar = str(row.get("pillar") or "")
        domain_id = str(row.get("domain_id") or "")
        if (
            pillar not in pillar_focus
            and domain_id not in domain_high
            and not (row.get("role_family_weights") or {}).keys() & taxonomy_ids
        ):
            continue
        score = _row_score(row, taxonomy_ids, pillar_focus, domain_high)
        if score <= 0:
            continue
        scored.append((score, sid, row))
        for kw in row.get("ats_keywords") or []:
            if kw not in ats_kw:
                ats_kw.append(str(kw))
        ag = row.get("achievement_framing_guidance")
        if ag and ag not in achieve:
            achieve.append(str(ag))
        ng = row.get("narrative_synthesis_guidance")
        if ng and ng not in narrative:
            narrative.append(str(ng))
        cv = row.get("claim_verification_policy")
        if cv:
            verify.append(f"{sid}: {cv}")

    scored.sort(key=lambda t: (-t[0], t[1]))
    internal_ids = [sid for _, sid, _ in scored]
    external_ids = [sid for _, sid, row in scored if skill_row_eligible_for_external_claim(row)]

    fact_ids: list[str] = []
    for _, _, row in scored:
        if row["skill_id"] not in external_ids:
            continue
        for fid in row.get("fact_id_links") or []:
            fs = str(fid)
            if fs not in fact_ids and not fs.startswith("skill_"):
                fact_ids.append(fs)

    actuarial_ranked = [
        sid for _, sid, row in scored if str(row.get("pillar")) == ACTUARIAL_PILLAR_ID
    ]
    actuarial_diff = bool(actuarial_ranked)
    if role_family_key == "SVP_ENGINEERING_AI_PLATFORM":
        actuarial_diff = actuarial_diff and ACTUARIAL_PILLAR_ID in pillar_focus

    partner_gtm = any(sid.startswith(PARTNER_GTM_SKILL_PREFIXES) for sid in internal_ids)
    gov_risk = any(
        str(row.get("pillar") or "") in GOVERNANCE_RISK_PILLAR_IDS
        or str(row.get("skill_id") or "").startswith("skill_risk_")
        or str(row.get("domain_id") or "").startswith("domain_security")
        or str(row.get("domain_id") or "").startswith("domain_runtime_gates")
        for _, _, row in scored
    )

    epochs, pillar_nodes, domain_nodes = _collect_graph_candidates(scored)

    policies = ledger.get("external_claim_policies") or {}
    policy_summary = tuple(
        f"{pid}: {pol.get('enforcement', '')}" for pid, pol in policies.items() if isinstance(pol, dict)
    )[:14]

    notes: list[str] = [
        "Projection is arsenal-layer ranking only; live executive_summary generation was not run.",
        "Graph-aware projection uses capability-domain taxonomy; source concepts are metadata only.",
    ]
    if role_family_key == "SVP_ENGINEERING_AI_PLATFORM":
        notes.append("Actuarial foundation is a differentiator pillar, not the dominant theme.")
    if external_ids != internal_ids:
        notes.append(
            f"{len(internal_ids) - len(external_ids)} skill(s) are internal-ranking only "
            "(pending source, repo portfolio, weak evidence, or blocked)."
        )

    section_notes = (
        f"Top domains for {role_family_key}: "
        + ", ".join(domain_nodes[:8])
        if domain_nodes
        else f"Pillar focus for {role_family_key}"
    )

    return ExecutiveSummaryArsenalProjection(
        role_family_key=role_family_key,
        selected_pillar_ids=tuple(sorted(pillar_focus)),
        internal_ranked_skill_ids=tuple(internal_ids),
        external_eligible_skill_ids=tuple(external_ids),
        linked_fact_ids=tuple(fact_ids),
        actuarial_differentiator_included=actuarial_diff,
        partner_gtm_included=partner_gtm,
        governance_risk_included=gov_risk,
        notes=tuple(notes),
        selected_epoch_nodes=tuple(epochs),
        selected_pillar_nodes=tuple(pillar_nodes),
        selected_domain_nodes=tuple(domain_nodes),
        blocked_or_pending_skill_ids=tuple(blocked_pending),
        section_projection_notes=(section_notes,),
        external_claim_policy_summary=policy_summary,
        ats_keyword_candidates=tuple(ats_kw[:30]),
        achievement_framing_candidates=tuple(achieve[:20]),
        narrative_synthesis_candidates=tuple(narrative[:20]),
        claim_verification_summary=tuple(verify[:25]),
    )
