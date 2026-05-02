"""YAML loader for app-domain contract proposals.

Reads the 13-file YAML set under ``apps_<name>/config/domain_contract/`` and
returns an :class:`AppDomainContractBundle` ready to pass to
:func:`register_bundle`. Proposal-side: never writes to L4.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml

from agentic_core.L4_state.contracts.app_domain import (
    AppCapabilityProfileRecord,
    AppDomainContractError,
    AppDomainContractRecord,
    AppEvalRubricRecord,
    AppFixtureRecord,
    AppGraderRosterRecord,
    AppInputContractRecord,
    AppNegativeControlRecord,
    AppOrchestrationProfileRecord,
    AppOutputSchemaRecord,
    AppPromptProfileRecord,
    AppRetrievalProfileRecord,
    AppRouteProfileRecord,
    AppThresholdProfileRecord,
    ScoreDimension,
    TaskClassEntry,
)
from agentic_core.L4_state.uwg.app_domain_registration import AppDomainContractBundle

Logger = logging.getLogger(__name__)

DOMAIN_CONTRACT_FILES = (
    "app_domain_manifest.yaml",
    "task_classes.yaml",
    "input_contract.yaml",
    "output_schema.yaml",
    "eval_rubrics.yaml",
    "threshold_profiles.yaml",
    "grader_roster.yaml",
    "retrieval_profiles.yaml",
    "prompt_profiles.yaml",
    "capability_profiles.yaml",
    "route_profiles.yaml",
    "orchestration_profiles.yaml",
    "fixtures.yaml",
    "negative_controls.yaml",
)


def _read_yaml(path: Path) -> Any:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _str_tuple(value: Any) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(str(v) for v in value)
    raise AppDomainContractError(f"expected list, got {type(value).__name__}")


def _str_str_map(value: Any) -> Dict[str, str]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    raise AppDomainContractError(f"expected mapping, got {type(value).__name__}")


def _str_float_map(value: Any) -> Dict[str, float]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return {str(k): float(v) for k, v in value.items()}
    raise AppDomainContractError(f"expected mapping, got {type(value).__name__}")


def _require(d: Dict[str, Any], key: str, ctx: str) -> Any:
    if key not in d:
        raise AppDomainContractError(f"{ctx}: missing required field {key!r}")
    return d[key]


def _build_task_class(d: Dict[str, Any]) -> TaskClassEntry:
    return TaskClassEntry(
        task_class=str(_require(d, "task_class", "task_class")),
        kind=str(_require(d, "kind", "task_class")),
        description=str(d.get("description", "")),
        risk_tier=str(d.get("risk_tier", "standard")),
        hitl_required=bool(d.get("hitl_required", False)),
    )


def _build_score_dimension(d: Dict[str, Any]) -> ScoreDimension:
    return ScoreDimension(
        dimension_id=str(_require(d, "dimension_id", "score_dimension")),
        description=str(d.get("description", "")),
        weight=float(_require(d, "weight", "score_dimension")),
        grader_type=str(_require(d, "grader_type", "score_dimension")),
        min_required_score=float(d.get("min_required_score", -1.0)),
        evidence_required=bool(d.get("evidence_required", True)),
        fail_closed_if_unknown=bool(d.get("fail_closed_if_unknown", True)),
    )


def _build_manifest(d: Dict[str, Any], task_classes: Tuple[TaskClassEntry, ...]) -> AppDomainContractRecord:
    return AppDomainContractRecord(
        app_domain_contract_id=str(_require(d, "app_domain_contract_id", "manifest")),
        app_id=str(_require(d, "app_id", "manifest")),
        app_version=str(_require(d, "app_version", "manifest")),
        domain=str(_require(d, "domain", "manifest")),
        owner_surface=str(_require(d, "owner_surface", "manifest")),
        status=str(_require(d, "status", "manifest")),
        task_classes=task_classes,
        input_contract_ref=str(d.get("input_contract_ref", "")),
        output_schema_ref=str(d.get("output_schema_ref", "")),
        eval_rubric_refs=_str_tuple(d.get("eval_rubric_refs")),
        threshold_profile_refs=_str_tuple(d.get("threshold_profile_refs")),
        grader_roster_refs=_str_tuple(d.get("grader_roster_refs")),
        retrieval_profile_refs=_str_tuple(d.get("retrieval_profile_refs")),
        prompt_profile_refs=_str_tuple(d.get("prompt_profile_refs")),
        capability_profile_refs=_str_tuple(d.get("capability_profile_refs")),
        route_profile_refs=_str_tuple(d.get("route_profile_refs")),
        orchestration_profile_refs=_str_tuple(d.get("orchestration_profile_refs")),
        fixture_refs=_str_tuple(d.get("fixture_refs")),
        negative_control_refs=_str_tuple(d.get("negative_control_refs")),
        policy_hash=str(d.get("policy_hash", "")),
        blueprint_hash=str(d.get("blueprint_hash", "")),
        registry_digest_set=_str_tuple(d.get("registry_digest_set")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_input_contract(d: Dict[str, Any]) -> AppInputContractRecord:
    return AppInputContractRecord(
        input_contract_id=str(_require(d, "input_contract_id", "input_contract")),
        app_id=str(_require(d, "app_id", "input_contract")),
        task_class=str(_require(d, "task_class", "input_contract")),
        version=str(_require(d, "version", "input_contract")),
        status=str(_require(d, "status", "input_contract")),
        missing_input_behavior=str(_require(d, "missing_input_behavior", "input_contract")),
        ambiguity_behavior=str(_require(d, "ambiguity_behavior", "input_contract")),
        policy_hash=str(d.get("policy_hash", "")),
        required_inputs=_str_tuple(d.get("required_inputs")),
        optional_inputs=_str_tuple(d.get("optional_inputs")),
        forbidden_inputs=_str_tuple(d.get("forbidden_inputs")),
        input_normalization_rules=_str_tuple(d.get("input_normalization_rules")),
        data_boundary_rules=_str_tuple(d.get("data_boundary_rules")),
        origin_trust_requirements=_str_tuple(d.get("origin_trust_requirements")),
        validation_rules=_str_tuple(d.get("validation_rules")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_output_schema(d: Dict[str, Any]) -> AppOutputSchemaRecord:
    return AppOutputSchemaRecord(
        output_schema_id=str(_require(d, "output_schema_id", "output_schema")),
        app_id=str(_require(d, "app_id", "output_schema")),
        task_class=str(_require(d, "task_class", "output_schema")),
        version=str(_require(d, "version", "output_schema")),
        status=str(_require(d, "status", "output_schema")),
        output_type=str(_require(d, "output_type", "output_schema")),
        policy_hash=str(d.get("policy_hash", "")),
        required_sections=_str_tuple(d.get("required_sections")),
        optional_sections=_str_tuple(d.get("optional_sections")),
        field_constraints=_str_str_map(d.get("field_constraints")),
        formatting_constraints=_str_str_map(d.get("formatting_constraints")),
        prohibited_outputs=_str_tuple(d.get("prohibited_outputs")),
        schema_validation_rules=_str_tuple(d.get("schema_validation_rules")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_eval_rubric(d: Dict[str, Any]) -> AppEvalRubricRecord:
    dims_raw = _require(d, "score_dimensions", "eval_rubric")
    if not isinstance(dims_raw, list) or not dims_raw:
        raise AppDomainContractError("eval_rubric.score_dimensions must be a non-empty list")
    return AppEvalRubricRecord(
        eval_rubric_id=str(_require(d, "eval_rubric_id", "eval_rubric")),
        app_id=str(_require(d, "app_id", "eval_rubric")),
        task_class=str(_require(d, "task_class", "eval_rubric")),
        version=str(_require(d, "version", "eval_rubric")),
        status=str(_require(d, "status", "eval_rubric")),
        policy_hash=str(d.get("policy_hash", "")),
        score_dimensions=tuple(_build_score_dimension(x) for x in dims_raw),
        shared_base_ref=str(d.get("shared_base_ref", "")),
        app_override_ref=str(d.get("app_override_ref", "")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_threshold_profile(d: Dict[str, Any]) -> AppThresholdProfileRecord:
    return AppThresholdProfileRecord(
        threshold_profile_id=str(_require(d, "threshold_profile_id", "threshold_profile")),
        app_id=str(_require(d, "app_id", "threshold_profile")),
        task_class=str(_require(d, "task_class", "threshold_profile")),
        version=str(_require(d, "version", "threshold_profile")),
        status=str(_require(d, "status", "threshold_profile")),
        overall_pass_threshold=float(_require(d, "overall_pass_threshold", "threshold_profile")),
        risk_tier=str(d.get("risk_tier", "standard")),
        route_id=str(d.get("route_id", "")),
        unknown_policy=str(d.get("unknown_policy", "fail_closed")),
        abstain_policy=str(d.get("abstain_policy", "soft")),
        hitl_policy=str(d.get("hitl_policy", "none")),
        policy_hash=str(d.get("policy_hash", "")),
        dimension_minimums=_str_float_map(d.get("dimension_minimums")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_grader_roster(d: Dict[str, Any]) -> AppGraderRosterRecord:
    return AppGraderRosterRecord(
        grader_roster_id=str(_require(d, "grader_roster_id", "grader_roster")),
        app_id=str(_require(d, "app_id", "grader_roster")),
        task_class=str(_require(d, "task_class", "grader_roster")),
        version=str(_require(d, "version", "grader_roster")),
        status=str(_require(d, "status", "grader_roster")),
        fallback_behavior=str(d.get("fallback_behavior", "fail_closed")),
        deterministic_graders=_str_tuple(d.get("deterministic_graders")),
        llm_judge_graders=_str_tuple(d.get("llm_judge_graders")),
        ensemble_or_consensus_graders=_str_tuple(d.get("ensemble_or_consensus_graders")),
        calibration_refs=_str_tuple(d.get("calibration_refs")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_retrieval_profile(d: Dict[str, Any]) -> AppRetrievalProfileRecord:
    return AppRetrievalProfileRecord(
        retrieval_profile_id=str(_require(d, "retrieval_profile_id", "retrieval_profile")),
        app_id=str(_require(d, "app_id", "retrieval_profile")),
        task_class=str(_require(d, "task_class", "retrieval_profile")),
        version=str(_require(d, "version", "retrieval_profile")),
        status=str(_require(d, "status", "retrieval_profile")),
        freshness_class=str(_require(d, "freshness_class", "retrieval_profile")),
        source_lineage_required=bool(d.get("source_lineage_required", True)),
        policy_hash=str(d.get("policy_hash", "")),
        allowed_sources=_str_tuple(d.get("allowed_sources")),
        prohibited_sources=_str_tuple(d.get("prohibited_sources")),
        required_evidence_for=_str_tuple(d.get("required_evidence_for")),
        acl_requirements=_str_tuple(d.get("acl_requirements")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_prompt_profile(d: Dict[str, Any]) -> AppPromptProfileRecord:
    return AppPromptProfileRecord(
        prompt_profile_id=str(_require(d, "prompt_profile_id", "prompt_profile")),
        app_id=str(_require(d, "app_id", "prompt_profile")),
        task_class=str(_require(d, "task_class", "prompt_profile")),
        version=str(_require(d, "version", "prompt_profile")),
        status=str(_require(d, "status", "prompt_profile")),
        output_schema_ref=str(_require(d, "output_schema_ref", "prompt_profile")),
        policy_hash=str(d.get("policy_hash", "")),
        required_slots=_str_tuple(d.get("required_slots")),
        optional_slots=_str_tuple(d.get("optional_slots")),
        forbidden_content=_str_tuple(d.get("forbidden_content")),
        prompt_boundary_rules=_str_tuple(d.get("prompt_boundary_rules")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_capability_profile(d: Dict[str, Any]) -> AppCapabilityProfileRecord:
    return AppCapabilityProfileRecord(
        capability_profile_id=str(_require(d, "capability_profile_id", "capability_profile")),
        app_id=str(_require(d, "app_id", "capability_profile")),
        task_class=str(_require(d, "task_class", "capability_profile")),
        version=str(_require(d, "version", "capability_profile")),
        status=str(_require(d, "status", "capability_profile")),
        side_effect_class=str(_require(d, "side_effect_class", "capability_profile")),
        policy_hash=str(d.get("policy_hash", "")),
        allowed_tools=_str_tuple(d.get("allowed_tools")),
        forbidden_tools=_str_tuple(d.get("forbidden_tools")),
        allowed_connectors=_str_tuple(d.get("allowed_connectors")),
        forbidden_connectors=_str_tuple(d.get("forbidden_connectors")),
        hitl_required_for=_str_tuple(d.get("hitl_required_for")),
        sandbox_requirements=_str_tuple(d.get("sandbox_requirements")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_route_profile(d: Dict[str, Any]) -> AppRouteProfileRecord:
    return AppRouteProfileRecord(
        route_profile_id=str(_require(d, "route_profile_id", "route_profile")),
        app_id=str(_require(d, "app_id", "route_profile")),
        task_class=str(_require(d, "task_class", "route_profile")),
        version=str(_require(d, "version", "route_profile")),
        status=str(_require(d, "status", "route_profile")),
        default_route_id=str(_require(d, "default_route_id", "route_profile")),
        grounding_required=bool(d.get("grounding_required", True)),
        managed_workflow_allowed=bool(d.get("managed_workflow_allowed", True)),
        allowed_route_ids=_str_tuple(d.get("allowed_route_ids")),
        l3_dag_ref=str(d.get("l3_dag_ref", "")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_orchestration_profile(d: Dict[str, Any]) -> AppOrchestrationProfileRecord:
    return AppOrchestrationProfileRecord(
        orchestration_profile_id=str(_require(d, "orchestration_profile_id", "orchestration_profile")),
        app_id=str(_require(d, "app_id", "orchestration_profile")),
        task_class=str(_require(d, "task_class", "orchestration_profile")),
        version=str(_require(d, "version", "orchestration_profile")),
        status=str(_require(d, "status", "orchestration_profile")),
        orchestration_kind=str(_require(d, "orchestration_kind", "orchestration_profile")),
        hop_sequence=_str_tuple(d.get("hop_sequence")),
        dag_node_refs=_str_tuple(d.get("dag_node_refs")),
        blueprint_ref=str(d.get("blueprint_ref", "")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_fixture(d: Dict[str, Any]) -> AppFixtureRecord:
    return AppFixtureRecord(
        fixture_id=str(_require(d, "fixture_id", "fixture")),
        app_id=str(_require(d, "app_id", "fixture")),
        task_class=str(_require(d, "task_class", "fixture")),
        fixture_type=str(_require(d, "fixture_type", "fixture")),
        version=str(_require(d, "version", "fixture")),
        status=str(_require(d, "status", "fixture")),
        input_ref=str(_require(d, "input_ref", "fixture")),
        expected_disposition=str(_require(d, "expected_disposition", "fixture")),
        expected_gate_results=_str_str_map(d.get("expected_gate_results")),
        expected_output_assertions=_str_tuple(d.get("expected_output_assertions")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _build_negative_control(d: Dict[str, Any]) -> AppNegativeControlRecord:
    return AppNegativeControlRecord(
        negative_control_id=str(_require(d, "negative_control_id", "negative_control")),
        app_id=str(_require(d, "app_id", "negative_control")),
        task_class=str(_require(d, "task_class", "negative_control")),
        version=str(_require(d, "version", "negative_control")),
        status=str(_require(d, "status", "negative_control")),
        expected_failure_dimension=str(_require(d, "expected_failure_dimension", "negative_control")),
        expected_failure_reason=str(_require(d, "expected_failure_reason", "negative_control")),
        input_ref=str(_require(d, "input_ref", "negative_control")),
        expected_gate_results=_str_str_map(d.get("expected_gate_results")),
        source_app_config_ref=str(d.get("source_app_config_ref", "")),
        created_at=str(d.get("created_at", "")),
    )


def _list_or_empty(raw: Any, ctx: str) -> list:
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    raise AppDomainContractError(f"{ctx}: expected a list, got {type(raw).__name__}")


def load_bundle_from_dir(domain_contract_dir: Path) -> AppDomainContractBundle:
    """Load all 13 YAML files from ``apps_<name>/config/domain_contract/``.

    Missing optional files (``orchestration_profiles.yaml`` for linear apps)
    are tolerated and produce empty tuples. Missing required files raise
    :class:`AppDomainContractError`.
    """
    if not domain_contract_dir.is_dir():
        raise AppDomainContractError(f"not a directory: {domain_contract_dir}")

    manifest_raw = _read_yaml(domain_contract_dir / "app_domain_manifest.yaml")
    if not isinstance(manifest_raw, dict):
        raise AppDomainContractError(
            f"app_domain_manifest.yaml is missing or malformed in {domain_contract_dir}",
        )

    task_classes_raw = _read_yaml(domain_contract_dir / "task_classes.yaml")
    tcs = tuple(
        _build_task_class(t) for t in _list_or_empty(task_classes_raw, "task_classes")
    )

    input_raw = _read_yaml(domain_contract_dir / "input_contract.yaml")
    if not isinstance(input_raw, dict):
        raise AppDomainContractError("input_contract.yaml is missing or malformed")

    output_raw = _read_yaml(domain_contract_dir / "output_schema.yaml")
    if not isinstance(output_raw, dict):
        raise AppDomainContractError("output_schema.yaml is missing or malformed")

    rubrics_raw = _read_yaml(domain_contract_dir / "eval_rubrics.yaml")
    rubrics = tuple(
        _build_eval_rubric(r) for r in _list_or_empty(rubrics_raw, "eval_rubrics")
    )

    thresholds_raw = _read_yaml(domain_contract_dir / "threshold_profiles.yaml")
    thresholds = tuple(
        _build_threshold_profile(t)
        for t in _list_or_empty(thresholds_raw, "threshold_profiles")
    )

    rosters_raw = _read_yaml(domain_contract_dir / "grader_roster.yaml")
    rosters = tuple(
        _build_grader_roster(r) for r in _list_or_empty(rosters_raw, "grader_roster")
    )

    retrieval_raw = _read_yaml(domain_contract_dir / "retrieval_profiles.yaml")
    retrieval = tuple(
        _build_retrieval_profile(r)
        for r in _list_or_empty(retrieval_raw, "retrieval_profiles")
    )

    prompt_raw = _read_yaml(domain_contract_dir / "prompt_profiles.yaml")
    prompts = tuple(
        _build_prompt_profile(p) for p in _list_or_empty(prompt_raw, "prompt_profiles")
    )

    capability_raw = _read_yaml(domain_contract_dir / "capability_profiles.yaml")
    capabilities = tuple(
        _build_capability_profile(c)
        for c in _list_or_empty(capability_raw, "capability_profiles")
    )

    route_raw = _read_yaml(domain_contract_dir / "route_profiles.yaml")
    routes = tuple(
        _build_route_profile(r) for r in _list_or_empty(route_raw, "route_profiles")
    )

    orch_raw = _read_yaml(domain_contract_dir / "orchestration_profiles.yaml")
    orchestrations = tuple(
        _build_orchestration_profile(o)
        for o in _list_or_empty(orch_raw, "orchestration_profiles")
    )

    fixtures_raw = _read_yaml(domain_contract_dir / "fixtures.yaml")
    fixtures = tuple(
        _build_fixture(f) for f in _list_or_empty(fixtures_raw, "fixtures")
    )

    negatives_raw = _read_yaml(domain_contract_dir / "negative_controls.yaml")
    negatives = tuple(
        _build_negative_control(n)
        for n in _list_or_empty(negatives_raw, "negative_controls")
    )

    bundle = AppDomainContractBundle(
        contract=_build_manifest(manifest_raw, tcs),
        input_contract=_build_input_contract(input_raw),
        output_schema=_build_output_schema(output_raw),
        eval_rubrics=rubrics,
        threshold_profiles=thresholds,
        grader_rosters=rosters,
        retrieval_profiles=retrieval,
        prompt_profiles=prompts,
        capability_profiles=capabilities,
        route_profiles=routes,
        orchestration_profiles=orchestrations,
        fixtures=fixtures,
        negative_controls=negatives,
    )
    return bundle


def discover_app_contract_dirs(repo_root: Path) -> Dict[str, Path]:
    """Return ``{app_id: domain_contract_dir}`` for every apps_* with the dir present."""
    out: Dict[str, Path] = {}
    for child in sorted(repo_root.iterdir()):
        if not child.is_dir():
            continue
        if not child.name.startswith("apps_"):
            continue
        dc_dir = child / "config" / "domain_contract"
        if dc_dir.is_dir() and (dc_dir / "app_domain_manifest.yaml").is_file():
            out[child.name] = dc_dir
    return out


__all__ = [
    "DOMAIN_CONTRACT_FILES",
    "load_bundle_from_dir",
    "discover_app_contract_dirs",
]
