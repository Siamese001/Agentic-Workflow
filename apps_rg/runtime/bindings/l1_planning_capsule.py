"""Deterministic apps_rg L1 planning capsule.

This module is planning-only. It reads app-owned planning priors and U0
projections, then emits advisory structure for downstream stages to consume.
It never routes, retrieves evidence, assembles prompts, calls providers, or
writes run state.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from apps_rg.runtime.bindings.u0_profile_manifest import repo_root
from apps_rg.runtime.reasoning.section_reasoning_intensity import (
    profile_to_requested_kw,
    section_reasoning_profile,
)

_FULL_RESUME_GENERATION_MODES = frozenset(
    {"strategic_tailor", "tailor_existing", "generate_scratch"}
)
_SECTION_MODES = frozenset({"section_regen", "healing_fact_check"})
_SEVERITY_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
_ROUTE_AUTHORITY_KEYS = frozenset(
    {"route_id", "route_family", "execution_form", "selected_route_reason", "route_digest"}
)


def stable_capsule_digest(capsule_without_digest: Mapping[str, Any]) -> str:
    """Return a stable sha256 digest over a capsule, excluding only its own digest."""

    body = dict(capsule_without_digest)
    body.pop("capsule_digest", None)
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def stable_ambiguity_register(
    *,
    app_payload: Mapping[str, Any],
    ambiguity_rules: Sequence[Mapping[str, Any]],
    request_id: str,
    planning_profile_digest: str,
) -> dict[str, Any]:
    """Build a deterministic ambiguity register from profile rules and U0 projections."""

    entries: list[dict[str, Any]] = []
    for rule in ambiguity_rules:
        if not isinstance(rule, Mapping):
            continue
        field = str(rule.get("field") or "").strip()
        code = str(rule.get("code") or "").strip()
        if not field or not code or not _field_is_missing(app_payload, field):
            continue
        if field == "target_role" and not _field_value(app_payload, "target_company"):
            continue
        if field == "target_company" and not _field_value(app_payload, "target_role"):
            continue
        entries.append(
            {
                "code": code,
                "field": field,
                "severity": str(rule.get("severity") or "low"),
                "blocks_progress": bool(rule.get("blocks_progress", False)),
                "note": _ambiguity_note(code),
            }
        )

    max_severity = "none"
    for entry in entries:
        severity = str(entry.get("severity") or "none")
        if _SEVERITY_RANK.get(severity, 0) > _SEVERITY_RANK.get(max_severity, 0):
            max_severity = severity
    blocks_progress = any(bool(entry.get("blocks_progress")) for entry in entries)
    entries_json = json.dumps(entries, sort_keys=True, separators=(",", ":"), default=str)
    digest_body = {
        "request_id": request_id,
        "planning_profile_digest": planning_profile_digest,
        "entries": entries,
        "max_severity": max_severity,
        "blocks_progress": blocks_progress,
    }
    register_digest = _sha256_json_prefixed(digest_body)
    register_id_seed = f"{request_id}|{planning_profile_digest}|{entries_json}"
    register_id = f"amb-{hashlib.sha256(register_id_seed.encode('utf-8')).hexdigest()[:16]}"
    return {
        "schema_version": "apps_rg_ambiguity_register_v2",
        "register_id": register_id,
        "register_digest": register_digest,
        "max_severity": max_severity,
        "blocks_progress": blocks_progress,
        "hitl_hint": "required" if blocks_progress else ("optional" if entries else "none"),
        "entries": entries,
    }


def build_apps_rg_l1_planning_capsule(
    *,
    app_payload: Mapping[str, Any],
    request_id: str,
    run_id: str,
    trace_id: str,
    replay_key: str,
    planning_profile_ref: str,
    planning_profile_digest: str,
) -> dict[str, Any]:
    """Build the deterministic apps_rg L1 planning capsule."""

    profile = _load_planning_profile(planning_profile_ref)
    generation_mode = _generation_mode(app_payload)
    mode_profile = _mode_profile(profile, generation_mode)
    work_units = _work_units_for_mode(profile, app_payload, generation_mode)
    ambiguity_register = stable_ambiguity_register(
        app_payload=app_payload,
        ambiguity_rules=profile.get("ambiguity_rules") or (),
        request_id=request_id,
        planning_profile_digest=planning_profile_digest,
    )
    route_feature_hints = _route_feature_hints(mode_profile, generation_mode)
    completion_criteria = list(mode_profile.get("completion_criteria") or ())
    if not completion_criteria:
        completion_criteria = ["validated_request_shape_preserved", "no_route_authority_claims"]

    capsule: dict[str, Any] = {
        "schema_version": "apps_rg_l1_planning_capsule.v1",
        "authority_class": "PLANNING_ADVISORY_ONLY",
        "request_id": request_id,
        "run_id": run_id,
        "trace_id": trace_id,
        "replay_key": replay_key,
        "planning_prior_refs": [
            {
                "ref": planning_profile_ref,
                "digest": planning_profile_digest,
                "authority_class": "PLANNING_PRIOR_ONLY",
            }
        ],
        "intent_frame": _intent_frame(app_payload, generation_mode, mode_profile),
        "ambiguity_register": ambiguity_register,
        "completion_criteria": completion_criteria,
        "work_units": work_units,
        "dependency_sketch": _dependency_sketch(work_units),
        "evidence_plan": _evidence_plan(work_units),
        "prompt_plan": _prompt_plan(work_units),
        "cognition_plan": _cognition_plan(work_units),
        "route_feature_hints": route_feature_hints,
        "validation": {
            "no_route_selection": True,
            "no_evidence_retrieval": True,
            "no_prompt_assembly": True,
            "no_model_call": True,
            "no_tool_call": True,
            "no_l4_write": True,
        },
    }
    capsule["capsule_digest"] = stable_capsule_digest(capsule)
    _validate_no_route_authority_keys(capsule)
    return capsule


def _load_planning_profile(planning_profile_ref: str) -> dict[str, Any]:
    ref = planning_profile_ref or "apps_rg/profiles/rg_planning_profile.yaml"
    path = Path(ref)
    if not path.is_absolute():
        path = repo_root() / ref
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"L1 planning profile must be a mapping: {path}")
    return data


def _mode_profile(profile: Mapping[str, Any], generation_mode: str) -> Mapping[str, Any]:
    modes = profile.get("generation_modes")
    if not isinstance(modes, Mapping):
        return {}
    row = modes.get(generation_mode)
    return row if isinstance(row, Mapping) else {}


def _generation_mode(app_payload: Mapping[str, Any]) -> str:
    task_spec = app_payload.get("task_spec") if isinstance(app_payload.get("task_spec"), Mapping) else {}
    return str(task_spec.get("generation_mode") or app_payload.get("generation_mode") or "").strip()


def _intent_frame(
    app_payload: Mapping[str, Any],
    generation_mode: str,
    mode_profile: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "task_class": "resume_generation",
        "generation_mode": generation_mode or "unknown",
        "deliverable": str(mode_profile.get("deliverable") or "resume_planning_request"),
        "target_company": _field_value(app_payload, "target_company"),
        "target_role": _field_value(app_payload, "target_role"),
        "target_level": _field_value(app_payload, "target_level"),
        "assumptions": _intent_assumptions(app_payload),
        "excluded_authority_claims": [
            "route_selection",
            "evidence_retrieval",
            "prompt_assembly",
            "model_execution",
            "tool_execution",
            "l4_write",
        ],
    }


def _intent_assumptions(app_payload: Mapping[str, Any]) -> list[str]:
    assumptions: list[str] = []
    if not _field_value(app_payload, "target_level"):
        assumptions.append("target_level_may_be_inferred_downstream")
    if not _field_value(app_payload, "target_company"):
        assumptions.append("target_company_may_be_absent")
    return assumptions


def _work_units_for_mode(
    profile: Mapping[str, Any],
    app_payload: Mapping[str, Any],
    generation_mode: str,
) -> list[dict[str, Any]]:
    profiles = profile.get("work_unit_profiles")
    work_unit_profiles = profiles if isinstance(profiles, Mapping) else {}
    if generation_mode in _FULL_RESUME_GENERATION_MODES:
        return [
            _work_unit_from_profile(str(unit_id), row)
            for unit_id, row in work_unit_profiles.items()
            if isinstance(row, Mapping)
        ]
    if generation_mode in _SECTION_MODES:
        section_id = _requested_section_id(app_payload)
        if section_id:
            row = _section_profile(section_id, work_unit_profiles)
            return [_work_unit_from_profile(section_id, row)]
        generic_id = "healing_section" if generation_mode == "healing_fact_check" else "requested_section"
        return [_generic_work_unit(generic_id, healing=generation_mode == "healing_fact_check")]
    return [_generic_work_unit("request_planning_review", healing=False)]


def _work_unit_from_profile(unit_id: str, row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "unit_id": unit_id,
        "unit_type": str(row.get("unit_type") or "section"),
        "criticality": str(row.get("criticality") or "T2_QUALITY_SECTION"),
        "support_target": str(row.get("support_target") or "source_backed_claims"),
        "variance_class": str(row.get("variance_class") or "evidence_support"),
        "required_inputs": ["jd_hash", "resume_hash"],
        "required_slots": [str(slot) for slot in (row.get("required_slots") or ())],
        "output_contract_ref": f"apps_rg::output_contract::{unit_id}",
        "quality_floor_ref": f"apps_rg::quality_floor::{row.get('criticality') or 'T2_QUALITY_SECTION'}",
    }


def _generic_work_unit(unit_id: str, *, healing: bool) -> dict[str, Any]:
    return {
        "unit_id": unit_id,
        "unit_type": "fact_check_section" if healing else "section",
        "criticality": "T2_QUALITY_SECTION",
        "support_target": "source_backed_claims_only",
        "variance_class": "deterministic_guard" if healing else "evidence_support",
        "required_inputs": ["jd_hash", "resume_hash"],
        "required_slots": ["S0", "D0", "I0", "C0", "U0", "R0"],
        "output_contract_ref": f"apps_rg::output_contract::{unit_id}",
        "quality_floor_ref": "apps_rg::quality_floor::T2_QUALITY_SECTION",
    }


def _requested_section_id(app_payload: Mapping[str, Any]) -> str:
    direct = str(app_payload.get("section_id") or "").strip()
    if direct:
        return direct
    task_spec = app_payload.get("task_spec") if isinstance(app_payload.get("task_spec"), Mapping) else {}
    if task_spec.get("section_id"):
        return str(task_spec["section_id"]).strip()
    constraints = (
        app_payload.get("user_constraints")
        if isinstance(app_payload.get("user_constraints"), Mapping)
        else {}
    )
    if constraints.get("section_id"):
        return str(constraints["section_id"]).strip()
    sections = constraints.get("sections")
    if isinstance(sections, Sequence) and not isinstance(sections, (str, bytes)) and sections:
        return str(sections[0]).strip()
    return ""


def _section_profile(section_id: str, profiles: Mapping[str, Any]) -> Mapping[str, Any]:
    key = section_id.strip().lower()
    aliases = {
        "experience": "experience_block",
        "skills": "skills_block",
        "education": "education_block",
        "certifications": "certifications_block",
    }
    for candidate in (key, aliases.get(key, ""), f"{key}_block"):
        if candidate and isinstance(profiles.get(candidate), Mapping):
            return profiles[candidate]
    return _generic_work_unit(key or "requested_section", healing=False)


def _dependency_sketch(work_units: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for unit in work_units:
        unit_id = str(unit.get("unit_id") or "")
        if unit_id:
            rows.append({"from": "role_analysis", "to": unit_id, "relation": "SUPPORTS"})
            rows.append({"from": "source_resume_facts", "to": unit_id, "relation": "GROUNDS"})
    return rows


def _evidence_plan(work_units: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "unit_id": str(unit.get("unit_id") or ""),
            "support_target": str(unit.get("support_target") or ""),
            "query_intent": f"collect_support_for_{unit.get('unit_id') or 'unit'}",
            "allowed_source_classes": [
                "source_resume",
                "job_description",
                "approved_research_brief",
                "candidate_profile",
            ],
            "contradiction_scan_expected": True,
            "authority_class": "C0_EXECUTES_RETRIEVAL",
        }
        for unit in work_units
    ]


def _prompt_plan(work_units: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "unit_id": str(unit.get("unit_id") or ""),
            "required_slots": list(unit.get("required_slots") or ()),
            "provenance_slots_required": True,
            "prompt_bom_refs": ["apps_rg/prompt_assembly/prompt_bom.yaml"],
            "authority_class": "PA_ASSEMBLES_PROMPT",
        }
        for unit in work_units
    ]


def _cognition_plan(work_units: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for unit in work_units:
        unit_id = str(unit.get("unit_id") or "")
        profile = section_reasoning_profile(unit_id)
        requested = profile_to_requested_kw(profile)
        rows.append(
            {
                "unit_id": unit_id,
                "tier": profile.tier.value,
                "variance_class": str(unit.get("variance_class") or ""),
                "requested_controls": requested,
                "self_consistency_intent": float(profile.self_consistency_samples),
                "reflexion_intent": float(profile.reflexion_loops),
                "controls_applied": False,
                "execution_provability": "ADVISORY_ONLY_UNTIL_L2_RECEIPT",
                "singleton_transport_policy": "do_not_mark_applied_without_runner_receipt",
                "authority_class": "L2_OR_L3_MUST_PROVE_EXECUTION",
            }
        )
    return rows


def _route_feature_hints(
    mode_profile: Mapping[str, Any],
    generation_mode: str,
) -> dict[str, Any]:
    raw = mode_profile.get("route_feature_hints")
    hints = dict(raw) if isinstance(raw, Mapping) else {}
    if not hints:
        hints = {
            "multi_work_unit": generation_mode in _FULL_RESUME_GENERATION_MODES,
            "merge_needed": generation_mode in _FULL_RESUME_GENERATION_MODES,
            "candidate_selection_needed": generation_mode in _FULL_RESUME_GENERATION_MODES,
            "grounding_needed": generation_mode in _FULL_RESUME_GENERATION_MODES or generation_mode in _SECTION_MODES,
        }
    hints["authority_class"] = "ADVISORY_ONLY"
    hints["hitl_risk_hint"] = "low"
    return hints


def _field_is_missing(app_payload: Mapping[str, Any], field: str) -> bool:
    return not bool(_field_value(app_payload, field).strip())


def _field_value(app_payload: Mapping[str, Any], field: str) -> str:
    if field in {"target_company", "target_role", "target_level"}:
        query_spec = app_payload.get("query_spec") if isinstance(app_payload.get("query_spec"), Mapping) else {}
        target = query_spec.get("target") if isinstance(query_spec.get("target"), Mapping) else {}
        target_key = field.removeprefix("target_")
        return str(app_payload.get(field) or target.get(target_key) or "").strip()
    if field == "job_description_text":
        jd_payload = app_payload.get("jd_payload") if isinstance(app_payload.get("jd_payload"), Mapping) else {}
        return str(
            app_payload.get("job_description_text")
            or app_payload.get("jd_text")
            or jd_payload.get("jd_text")
            or jd_payload.get("text")
            or ""
        ).strip()
    if field == "source_resume_text":
        resume_payload = (
            app_payload.get("resume_payload")
            if isinstance(app_payload.get("resume_payload"), Mapping)
            else {}
        )
        return str(
            app_payload.get("source_resume_text")
            or app_payload.get("resume_text")
            or resume_payload.get("resume_text")
            or resume_payload.get("text")
            or ""
        ).strip()
    return str(app_payload.get(field) or "").strip()


def _ambiguity_note(code: str) -> str:
    return {
        "TARGET_ROLE_MISSING": "Company provided without explicit role title",
        "TARGET_COMPANY_MISSING": "Role provided without company name",
        "TARGET_LEVEL_UNSPECIFIED": "Default downstream level policy may apply",
        "JOB_DESCRIPTION_EMPTY": "Grounding and tailoring cannot be proven without JD text",
        "SOURCE_RESUME_EMPTY": "Resume body missing at U0 handoff",
    }.get(code, "Planning signal missing")


def _sha256_json_prefixed(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def _validate_no_route_authority_keys(payload: Any) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key in _ROUTE_AUTHORITY_KEYS:
                raise ValueError(f"L1 planning capsule contains route-authority key: {key}")
            _validate_no_route_authority_keys(value)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for value in payload:
            _validate_no_route_authority_keys(value)


__all__ = [
    "build_apps_rg_l1_planning_capsule",
    "stable_ambiguity_register",
    "stable_capsule_digest",
]
