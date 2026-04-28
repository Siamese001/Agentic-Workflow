"""Tier 6 -- 6 MUST / RELEASE_BLOCKING rows static reference module.

Static metadata only. Does not call runtime services, execute tools,
emit OTEL spans, import an OTEL exporter, or mutate runtime state.

Covers the 6 final-tier MUST requirements for which deterministic
trace + replay + negative-control fixtures are produced (scenarios
CT..CY). The 15 NON_BLOCKING_REFERENCE rows live in
``reference_only_policy_refs`` instead and are governed by the
reference-only policy (no runtime fixtures).
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

CLUSTER_ID: str = "M"  # M = MUST

STEP1_REQ_IDS: Tuple[str, ...] = (
    "REQ-C0-WEAK-SUPPORT-REFINEMENT-001",
    "REQ-E2E-ACCEPTANCE-COMMANDS-001",
    "REQ-E2E-GOLDEN-PATH-001",
    "REQ-E2E-ROUTE-PATH-COVERAGE-001",
    "REQ-EXIT-RUNTIME-TO-REGRESSION-001",
    "REQ-L6-HUMAN-CALIBRATION-001",
)

EXPECTED_FAIL_REASONS: Dict[str, str] = {
    "REQ-C0-WEAK-SUPPORT-REFINEMENT-001": "C0_WEAK_SUPPORT_REFINEMENT_REQUIRED",
    "REQ-E2E-ACCEPTANCE-COMMANDS-001": "E2E_ACCEPTANCE_COMMANDS_MISSING",
    "REQ-E2E-GOLDEN-PATH-001": "E2E_GOLDEN_PATH_MISSING",
    "REQ-E2E-ROUTE-PATH-COVERAGE-001": "E2E_ROUTE_PATH_COVERAGE_MISSING",
    "REQ-EXIT-RUNTIME-TO-REGRESSION-001": "EXIT_RUNTIME_TO_REGRESSION_MISSING",
    "REQ-L6-HUMAN-CALIBRATION-001": "L6_HUMAN_CALIBRATION_MISSING",
}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    "REQ-C0-WEAK-SUPPORT-REFINEMENT-001": ("tier6.c0.weak_support_refinement",),
    "REQ-E2E-ACCEPTANCE-COMMANDS-001": ("tier6.e2e.acceptance_commands",),
    "REQ-E2E-GOLDEN-PATH-001": ("tier6.e2e.golden_path",),
    "REQ-E2E-ROUTE-PATH-COVERAGE-001": ("tier6.e2e.route_path_coverage",),
    "REQ-EXIT-RUNTIME-TO-REGRESSION-001": ("tier6.exit.runtime_to_regression",),
    "REQ-L6-HUMAN-CALIBRATION-001": ("tier6.l6.human_calibration",),
}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {
    "REQ-C0-WEAK-SUPPORT-REFINEMENT-001": "negative_control_c0_weak_support_refinement_blocked",
    "REQ-E2E-ACCEPTANCE-COMMANDS-001": "negative_control_e2e_acceptance_commands_blocked",
    "REQ-E2E-GOLDEN-PATH-001": "negative_control_e2e_golden_path_blocked",
    "REQ-E2E-ROUTE-PATH-COVERAGE-001": "negative_control_e2e_route_path_coverage_blocked",
    "REQ-EXIT-RUNTIME-TO-REGRESSION-001": "negative_control_exit_runtime_to_regression_blocked",
    "REQ-L6-HUMAN-CALIBRATION-001": "negative_control_l6_human_calibration_blocked",
}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    "REQ-C0-WEAK-SUPPORT-REFINEMENT-001": ("weak_support_refinement_required",),
    "REQ-E2E-ACCEPTANCE-COMMANDS-001": ("acceptance_commands_declared",),
    "REQ-E2E-GOLDEN-PATH-001": ("golden_path_validated",),
    "REQ-E2E-ROUTE-PATH-COVERAGE-001": ("route_path_coverage_validated",),
    "REQ-EXIT-RUNTIME-TO-REGRESSION-001": ("runtime_to_regression_recorded",),
    "REQ-L6-HUMAN-CALIBRATION-001": ("human_calibration_required",),
}


def validate_contract(req_id: str, payload: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a Tier 6 MUST-row scenario payload against the contract.

    Pure function; no I/O, no runtime, no OTEL. Returns ``(ok, errors)``.
    """
    errors: List[str] = []
    if req_id not in STEP1_REQ_IDS:
        errors.append(f"req_id {req_id!r} not in MUST STEP1_REQ_IDS")
        return (False, errors)
    if payload.get("step1_req_id") != req_id:
        errors.append(f"step1_req_id mismatch: got {payload.get('step1_req_id')!r} expected {req_id!r}")
    expected_efr = EXPECTED_FAIL_REASONS.get(req_id)
    if payload.get("expected_fail_reason") != expected_efr:
        errors.append(
            f"expected_fail_reason mismatch: got "
            f"{payload.get('expected_fail_reason')!r} expected {expected_efr!r}"
        )
    if payload.get("gate_result") != "BLOCKED":
        errors.append(f"gate_result must be BLOCKED, got {payload.get('gate_result')!r}")
    if payload.get("blocker_target") != req_id:
        errors.append(f"blocker_target mismatch: got {payload.get('blocker_target')!r} expected {req_id!r}")
    for fld in REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID.get(req_id, ()):
        if fld not in payload:
            errors.append(f"missing required artifact field: {fld}")
        elif payload[fld] is not True:
            errors.append(f"artifact field {fld} must be True, got {payload[fld]!r}")
    spans = payload.get("spans") or []
    expected_spans = SPAN_NAMES_BY_REQ_ID.get(req_id, ())
    for span in expected_spans:
        if span not in spans:
            errors.append(f"missing OTEL span name in spans list: {span}")
    return (not errors, errors)
