"""C0.1 — section retrieval plan (targets only, no retrieval)."""

from __future__ import annotations

import re
from typing import Any

_JD_KEYWORD_PATTERN = re.compile(
    r"\b(required|responsibilities|you will|qualifications|skills|requirements|about the role)\b",
    re.IGNORECASE,
)
_JD_EXCERPT_MAX = 300


def _smart_jd_excerpt(jd_text: str) -> str:
    """Return a content-anchored excerpt of at most _JD_EXCERPT_MAX chars.

    Scans for common structural markers (requirements, responsibilities, etc.)
    and starts the excerpt there. Falls back to [:240] when no marker is found.
    """
    text = (jd_text or "").strip()
    if len(text) <= _JD_EXCERPT_MAX:
        return text
    match = _JD_KEYWORD_PATTERN.search(text)
    if match:
        return text[match.start() : match.start() + _JD_EXCERPT_MAX]
    return text[:240]

_ROLE_FAMILY_PLAN_EXTRAS: dict[str, dict[str, list[str]]] = {
    "INSURANCE_CARRIER_TRANSFORMATION": {
        "primary_targets": [
            "underwriting_claims_ops_facts",
            "agentic_platform_governance_facts",
            "insurance_carrier_transformation",
        ],
        "secondary_targets": ["actuarial_risk_lineage", "process_reengineering_metrics"],
    },
    "PARTNER_APPLIED_AI_ARCHITECTURE": {
        "primary_targets": ["partner_solution_architecture", "systems_integrator_enablement"],
        "secondary_targets": ["reference_architecture", "prototype_to_production"],
    },
    "SVP_ENGINEERING_AI_PLATFORM": {
        "primary_targets": ["platform_engineering", "governed_agentic_runtime"],
        "secondary_targets": ["cloud_ml_delivery"],
    },
    "INSURER_IT_AI_ENABLEMENT": {
        "primary_targets": [
            "enterprise_architecture_standards",
            "it_strategy_innovation_facts",
            "data_ai_enablement",
        ],
        "secondary_targets": ["portfolio_governance", "modernization_roadmap"],
    },
    "INSURANCE_BROKERAGE_IT_INNOVATION": {
        "primary_targets": [
            "brokerage_distribution_innovation",
            "interoperability_integration_facts",
            "it_strategy_innovation_facts",
        ],
        "secondary_targets": ["innovation_labs_pilots", "enterprise_architecture_alignment"],
    },
}

_SECTION_PLAN: dict[str, dict[str, Any]] = {
    "headline": {
        "primary_targets": ["strongest_positioning_facts", "role_family_fit"],
        "secondary_targets": ["metric_highlights"],
    },
    "executive_summary": {
        "primary_targets": [
            "commercial_outcomes",
            "platform_governance",
            "executive_scope",
        ],
        "secondary_targets": ["career_capstone", "cross_domain_leadership"],
    },
    "competencies": {
        "primary_targets": ["skill_clusters", "capability_tags", "pillar_alignment"],
        "secondary_targets": ["metric_backed_capabilities"],
    },
    "bullets": {
        "primary_targets": ["employer_role_facts", "quantified_outcomes"],
        "secondary_targets": ["technology_delivery"],
    },
    "narrative": {
        "primary_targets": ["career_phase_facts", "capstone_narrative_atoms"],
        "secondary_targets": ["lineage_support"],
    },
}

# Lane CLI ids → canonical C0.1 plan keys (phase 2 bullets, phase 3 narratives).
_C01_SECTION_ALIASES: dict[str, str] = {
    "unify_bullets": "bullets",
    "ibm_bullets": "bullets",
    "unify_narrative": "narrative",
    "ibm_narrative": "narrative",
}


def _c01_plan_key(section_id: str) -> str:
    if section_id in _SECTION_PLAN:
        return section_id
    return _C01_SECTION_ALIASES.get(section_id, section_id)


def build_c01_retrieval_plan(
    *,
    section_id: str,
    target_role: str = "",
    jd_constraints: dict[str, Any] | None = None,
    route_ref: str = "",
    role_family_key: str = "",
    jd_text: str = "",
) -> dict[str, Any]:
    """C0.1 output: what to retrieve for this section (not proof)."""
    plan_key = _c01_plan_key(section_id)
    base = dict(_SECTION_PLAN.get(plan_key) or _SECTION_PLAN["executive_summary"])
    targets = {
        "primary_targets": list(base.get("primary_targets") or []),
        "secondary_targets": list(base.get("secondary_targets") or []),
    }
    extras = _ROLE_FAMILY_PLAN_EXTRAS.get(role_family_key) or {}
    for key in ("primary_targets", "secondary_targets"):
        merged = list(targets.get(key) or [])
        for item in extras.get(key) or []:
            if item not in merged:
                merged.append(item)
        targets[key] = merged
    jd_excerpt = _smart_jd_excerpt(jd_text or "")
    return {
        "schema_version": "c01_retrieval_plan_v1",
        "section_id": section_id,
        "target_role": target_role,
        "role_family_key": role_family_key,
        "jd_constraints_present": bool(jd_constraints),
        "jd_text_excerpt": jd_excerpt,
        "route_ref": route_ref,
        "retrieval_targets": targets,
        "jd_as_proof": False,
        "generic_docs_as_truth": False,
    }


__all__ = ["build_c01_retrieval_plan"]
