"""Reasoning-intensity policy for apps_lic LinkedIn outreach.

The policy is app-owned and deterministic. It selects control knobs for the
canonical spine; it does not authorize routing, evidence claims, sending, or
Exit outcomes.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Mapping


POLICY_REF = "apps_lic.policy.reasoning_intensity.v1"

SC_0 = "SC-0"
SC_1 = "SC-1"
SC_2 = "SC-2"
SC_3 = "SC-3"

R0_MINIMAL = "R0_MINIMAL"
R1_STANDARD = "R1_STANDARD"
R2_DELIBERATE = "R2_DELIBERATE"
R3_STRICT = "R3_STRICT"

JUDGE_SCHEMA_POLICY_NO_SEND = "deterministic_schema_policy_no_send_judge"
JUDGE_LINKEDIN_TONE = "linkedin_tone_channel_quality_judge"
JUDGE_EVIDENCE_SUPPORT = "evidence_claim_support_judge"
JUDGE_SAFETY_NO_FABRICATION = "safety_no_fabrication_no_send_judge"
JUDGE_CANDIDATE_SELECTION = "candidate_selection_judge"
JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D = (
    "linkedin_originality_thoughtfulness_x1d_llm_judge"
)

NORMAL_DEFAULT_X2_GATES = (
    JUDGE_SCHEMA_POLICY_NO_SEND,
    JUDGE_LINKEDIN_TONE,
)

DELIBERATE_X2_GATES = (
    JUDGE_SCHEMA_POLICY_NO_SEND,
    JUDGE_LINKEDIN_TONE,
    JUDGE_CANDIDATE_SELECTION,
)

STRICT_X2_GATES = (
    JUDGE_EVIDENCE_SUPPORT,
    JUDGE_LINKEDIN_TONE,
    JUDGE_SAFETY_NO_FABRICATION,
)

DEFAULT_X1D_LLM_JUDGES = (JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,)

NORMAL_DEFAULT_JUDGES = (*NORMAL_DEFAULT_X2_GATES, *DEFAULT_X1D_LLM_JUDGES)
DELIBERATE_JUDGES = (*DELIBERATE_X2_GATES, *DEFAULT_X1D_LLM_JUDGES)
STRICT_JUDGES = (*STRICT_X2_GATES, *DEFAULT_X1D_LLM_JUDGES)

_GENERIC_NAMES = {"", "recruiter", "unknown", "unknown recipient"}
_GENERIC_COMPANIES = {"", "unknown", "n/a", "na"}
_ROLE_TERMS = (
    "role",
    "opportunity",
    "search",
    "vp",
    "global head",
    "head of",
    "executive",
    "leadership",
)
_EXECUTIVE_TERMS = (
    "executive",
    "chief",
    "c-level",
    "c level",
    "cto",
    "cdo",
    "cio",
    "ceo",
    "svp",
    "evp",
    "vice president",
    "vp",
    "global head",
)
_SENSITIVE_TERMS = (
    "compensation",
    "salary",
    "visa",
    "sponsorship",
    "referral",
    "referred",
    "prior relationship",
    "worked together",
    "met at",
    "personal",
)
_SEND_TERMS = (
    "send",
    "post",
    "publish",
    "auto-send",
    "autosend",
    "linkedin_send",
    "connector_send",
)


def default_reasoning_policy() -> dict[str, Any]:
    """Return the requested default apps_lic reasoning policy."""
    return {
        "policy_ref": POLICY_REF,
        "sc_level": SC_1,
        "reasoning_intensity": R1_STANDARD,
        "judge_profile": "normal_default",
        "judges": list(NORMAL_DEFAULT_JUDGES),
        "x2_deterministic_gates": list(NORMAL_DEFAULT_X2_GATES),
        "x1d_llm_judges": list(DEFAULT_X1D_LLM_JUDGES),
        "x1d_enabled": True,
        "x1d_runs_after_x2": True,
        "x1d_max_attempts": 1,
        "x1d_temperature": 0.1,
        "x1d_failure_policy": "quality_block_not_exit_override",
        "x1d_provider_profile": "qwen_vllm_x1d",
        "max_candidates": 1,
        "validation_repair_passes": 1,
        "fail_closed_on_empty_evidence": True,
        "no_send_authority": True,
        "escalation_triggers": [],
        "evidence_action": "pass_through_when_supported",
        "evidence_support_status": "",
    }


def select_reasoning_policy(app_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Select SC/R-level policy from U0 app payload risk signals."""
    campaign = _mapping(app_payload.get("campaign"))
    entity_refs = _mapping(app_payload.get("entity_refs"))
    lead = _mapping(entity_refs.get("lead_profile"))
    personalization = _mapping(app_payload.get("personalization"))
    inputs = _mapping(personalization.get("inputs"))
    routing_policy = _mapping(app_payload.get("routing_policy"))
    generation_hints = _mapping(app_payload.get("generation_hints"))

    text = _combined_text(campaign, lead, inputs, routing_policy, generation_hints)
    personalized_text = _combined_text(inputs, routing_policy, generation_hints)
    triggers: list[str] = []
    named_contact = _has_named_contact(lead)
    named_company = _has_named_company(lead)

    if named_contact:
        triggers.append("named_target_contact")
    if named_company:
        triggers.append("named_company")
    if _contains_any(personalized_text, _ROLE_TERMS) or (
        named_company and _contains_any(text, _ROLE_TERMS)
    ):
        triggers.append("role_specific_personalization")
    if _is_executive_contact(lead) or _contains_any(text, _EXECUTIVE_TERMS):
        triggers.append("executive_or_high_stakes")
    if _contains_any(text, _SENSITIVE_TERMS):
        triggers.append("sensitive_or_relationship_language")
    if _has_metric(text):
        triggers.append("metric_or_quantified_claim")
    if _contains_any(text, _SEND_TERMS):
        triggers.append("send_or_post_requested")

    strict = any(
        trigger in triggers
        for trigger in (
            "executive_or_high_stakes",
            "sensitive_or_relationship_language",
            "metric_or_quantified_claim",
            "send_or_post_requested",
        )
    )
    deliberate = any(
        trigger in triggers
        for trigger in (
            "named_target_contact",
            "named_company",
            "role_specific_personalization",
        )
    )

    policy = default_reasoning_policy()
    if strict:
        policy.update(
            {
                "sc_level": SC_3,
                "reasoning_intensity": R3_STRICT,
                "judge_profile": "high_risk_strict",
                "judges": list(STRICT_JUDGES),
                "x2_deterministic_gates": list(STRICT_X2_GATES),
                "x1d_llm_judges": list(DEFAULT_X1D_LLM_JUDGES),
                "max_candidates": 3,
                "validation_repair_passes": 2,
            }
        )
    elif deliberate:
        policy.update(
            {
                "sc_level": SC_2,
                "reasoning_intensity": R2_DELIBERATE,
                "judge_profile": "deliberate_selection",
                "judges": list(DELIBERATE_JUDGES),
                "x2_deterministic_gates": list(DELIBERATE_X2_GATES),
                "x1d_llm_judges": list(DEFAULT_X1D_LLM_JUDGES),
                "max_candidates": 2,
            }
        )

    requested_intensity = str(generation_hints.get("reasoning_intensity", "") or "")
    if requested_intensity == R0_MINIMAL and not triggers:
        policy.update(
            {
                "sc_level": SC_0,
                "reasoning_intensity": R0_MINIMAL,
                "judge_profile": "minimal_schema_only",
                "judges": [JUDGE_SCHEMA_POLICY_NO_SEND],
                "x2_deterministic_gates": [JUDGE_SCHEMA_POLICY_NO_SEND],
                "x1d_llm_judges": [],
                "x1d_enabled": False,
                "max_candidates": 1,
                "validation_repair_passes": 0,
            }
        )

    policy["escalation_triggers"] = sorted(set(triggers))
    return policy


