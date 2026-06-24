"""C0.1 — section retrieval plan (targets only, no retrieval)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_JD_KEYWORD_PATTERN = re.compile(
    r"\b(required|responsibilities|you will|qualifications|skills|requirements|about the role)\b",
    re.IGNORECASE,
)
_JD_EXCERPT_MAX = 300
_JD_ROLE_AXIS_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "partner_motions",
        re.compile(r"\b(partner(ship(s)?|s)?|alliance|alliances|ecosystem)\b", re.IGNORECASE),
    ),
    (
        "partner_gtm",
        re.compile(r"\b(GTM|go[- ]?to[- ]?market|marketplace|channel)\b", re.IGNORECASE),
    ),
    (
        "co_sell",
        re.compile(r"\b(co[- ]?sell|cosell|joint selling|joint revenue)\b", re.IGNORECASE),
    ),
    (
        "hyperscaler_alliance",
        re.compile(r"\b(hyperscaler|AWS|Azure|GCP|Google Cloud|cloud partner)\b", re.IGNORECASE),
    ),
    (
        "systems_integrator_enablement",
        re.compile(
            r"\b(system integrator|systems integrator|GSI|GSIs|global integrator|consulting partner)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "applied_ai_architecture",
        re.compile(
            r"\b(applied AI|generative AI|genAI|LLM|Claude|agentic|AI architecture|solution architecture)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "deployment_adoption",
        re.compile(r"\b(deployment|deploy|adoption|enablement|production|rollout)\b", re.IGNORECASE),
    ),
    (
        "joint_solution",
        re.compile(r"\b(joint solution|reference architecture|integration|integrated solution)\b", re.IGNORECASE),
    ),
)


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


def _extract_jd_role_axes(jd_text: str) -> list[str]:
    """Return JD-derived routing axes only; the JD remains forbidden as proof."""
    text = (jd_text or "").strip()
    if not text:
        return []
    return [axis for axis, pattern in _JD_ROLE_AXIS_PATTERNS if pattern.search(text)]

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

_PROFILE_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "domain_contract"
    / "section_retrieval_profile.yaml"
)


def _c01_plan_key(section_id: str) -> str:
    if section_id in _SECTION_PLAN:
        return section_id
    return _C01_SECTION_ALIASES.get(section_id, section_id)


def _section_retrieval_profile_row(section_id: str) -> dict[str, Any]:
    """Read the C0.2 retrieval profile row used by the same section, if present."""
    if not _PROFILE_PATH.is_file():
        return {}
    import yaml

    doc = yaml.safe_load(_PROFILE_PATH.read_text(encoding="utf-8")) or {}
    aliases = doc.get("section_id_aliases") or {}
    canonical = str(aliases.get(section_id) or section_id) if isinstance(aliases, dict) else section_id
    for row in doc.get("sections") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("section_id") or "") in (section_id, canonical):
            return dict(row)
    return {}


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
    profile_row = _section_retrieval_profile_row(section_id)
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
    jd_role_axes = _extract_jd_role_axes(jd_text or "")
    if jd_role_axes:
        targets["jd_role_axis_targets"] = jd_role_axes
    return {
        "schema_version": "c01_retrieval_plan_v1",
        "section_id": section_id,
        "target_role": target_role,
        "role_family_key": role_family_key,
        "jd_constraints_present": bool(jd_constraints) or bool(jd_role_axes),
        "jd_constraints": dict(jd_constraints or {}),
        "jd_role_axes": jd_role_axes,
        "jd_text_excerpt": jd_excerpt,
        "route_ref": route_ref,
        "retrieval_targets": targets,
        "retrieval_profile_ref": str(
            profile_row.get("retrieval_profile_id") or f"{_PROFILE_PATH.as_posix()}#{section_id}"
        ),
        "retrieval_profile_source": _PROFILE_PATH.as_posix(),
        "retrieval_profile_query_fields": list(profile_row.get("query_fields") or []),
        "retrieval_profile_fallback_queries": list(profile_row.get("fallback_queries") or []),
        "jd_as_proof": False,
        "generic_docs_as_truth": False,
    }


__all__ = ["build_c01_retrieval_plan"]
