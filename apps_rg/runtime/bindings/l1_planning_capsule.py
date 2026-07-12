"""Deterministic, integrity-bound apps_rg L1 planning capsule.

This module is planning-only. It reads app-owned planning priors and U0
projections, then emits immutable advisory structure for downstream stages.
It never routes, retrieves evidence, assembles prompts, calls providers, or
writes run state.
"""

from __future__ import annotations

import hashlib
import json
import re
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
_CANONICAL_PROFILE_REF = "apps_rg/profiles/rg_planning_profile.yaml"
_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_VALIDATION_ASSERTIONS = frozenset(
    {
        "no_route_selection",
        "no_evidence_retrieval",
        "no_prompt_assembly",
        "no_model_call",
        "no_tool_call",
        "no_l4_write",
        "profile_ref_digest_bound",
    }
)


class PlanningProfileIntegrityError(ValueError):
    """Raised when an L1 planning profile ref or digest is not trustworthy."""


class PlanningCapsuleIntegrityError(ValueError):
    """Raised when a planning capsule is malformed, mutable, or digest-invalid."""


class FrozenDict(dict):
    """JSON-compatible recursively frozen dictionary."""

    __slots__ = ()

    @staticmethod
    def _immutable(*_args: Any, **_kwargs: Any) -> None:
        raise TypeError("planning capsule mappings are immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable
    __ior__ = _immutable

    def __copy__(self) -> "FrozenDict":
        return self

    def __deepcopy__(self, _memo: dict[int, Any]) -> "FrozenDict":
        return self


class FrozenList(list):
    """JSON-compatible recursively frozen list."""

    __slots__ = ()

    @staticmethod
    def _immutable(*_args: Any, **_kwargs: Any) -> None:
        raise TypeError("planning capsule sequences are immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    __iadd__ = _immutable
    __imul__ = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    pop = _immutable
    remove = _immutable
    reverse = _immutable
    sort = _immutable

    def __copy__(self) -> "FrozenList":
        return self

    def __deepcopy__(self, _memo: dict[int, Any]) -> "FrozenList":
        return self


def _freeze(value: Any) -> Any:
    if isinstance(value, (FrozenDict, FrozenList)):
        return value
    if isinstance(value, Mapping):
        return FrozenDict((key, _freeze(item)) for key, item in value.items())
    if isinstance(value, list):
        return FrozenList(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def stable_capsule_digest(capsule_without_digest: Mapping[str, Any]) -> str:
    """Return stable SHA-256 over a capsule, excluding only its own digest field."""

    body = dict(capsule_without_digest)
    body.pop("capsule_digest", None)
    return f"sha256:{hashlib.sha256(_canonical_json(body).encode('utf-8')).hexdigest()}"


def verify_planning_profile_ref_digest(
    planning_profile_ref: str,
    planning_profile_digest: str,
) -> tuple[dict[str, Any], str, str]:
    """Resolve an approved profile and bind the exact loaded bytes to its digest.

    Only files beneath ``apps_rg/profiles`` are eligible. Symlink/path traversal
    escapes fail closed after path resolution.
    """

    root = repo_root().resolve()
    approved_root = (root / "apps_rg" / "profiles").resolve()
    raw_ref = str(planning_profile_ref or _CANONICAL_PROFILE_REF).strip()
    candidate = Path(raw_ref)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(approved_root)
        normalized_ref = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise PlanningProfileIntegrityError(
            f"L1 planning profile ref must remain under apps_rg/profiles: {raw_ref!r}"
        ) from exc
    if not resolved.is_file():
        raise PlanningProfileIntegrityError(f"L1 planning profile not found: {normalized_ref}")

    declared_digest = str(planning_profile_digest or "").strip().lower()
    if not _SHA256_HEX_RE.fullmatch(declared_digest):
        raise PlanningProfileIntegrityError(
            "L1 planning profile digest must be a lowercase 64-character SHA-256 hex string"
        )

    try:
        raw = resolved.read_bytes()
    except OSError as exc:
        raise PlanningProfileIntegrityError(
            f"L1 planning profile unreadable: {normalized_ref}: {exc}"
        ) from exc
    computed_digest = hashlib.sha256(raw).hexdigest()
    if computed_digest != declared_digest:
        raise PlanningProfileIntegrityError(
            "L1 planning profile ref/digest mismatch: "
            f"ref={normalized_ref!r} declared={declared_digest!r} computed={computed_digest!r}"
        )

    try:
        parsed = yaml.safe_load(raw.decode("utf-8")) or {}
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise PlanningProfileIntegrityError(
            f"L1 planning profile is not valid UTF-8 YAML: {normalized_ref}"
        ) from exc
    if not isinstance(parsed, dict):
        raise PlanningProfileIntegrityError(
            f"L1 planning profile must be a mapping: {normalized_ref}"
        )
    if parsed.get("authority_class") != "PLANNING_PRIOR_ONLY":
        raise PlanningProfileIntegrityError(
            f"L1 planning profile authority_class must be PLANNING_PRIOR_ONLY: {normalized_ref}"
        )
    return parsed, normalized_ref, computed_digest


def _rule_applies(rule: Mapping[str, Any], generation_mode: str) -> bool:
    included = rule.get("applicable_modes") or rule.get("modes")
    if included:
        if not isinstance(included, Sequence) or isinstance(included, (str, bytes)):
            return False
        if generation_mode not in {str(item) for item in included}:
            return False
    excluded = rule.get("excluded_modes") or ()
    if isinstance(excluded, Sequence) and not isinstance(excluded, (str, bytes)):
        if generation_mode in {str(item) for item in excluded}:
            return False
    return True


def stable_ambiguity_register(
    *,
    app_payload: Mapping[str, Any],
    ambiguity_rules: Sequence[Mapping[str, Any]],
    request_id: str,
    planning_profile_digest: str,
    generation_mode: str = "",
) -> dict[str, Any]:
    """Build a deterministic, mode-aware ambiguity register."""

    entries: list[dict[str, Any]] = []
    for rule in ambiguity_rules:
        if not isinstance(rule, Mapping) or not _rule_applies(rule, generation_mode):
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
    digest_body = {
        "request_id": request_id,
        "generation_mode": generation_mode,
        "planning_profile_digest": planning_profile_digest,
        "entries": entries,
        "max_severity": max_severity,
        "blocks_progress": blocks_progress,
    }
    register_digest = _sha256_json_prefixed(digest_body)
    register_id = f"amb-{register_digest.removeprefix('sha256:')[:16]}"
    if blocks_progress:
        hitl_hint = "required"
    elif _SEVERITY_RANK.get(max_severity, 0) >= _SEVERITY_RANK["high"]:
        hitl_hint = "review"
    elif entries:
        hitl_hint = "optional"
    else:
        hitl_hint = "none"
    return {
        "schema_version": "apps_rg_ambiguity_register_v2",
        "register_id": register_id,
        "register_digest": register_digest,
        "generation_mode": generation_mode or "unknown",
        "max_severity": max_severity,
        "blocks_progress": blocks_progress,
        "hitl_hint": hitl_hint,
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
) -> FrozenDict:
    """Build an immutable, verified apps_rg L1 planning capsule."""

    profile, verified_ref, verified_digest = verify_planning_profile_ref_digest(
        planning_profile_ref,
        planning_profile_digest,
    )
    generation_mode = _generation_mode(app_payload)
    mode_profile = _mode_profile(profile, generation_mode)
    work_units = _work_units_for_mode(profile, app_payload, generation_mode)
    ambiguity_register = stable_ambiguity_register(
        app_payload=app_payload,
        ambiguity_rules=profile.get("ambiguity_rules") or (),
        request_id=request_id,
        planning_profile_digest=verified_digest,
        generation_mode=generation_mode,
    )
    planning_status = "BLOCKED" if ambiguity_register["blocks_progress"] else "READY"
    route_feature_hints = _route_feature_hints(
        mode_profile,
        generation_mode,
        ambiguity_register=ambiguity_register,
    )
    completion_criteria = list(mode_profile.get("completion_criteria") or ())
    if not completion_criteria:
        completion_criteria = ["validated_request_shape_preserved", "no_route_authority_claims"]

    capsule: dict[str, Any] = {
        "schema_version": "apps_rg_l1_planning_capsule.v1",
        "authority_class": "PLANNING_ADVISORY_ONLY",
        "planning_status": planning_status,
        "request_id": request_id,
        "run_id": run_id,
        "trace_id": trace_id,
        "replay_key": replay_key,
        "planning_prior_refs": [
            {
                "ref": verified_ref,
                "digest": verified_digest,
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
            "profile_ref_digest_bound": True,
        },
    }
    capsule["capsule_digest"] = stable_capsule_digest(capsule)
    verify_apps_rg_l1_planning_capsule(
        capsule,
        expected_profile_ref=verified_ref,
        expected_profile_digest=verified_digest,
    )
    return _freeze(capsule)


def verify_apps_rg_l1_planning_capsule(
    capsule: Mapping[str, Any],
    *,
    expected_capsule_digest: str = "",
    expected_profile_ref: str = "",
    expected_profile_digest: str = "",
) -> FrozenDict:
    """Fail closed unless a capsule is complete, internally coherent, and digest-valid."""

    if not isinstance(capsule, Mapping):
        raise PlanningCapsuleIntegrityError("L1 planning capsule must be a mapping")
    if capsule.get("schema_version") != "apps_rg_l1_planning_capsule.v1":
        raise PlanningCapsuleIntegrityError("unsupported L1 planning capsule schema_version")
    if capsule.get("authority_class") != "PLANNING_ADVISORY_ONLY":
        raise PlanningCapsuleIntegrityError("L1 planning capsule authority_class is invalid")
    _validate_no_route_authority_keys(capsule)

    declared_digest = str(capsule.get("capsule_digest") or "").strip()
    computed_digest = stable_capsule_digest(capsule)
    if not declared_digest or declared_digest != computed_digest:
        raise PlanningCapsuleIntegrityError(
            f"L1 planning capsule digest mismatch: declared={declared_digest!r} computed={computed_digest!r}"
        )
    if expected_capsule_digest and declared_digest != expected_capsule_digest:
        raise PlanningCapsuleIntegrityError(
            "L1 planning capsule ref does not match the embedded capsule digest"
        )

    prior_refs = capsule.get("planning_prior_refs")
    if (
        not isinstance(prior_refs, Sequence)
        or isinstance(prior_refs, (str, bytes))
        or len(prior_refs) != 1
    ):
        raise PlanningCapsuleIntegrityError(
            "L1 planning capsule must bind exactly one planning prior"
        )
    prior = prior_refs[0]
    if not isinstance(prior, Mapping):
        raise PlanningCapsuleIntegrityError("L1 planning prior binding must be a mapping")
    profile_ref = str(prior.get("ref") or "").strip()
    profile_digest = str(prior.get("digest") or "").strip()
    if prior.get("authority_class") != "PLANNING_PRIOR_ONLY":
        raise PlanningCapsuleIntegrityError("planning prior authority_class is invalid")
    try:
        _profile, verified_profile_ref, verified_profile_digest = (
            verify_planning_profile_ref_digest(profile_ref, profile_digest)
        )
    except PlanningProfileIntegrityError as exc:
        raise PlanningCapsuleIntegrityError(
            f"planning prior ref/digest verification failed: {exc}"
        ) from exc
    if profile_ref != verified_profile_ref or profile_digest != verified_profile_digest:
        raise PlanningCapsuleIntegrityError(
            "planning prior binding is not in canonical normalized form"
        )
    if expected_profile_ref and profile_ref != expected_profile_ref:
        raise PlanningCapsuleIntegrityError("planning profile ref does not match expected ref")
    if expected_profile_digest and profile_digest != expected_profile_digest:
        raise PlanningCapsuleIntegrityError("planning profile digest does not match expected digest")

    ambiguity = capsule.get("ambiguity_register")
    if not isinstance(ambiguity, Mapping):
        raise PlanningCapsuleIntegrityError("ambiguity_register is required")
    planning_status = str(capsule.get("planning_status") or "")
    expected_status = "BLOCKED" if bool(ambiguity.get("blocks_progress")) else "READY"
    if planning_status != expected_status:
        raise PlanningCapsuleIntegrityError(
            f"planning_status={planning_status!r} conflicts with ambiguity register"
        )

    validation = capsule.get("validation")
    if not isinstance(validation, Mapping):
        raise PlanningCapsuleIntegrityError("validation assertions are required")
    missing_assertions = _REQUIRED_VALIDATION_ASSERTIONS - set(validation)
    false_assertions = sorted(
        key for key in _REQUIRED_VALIDATION_ASSERTIONS if validation.get(key) is not True
    )
    if missing_assertions or false_assertions:
        raise PlanningCapsuleIntegrityError(
            "L1 planning capsule validation assertions are incomplete: "
            f"missing={sorted(missing_assertions)} false={false_assertions}"
        )

    receipt = {
        "schema_version": "apps_rg_l1_capsule_verification.v1",
        "verified": True,
        "capsule_digest": declared_digest,
        "planning_profile_ref": profile_ref,
        "planning_profile_digest": profile_digest,
        "planning_status": planning_status,
    }
    return _freeze(receipt)


def extract_verified_planning_capsule(
    plan: Any,
    *,
    required: bool = True,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Extract and verify the capsule carried by an L1 plan contract."""

    task_spec = getattr(plan, "task_spec", None) or {}
    if not isinstance(task_spec, Mapping):
        raise PlanningCapsuleIntegrityError("L1 plan task_spec must be a mapping")
    capsule = task_spec.get("apps_rg_planning_capsule")
    capsule_ref = str(task_spec.get("apps_rg_planning_capsule_ref") or "").strip()
    if capsule is None:
        if required:
            raise PlanningCapsuleIntegrityError("L1 plan is missing apps_rg planning capsule")
        return {}, {}
    if not isinstance(capsule, Mapping):
        raise PlanningCapsuleIntegrityError(
            "embedded apps_rg planning capsule must be a mapping"
        )
    receipt = verify_apps_rg_l1_planning_capsule(
        capsule,
        expected_capsule_digest=capsule_ref,
    )
    return capsule, receipt


def _mode_profile(profile: Mapping[str, Any], generation_mode: str) -> Mapping[str, Any]:
    modes = profile.get("generation_modes")
    if not isinstance(modes, Mapping):
        return {}
    row = modes.get(generation_mode)
    return row if isinstance(row, Mapping) else {}


def _generation_mode(app_payload: Mapping[str, Any]) -> str:
    task_spec = (
        app_payload.get("task_spec")
        if isinstance(app_payload.get("task_spec"), Mapping)
        else {}
    )
    return str(
        task_spec.get("generation_mode") or app_payload.get("generation_mode") or ""
    ).strip()


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
        generic_id = (
            "healing_section"
            if generation_mode == "healing_fact_check"
            else "requested_section"
        )
        return [
            _generic_work_unit(
                generic_id,
                healing=generation_mode == "healing_fact_check",
            )
        ]
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
        "quality_floor_ref": (
            f"apps_rg::quality_floor::{row.get('criticality') or 'T2_QUALITY_SECTION'}"
        ),
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
    task_spec = (
        app_payload.get("task_spec")
        if isinstance(app_payload.get("task_spec"), Mapping)
        else {}
    )
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
    if (
        isinstance(sections, Sequence)
        and not isinstance(sections, (str, bytes))
        and sections
    ):
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
            rows.append(
                {"from": "source_resume_facts", "to": unit_id, "relation": "GROUNDS"}
            )
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


def _reasoning_lane_for_unit(unit_id: str) -> str:
    return {
        "education_block": "education",
        "certifications_block": "certifications",
        "skills_block": "competencies",
    }.get(unit_id, unit_id)


def _cognition_plan(work_units: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for unit in work_units:
        unit_id = str(unit.get("unit_id") or "")
        profile = section_reasoning_profile(_reasoning_lane_for_unit(unit_id))
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
                "singleton_transport_policy": (
                    "do_not_mark_applied_without_runner_receipt"
                ),
                "authority_class": "L2_OR_L3_MUST_PROVE_EXECUTION",
            }
        )
    return rows


def _route_feature_hints(
    mode_profile: Mapping[str, Any],
    generation_mode: str,
    *,
    ambiguity_register: Mapping[str, Any],
) -> dict[str, Any]:
    raw = mode_profile.get("route_feature_hints")
    hints = dict(raw) if isinstance(raw, Mapping) else {}
    if not hints:
        hints = {
            "multi_work_unit": generation_mode in _FULL_RESUME_GENERATION_MODES,
            "merge_needed": generation_mode in _FULL_RESUME_GENERATION_MODES,
            "candidate_selection_needed": generation_mode
            in _FULL_RESUME_GENERATION_MODES,
            "grounding_needed": generation_mode in _FULL_RESUME_GENERATION_MODES
            or generation_mode in _SECTION_MODES,
        }
    if ambiguity_register.get("blocks_progress"):
        hitl_risk = "required"
    elif ambiguity_register.get("hitl_hint") == "review":
        hitl_risk = "medium"
    elif ambiguity_register.get("entries"):
        hitl_risk = "low"
    else:
        hitl_risk = "none"
    hints["authority_class"] = "ADVISORY_ONLY"
    hints["hitl_risk_hint"] = hitl_risk
    return hints


def _field_is_missing(app_payload: Mapping[str, Any], field: str) -> bool:
    return not bool(_field_value(app_payload, field).strip())


def _field_value(app_payload: Mapping[str, Any], field: str) -> str:
    if field in {"target_company", "target_role", "target_level"}:
        query_spec = (
            app_payload.get("query_spec")
            if isinstance(app_payload.get("query_spec"), Mapping)
            else {}
        )
        target = (
            query_spec.get("target")
            if isinstance(query_spec.get("target"), Mapping)
            else {}
        )
        target_key = field.removeprefix("target_")
        return str(app_payload.get(field) or target.get(target_key) or "").strip()
    if field == "job_description_text":
        jd_payload = (
            app_payload.get("jd_payload")
            if isinstance(app_payload.get("jd_payload"), Mapping)
            else {}
        )
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
    return f"sha256:{hashlib.sha256(_canonical_json(payload).encode('utf-8')).hexdigest()}"


def _validate_no_route_authority_keys(payload: Any) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key in _ROUTE_AUTHORITY_KEYS:
                raise PlanningCapsuleIntegrityError(
                    f"L1 planning capsule contains route-authority key: {key}"
                )
            _validate_no_route_authority_keys(value)
    elif isinstance(payload, Sequence) and not isinstance(
        payload,
        (str, bytes, bytearray),
    ):
        for value in payload:
            _validate_no_route_authority_keys(value)


__all__ = [
    "FrozenDict",
    "FrozenList",
    "PlanningCapsuleIntegrityError",
    "PlanningProfileIntegrityError",
    "build_apps_rg_l1_planning_capsule",
    "extract_verified_planning_capsule",
    "stable_ambiguity_register",
    "stable_capsule_digest",
    "verify_apps_rg_l1_planning_capsule",
    "verify_planning_profile_ref_digest",
]