def apply_evidence_support(
    policy: Mapping[str, Any],
    support_status: str,
) -> dict[str, Any]:
    """Attach C0 evidence status without using it to raise SC."""
    out = deepcopy(dict(policy))
    status = str(support_status or "").upper()
    out["evidence_support_status"] = status
    if status in {"WEAK", "EMPTY"}:
        out["evidence_action"] = (
            "fail_closed"
            if out.get("fail_closed_on_empty_evidence", True)
            else "reduce_specificity"
        )
        out["sc_escalation_blocked_by_evidence"] = True
        out["x1d_evidence_authority"] = "x1d_cannot_override_weak_or_empty_c0"
    elif status == "PASS":
        out["evidence_action"] = "pass_through_when_supported"
        out["sc_escalation_blocked_by_evidence"] = False
        out["x1d_evidence_authority"] = "x1d_quality_only_c0_authoritative"
    return out


def compact_policy(policy: Mapping[str, Any]) -> dict[str, Any]:
    """Return the stable, receipt-safe policy projection."""
    data = default_reasoning_policy()
    data.update(dict(policy))
    data["x1d_enabled"] = bool(data.get("x1d_enabled", True))
    data["x1d_runs_after_x2"] = bool(data.get("x1d_runs_after_x2", True))
    data["x1d_max_attempts"] = int(data.get("x1d_max_attempts") or 1)
    data["x1d_temperature"] = float(data.get("x1d_temperature") or 0.1)
    data["x1d_failure_policy"] = str(
        data.get("x1d_failure_policy") or "quality_block_not_exit_override"
    )
    data["x1d_provider_profile"] = str(
        data.get("x1d_provider_profile") or "qwen_vllm_x1d"
    )
    data = _sync_judge_axes(data)
    data["max_candidates"] = int(data.get("max_candidates") or 1)
    data["validation_repair_passes"] = int(data.get("validation_repair_passes") or 0)
    data["fail_closed_on_empty_evidence"] = bool(
        data.get("fail_closed_on_empty_evidence", True)
    )
    data["no_send_authority"] = bool(data.get("no_send_authority", True))
    data["escalation_triggers"] = sorted(
        {str(v) for v in data.get("escalation_triggers") or []}
    )
    return data


