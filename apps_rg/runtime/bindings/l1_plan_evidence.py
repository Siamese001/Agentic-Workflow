"""L1 planning evidence — validation receipt + ambiguity register (W3)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

__all__ = [
    "build_ambiguity_register",
    "build_completion_criteria",
    "build_planning_capsule_ref",
    "build_planning_prior_set_ref",
    "build_validation_receipt_id",
]

_SEVERITY_RANK: dict[str, int] = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


def build_validation_receipt_id(
    *,
    request_id: str,
    profile_manifest_digest: str,
    planning_profile_digest: str,
) -> str:
    """Stable validation receipt id for L1 plan path (REQ-L1-PLAN-VALIDATION-001)."""

    canonical = "|".join(
        (
            request_id,
            profile_manifest_digest,
            planning_profile_digest,
        )
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"l1val-{request_id[:8]}-{digest}"


def _stable_digest(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _normalize_refs(refs: Sequence[str]) -> tuple[str, ...]:
    return tuple(str(ref).strip() for ref in refs if str(ref).strip())


def build_planning_prior_set_ref(
    *,
    generation_mode: str,
    target_level: str,
    planning_prior_refs: Sequence[str],
    prompt_bom_refs: Sequence[str],
    profile_manifest_digest: str,
    planning_profile_digest: str,
) -> str:
    """Stable ref for the version-bound prior set that seeds L1 planning."""

    payload = {
        "generation_mode": generation_mode or "",
        "target_level": target_level or "",
        "planning_prior_refs": _normalize_refs(planning_prior_refs),
        "prompt_bom_refs": _normalize_refs(prompt_bom_refs),
        "profile_manifest_digest": profile_manifest_digest or "",
        "planning_profile_digest": planning_profile_digest or "",
    }
    return f"l1priors-{_stable_digest(payload)[:16]}"


def _max_ambiguity_severity(ambiguity_register: Mapping[str, Any] | None) -> str:
    entries = []
    if isinstance(ambiguity_register, Mapping):
        raw_entries = ambiguity_register.get("entries")
        if isinstance(raw_entries, Sequence) and not isinstance(raw_entries, (str, bytes, bytearray)):
            entries = list(raw_entries)

    max_rank = 0
    max_severity = "none"
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        severity = str(entry.get("severity") or "").strip().lower()
        rank = _SEVERITY_RANK.get(severity, 0)
        if rank > max_rank:
            max_rank = rank
            max_severity = severity or "none"
    return max_severity


def build_completion_criteria(
    *,
    active_generation_mode: bool,
    planning_prior_set_ref: str,
    ambiguity_register: Mapping[str, Any] | None,
    planning_prior_refs: Sequence[str],
    prompt_bom_refs: Sequence[str],
    profile_manifest_digest: str,
    planning_profile_digest: str,
) -> dict[str, Any]:
    """Bounded completion criteria for the L1 planning capsule."""

    max_severity = _max_ambiguity_severity(ambiguity_register)
    max_refinement_passes = 1 if active_generation_mode else 0
    return {
        "schema_version": "apps_rg_completion_criteria_v1",
        "planning_mode": "bounded_refinement" if active_generation_mode else "minimal_plan",
        "max_refinement_passes": max_refinement_passes,
        "planning_prior_set_ref": planning_prior_set_ref,
        "version_bound_prior_refs": _normalize_refs(planning_prior_refs),
        "prompt_bom_refs": _normalize_refs(prompt_bom_refs),
        "profile_manifest_digest": profile_manifest_digest or "",
        "planning_profile_digest": planning_profile_digest or "",
        "max_ambiguity_severity": max_severity,
        "ambiguity_policy": {
            "low": "continue_with_defaults",
            "medium": "continue_with_conservative_defaults",
            "high": "stop_and_request_input",
        },
    }


def build_planning_capsule_ref(
    *,
    generation_mode: str,
    target_level: str,
    task_plan: Sequence[str],
    required_capabilities: Sequence[str],
    planning_prior_set_ref: str,
    completion_criteria: Mapping[str, Any],
    profile_manifest_digest: str,
    planning_profile_digest: str,
) -> str:
    """Stable ref for the complete L1 planning capsule."""

    payload = {
        "generation_mode": generation_mode or "",
        "target_level": target_level or "",
        "task_plan": tuple(str(step) for step in task_plan),
        "required_capabilities": tuple(str(cap) for cap in required_capabilities),
        "planning_prior_set_ref": planning_prior_set_ref,
        "completion_criteria": dict(completion_criteria or {}),
        "profile_manifest_digest": profile_manifest_digest or "",
        "planning_profile_digest": planning_profile_digest or "",
    }
    return f"l1plan-{_stable_digest(payload)[:16]}"


def build_ambiguity_register(app_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Optional ambiguity register when ingress/planning signals are incomplete."""

    entries: list[dict[str, Any]] = []
    target_company = str(app_payload.get("target_company") or "").strip()
    target_role = str(app_payload.get("target_role") or "").strip()
    target_level = str(app_payload.get("target_level") or "").strip()
    jd_text = str(
        app_payload.get("job_description_text") or app_payload.get("jd_text") or ""
    ).strip()
    source_resume = str(app_payload.get("source_resume_text") or "").strip()

    if target_company and not target_role:
        entries.append(
            {
                "code": "TARGET_ROLE_MISSING",
                "field": "target_role",
                "severity": "medium",
                "severity_rank": 2,
                "default_assumption_allowed": True,
                "planner_action": "continue_with_conservative_defaults",
                "note": "Company provided without explicit role title",
            }
        )
    if target_role and not target_company:
        entries.append(
            {
                "code": "TARGET_COMPANY_MISSING",
                "field": "target_company",
                "severity": "low",
                "severity_rank": 1,
                "default_assumption_allowed": True,
                "planner_action": "continue_with_defaults",
                "note": "Role provided without company name",
            }
        )
    if not target_level:
        entries.append(
            {
                "code": "TARGET_LEVEL_UNSPECIFIED",
                "field": "target_level",
                "severity": "low",
                "severity_rank": 1,
                "default_assumption_allowed": True,
                "planner_action": "continue_with_defaults",
                "note": "Default L0 profile selection may apply",
            }
        )
    if not jd_text:
        entries.append(
            {
                "code": "JOB_DESCRIPTION_EMPTY",
                "field": "job_description_text",
                "severity": "high",
                "severity_rank": 3,
                "default_assumption_allowed": False,
                "planner_action": "stop_and_request_input",
                "note": "Grounding and tailoring quality may degrade",
            }
        )
    if not source_resume:
        entries.append(
            {
                "code": "SOURCE_RESUME_EMPTY",
                "field": "source_resume_text",
                "severity": "high",
                "severity_rank": 3,
                "default_assumption_allowed": False,
                "planner_action": "stop_and_request_input",
                "note": "Resume body missing at U0 handoff",
            }
        )

    if not entries:
        return {}

    canonical = {
        "target_company": target_company,
        "target_role": target_role,
        "target_level": target_level,
        "job_description_text": jd_text,
        "source_resume_text": source_resume,
        "entries": entries,
    }
    max_severity = "none"
    for entry in entries:
        rank = _SEVERITY_RANK.get(str(entry.get("severity") or "").strip().lower(), 0)
        if rank >= _SEVERITY_RANK.get(max_severity, 0):
            max_severity = str(entry.get("severity") or "none").strip().lower()

    return {
        "schema_version": "apps_rg_ambiguity_register_v1",
        "register_id": f"amb-{_stable_digest(canonical)[:12]}",
        "max_severity": max_severity,
        "entry_count": len(entries),
        "entries": entries,
    }
