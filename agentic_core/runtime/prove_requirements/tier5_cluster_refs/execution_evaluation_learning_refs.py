"""Cluster C -- L2 execution / Exit evaluation / L6 learning reference module.

Static metadata only. Does not call runtime services, execute tools,
emit OTEL spans, import an OTEL exporter, or mutate runtime state.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

CLUSTER_ID: str = 'C'

STEP1_REQ_IDS: Tuple[str, ...] = (
    'REQ-L2-E2-VALID-WORK-ORDER-001',
    'REQ-L2-E3-EXEC-LANES-SANDBOX-001',
    'REQ-L2-E4-HEAL-SAME-AUTHORITY-001',
    'REQ-L2-RESOLUTION-CONTEXT-INVARIANT-001',
    'REQ-EXIT-INPUT-NORMALIZATION-001',
    'REQ-EXIT-GRADER-COMPOSITION-001',
    'REQ-EXIT-RETURN-RESPONSE-001',
    'REQ-L6-OUTCOME-TRAJECTORY-001',
    'REQ-L6-PROPOSAL-ADMISSION-001',
    'REQ-L6-MEMORY-PROMOTION-IFACE-001',
)

EXPECTED_FAIL_REASONS: Dict[str, str] = {
    'REQ-L2-E2-VALID-WORK-ORDER-001': 'L2_VALID_WORK_ORDER_REJECTED',
    'REQ-L2-E3-EXEC-LANES-SANDBOX-001': 'L2_EXEC_LANES_SANDBOX_VIOLATION',
    'REQ-L2-E4-HEAL-SAME-AUTHORITY-001': 'L2_HEAL_AUTHORITY_DRIFT_DETECTED',
    'REQ-L2-RESOLUTION-CONTEXT-INVARIANT-001': 'L2_RESOLUTION_CONTEXT_VIOLATION',
    'REQ-EXIT-INPUT-NORMALIZATION-001': 'EXIT_INPUT_NORMALIZATION_REJECTED',
    'REQ-EXIT-GRADER-COMPOSITION-001': 'EXIT_GRADER_COMPOSITION_VIOLATION',
    'REQ-EXIT-RETURN-RESPONSE-001': 'EXIT_RETURN_RESPONSE_DISPOSITION_MISSING',
    'REQ-L6-OUTCOME-TRAJECTORY-001': 'L6_OUTCOME_TRAJECTORY_VIOLATION',
    'REQ-L6-PROPOSAL-ADMISSION-001': 'L6_PROPOSAL_ADMISSION_REJECTED',
    'REQ-L6-MEMORY-PROMOTION-IFACE-001': 'L6_MEMORY_PROMOTION_IFACE_VIOLATION',
}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-L2-E2-VALID-WORK-ORDER-001': ('tier5.l2.e2_valid_work_order',),
    'REQ-L2-E3-EXEC-LANES-SANDBOX-001': ('tier5.l2.e3_exec_lanes_sandbox',),
    'REQ-L2-E4-HEAL-SAME-AUTHORITY-001': ('tier5.l2.e4_heal_same_authority',),
    'REQ-L2-RESOLUTION-CONTEXT-INVARIANT-001': ('tier5.l2.resolution_context_invariant',),
    'REQ-EXIT-INPUT-NORMALIZATION-001': ('tier5.exit.input_normalization',),
    'REQ-EXIT-GRADER-COMPOSITION-001': ('tier5.exit.grader_composition',),
    'REQ-EXIT-RETURN-RESPONSE-001': ('tier5.exit.return_response',),
    'REQ-L6-OUTCOME-TRAJECTORY-001': ('tier5.l6.outcome_trajectory',),
    'REQ-L6-PROPOSAL-ADMISSION-001': ('tier5.l6.proposal_admission',),
    'REQ-L6-MEMORY-PROMOTION-IFACE-001': ('tier5.l6.memory_promotion_iface',),
}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {
    'REQ-L2-E2-VALID-WORK-ORDER-001': 'negative_control_l2_e2_valid_work_order_blocked',
    'REQ-L2-E3-EXEC-LANES-SANDBOX-001': 'negative_control_l2_e3_exec_lanes_sandbox_blocked',
    'REQ-L2-E4-HEAL-SAME-AUTHORITY-001': 'negative_control_l2_e4_heal_same_authority_blocked',
    'REQ-L2-RESOLUTION-CONTEXT-INVARIANT-001': 'negative_control_l2_resolution_context_invariant_blocked',
    'REQ-EXIT-INPUT-NORMALIZATION-001': 'negative_control_exit_input_normalization_blocked',
    'REQ-EXIT-GRADER-COMPOSITION-001': 'negative_control_exit_grader_composition_blocked',
    'REQ-EXIT-RETURN-RESPONSE-001': 'negative_control_exit_return_response_blocked',
    'REQ-L6-OUTCOME-TRAJECTORY-001': 'negative_control_l6_outcome_trajectory_blocked',
    'REQ-L6-PROPOSAL-ADMISSION-001': 'negative_control_l6_proposal_admission_blocked',
    'REQ-L6-MEMORY-PROMOTION-IFACE-001': 'negative_control_l6_memory_promotion_iface_blocked',
}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-L2-E2-VALID-WORK-ORDER-001': ('valid_work_order_present',),
    'REQ-L2-E3-EXEC-LANES-SANDBOX-001': ('exec_lane_sandbox_enforced',),
    'REQ-L2-E4-HEAL-SAME-AUTHORITY-001': ('heal_same_authority_enforced',),
    'REQ-L2-RESOLUTION-CONTEXT-INVARIANT-001': ('resolution_context_preserved',),
    'REQ-EXIT-INPUT-NORMALIZATION-001': ('exit_input_normalized',),
    'REQ-EXIT-GRADER-COMPOSITION-001': ('grader_composition_validated',),
    'REQ-EXIT-RETURN-RESPONSE-001': ('return_response_contract_applied',),
    'REQ-L6-OUTCOME-TRAJECTORY-001': ('outcome_trajectory_recorded',),
    'REQ-L6-PROPOSAL-ADMISSION-001': ('proposal_admission_gated',),
    'REQ-L6-MEMORY-PROMOTION-IFACE-001': ('memory_promotion_iface_used',),
}


def validate_contract(req_id: str, payload: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a Tier 5 scenario payload against this cluster's contract.

    Pure function; no I/O, no runtime, no OTEL. Returns ``(ok, errors)``.
    """
    errors: List[str] = []
    if req_id not in STEP1_REQ_IDS:
        errors.append(f"req_id {req_id!r} not in cluster STEP1_REQ_IDS")
        return (False, errors)
    if payload.get("step1_req_id") != req_id:
        errors.append(
            f"step1_req_id mismatch: got {payload.get('step1_req_id')!r} "
            f"expected {req_id!r}"
        )
    expected_efr = EXPECTED_FAIL_REASONS.get(req_id)
    if payload.get("expected_fail_reason") != expected_efr:
        errors.append(
            f"expected_fail_reason mismatch: got "
            f"{payload.get('expected_fail_reason')!r} expected {expected_efr!r}"
        )
    if payload.get("gate_result") != "BLOCKED":
        errors.append(
            f"gate_result must be BLOCKED, got {payload.get('gate_result')!r}"
        )
    if payload.get("blocker_target") != req_id:
        errors.append(
            f"blocker_target mismatch: got {payload.get('blocker_target')!r} "
            f"expected {req_id!r}"
        )
    for fld in REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID.get(req_id, ()):
        if fld not in payload:
            errors.append(f"missing required artifact field: {fld}")
        elif payload[fld] is not True:
            errors.append(
                f"artifact field {fld} must be True, got {payload[fld]!r}"
            )
    spans = payload.get("spans") or []
    expected_spans = SPAN_NAMES_BY_REQ_ID.get(req_id, ())
    for span in expected_spans:
        if span not in spans:
            errors.append(f"missing OTEL span name in spans list: {span}")
    return (not errors, errors)