def policy_from_reason_codes(reason_codes: tuple[str, ...] | list[str]) -> dict[str, Any]:
    """Recover the policy projection from L0 reason codes."""
    policy = default_reasoning_policy()
    for code in reason_codes:
        if "=" not in str(code):
            continue
        key, value = str(code).split("=", 1)
        if key == "sc_level":
            policy["sc_level"] = value
        elif key == "reasoning_intensity":
            policy["reasoning_intensity"] = value
        elif key == "judge_profile":
            policy["judge_profile"] = value
        elif key == "max_candidates":
            try:
                policy["max_candidates"] = int(value)
            except ValueError:
                policy["max_candidates"] = 1
        elif key == "validation_repair_passes":
            try:
                policy["validation_repair_passes"] = int(value)
            except ValueError:
                policy["validation_repair_passes"] = 1
    if policy["reasoning_intensity"] == R3_STRICT:
        policy["judges"] = list(STRICT_JUDGES)
        policy["x2_deterministic_gates"] = list(STRICT_X2_GATES)
        policy["x1d_llm_judges"] = list(DEFAULT_X1D_LLM_JUDGES)
        policy["judge_profile"] = "high_risk_strict"
    elif policy["reasoning_intensity"] == R2_DELIBERATE:
        policy["judges"] = list(DELIBERATE_JUDGES)
        policy["x2_deterministic_gates"] = list(DELIBERATE_X2_GATES)
        policy["x1d_llm_judges"] = list(DEFAULT_X1D_LLM_JUDGES)
        policy["judge_profile"] = "deliberate_selection"
    elif policy["reasoning_intensity"] == R0_MINIMAL:
        policy["judges"] = [JUDGE_SCHEMA_POLICY_NO_SEND]
        policy["x2_deterministic_gates"] = [JUDGE_SCHEMA_POLICY_NO_SEND]
        policy["x1d_llm_judges"] = []
        policy["x1d_enabled"] = False
        policy["judge_profile"] = "minimal_schema_only"
    return compact_policy(policy)


def _sync_judge_axes(data: dict[str, Any]) -> dict[str, Any]:
    """Keep legacy ``judges`` and explicit X1D/X2 axes in sync."""
    raw_judges = [str(v) for v in data.get("judges") or [] if str(v).strip()]
    explicit_x2 = [
        str(v)
        for v in data.get("x2_deterministic_gates") or []
        if str(v).strip()
    ]
    explicit_x1d = [
        str(v)
        for v in data.get("x1d_llm_judges") or []
        if str(v).strip()
    ]
    if not explicit_x2:
        explicit_x2 = [j for j in raw_judges if j != JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D]
    if not data.get("x1d_enabled", True):
        explicit_x1d = []
    elif not explicit_x1d and data.get("reasoning_intensity") != R0_MINIMAL:
        explicit_x1d = list(DEFAULT_X1D_LLM_JUDGES)
    combined: list[str] = []
    for name in (*explicit_x2, *explicit_x1d):
        if name not in combined:
            combined.append(name)
    data["x2_deterministic_gates"] = explicit_x2
    data["x1d_llm_judges"] = explicit_x1d
    data["judges"] = combined
    return data


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _combined_text(*parts: Mapping[str, Any]) -> str:
    values: list[str] = []
    for part in parts:
        for value in part.values():
            values.append(str(value))
    return " ".join(values).lower()


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _has_metric(text: str) -> bool:
    return bool(re.search(r"\b\d+(?:\.\d+)?\s?%|\b\d+\s?(m|mm|k|b)\b", text))


def _has_named_contact(lead: Mapping[str, Any]) -> bool:
    name = str(lead.get("verified_name", "") or "").strip().lower()
    return name not in _GENERIC_NAMES


def _has_named_company(lead: Mapping[str, Any]) -> bool:
    company = str(lead.get("company_name", "") or "").strip().lower()
    return company not in _GENERIC_COMPANIES


def _is_executive_contact(lead: Mapping[str, Any]) -> bool:
    seniority = str(lead.get("seniority_class", "") or "").lower()
    title = str(lead.get("title", "") or "").lower()
    return _contains_any(f"{seniority} {title}", _EXECUTIVE_TERMS)


__all__ = [
    "JUDGE_CANDIDATE_SELECTION",
    "JUDGE_EVIDENCE_SUPPORT",
    "JUDGE_LINKEDIN_TONE",
    "JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D",
    "JUDGE_SAFETY_NO_FABRICATION",
    "JUDGE_SCHEMA_POLICY_NO_SEND",
    "POLICY_REF",
    "R0_MINIMAL",
    "R1_STANDARD",
    "R2_DELIBERATE",
    "R3_STRICT",
    "SC_0",
    "SC_1",
    "SC_2",
    "SC_3",
    "apply_evidence_support",
    "compact_policy",
    "default_reasoning_policy",
    "policy_from_reason_codes",
    "select_reasoning_policy",
]
