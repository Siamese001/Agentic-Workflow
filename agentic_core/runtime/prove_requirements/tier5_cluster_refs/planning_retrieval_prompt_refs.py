"""Cluster B -- U0 / L1 / L3 / C0 / PA planning, retrieval, prompt reference module.

Static metadata only. Does not call runtime services, execute tools,
emit OTEL spans, import an OTEL exporter, or mutate runtime state.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

CLUSTER_ID: str = 'B'

STEP1_REQ_IDS: Tuple[str, ...] = (
    'REQ-U0-TRANSPORT-ENVELOPE-001',
    'REQ-U0-DATA-LABELING-001',
    'REQ-U0-REJECTION-PATH-001',
    'REQ-L1-CONTEXTUAL-REFINEMENT-001',
    'REQ-L1-DRAFT-PLAN-ROUTE-HINTS-001',
    'REQ-L3-CONCURRENCY-FALLBACK-001',
    'REQ-L3-STEP-READINESS-LEDGER-001',
    'REQ-C0-SHAPE-RERANK-STRATIFY-001',
    'REQ-PA-SLOT-COMPOSITION-001',
)

EXPECTED_FAIL_REASONS: Dict[str, str] = {
    'REQ-U0-TRANSPORT-ENVELOPE-001': 'U0_TRANSPORT_ENVELOPE_REJECTED',
    'REQ-U0-DATA-LABELING-001': 'U0_DATA_LABELING_MISSING',
    'REQ-U0-REJECTION-PATH-001': 'U0_REJECTION_PATH_VIOLATION',
    'REQ-L1-CONTEXTUAL-REFINEMENT-001': 'L1_CONTEXTUAL_REFINEMENT_DRIFT_DETECTED',
    'REQ-L1-DRAFT-PLAN-ROUTE-HINTS-001': 'L1_DRAFT_PLAN_ROUTE_HINTS_REJECTED',
    'REQ-L3-CONCURRENCY-FALLBACK-001': 'L3_CONCURRENCY_FALLBACK_REJECTED',
    'REQ-L3-STEP-READINESS-LEDGER-001': 'L3_STEP_READINESS_LEDGER_VIOLATION',
    'REQ-C0-SHAPE-RERANK-STRATIFY-001': 'C0_SHAPE_RERANK_STRATIFY_DRIFT_DETECTED',
    'REQ-PA-SLOT-COMPOSITION-001': 'PA_SLOT_COMPOSITION_REJECTED',
}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-U0-TRANSPORT-ENVELOPE-001': ('tier5.u0.transport_envelope',),
    'REQ-U0-DATA-LABELING-001': ('tier5.u0.data_labeling',),
    'REQ-U0-REJECTION-PATH-001': ('tier5.u0.rejection_path',),
    'REQ-L1-CONTEXTUAL-REFINEMENT-001': ('tier5.l1.contextual_refinement',),
    'REQ-L1-DRAFT-PLAN-ROUTE-HINTS-001': ('tier5.l1.draft_plan_route_hints',),
    'REQ-L3-CONCURRENCY-FALLBACK-001': ('tier5.l3.concurrency_fallback',),
    'REQ-L3-STEP-READINESS-LEDGER-001': ('tier5.l3.step_readiness_ledger',),
    'REQ-C0-SHAPE-RERANK-STRATIFY-001': ('tier5.c0.shape_rerank_stratify',),
    'REQ-PA-SLOT-COMPOSITION-001': ('tier5.pa.slot_composition',),
}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {
    'REQ-U0-TRANSPORT-ENVELOPE-001': 'negative_control_u0_transport_envelope_blocked',
    'REQ-U0-DATA-LABELING-001': 'negative_control_u0_data_labeling_blocked',
    'REQ-U0-REJECTION-PATH-001': 'negative_control_u0_rejection_path_blocked',
    'REQ-L1-CONTEXTUAL-REFINEMENT-001': 'negative_control_l1_contextual_refinement_blocked',
    'REQ-L1-DRAFT-PLAN-ROUTE-HINTS-001': 'negative_control_l1_draft_plan_route_hints_blocked',
    'REQ-L3-CONCURRENCY-FALLBACK-001': 'negative_control_l3_concurrency_fallback_blocked',
    'REQ-L3-STEP-READINESS-LEDGER-001': 'negative_control_l3_step_readiness_ledger_blocked',
    'REQ-C0-SHAPE-RERANK-STRATIFY-001': 'negative_control_c0_shape_rerank_stratify_blocked',
    'REQ-PA-SLOT-COMPOSITION-001': 'negative_control_pa_slot_composition_blocked',
}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-U0-TRANSPORT-ENVELOPE-001': ('transport_envelope_validated',),
    'REQ-U0-DATA-LABELING-001': ('data_labeling_applied',),
    'REQ-U0-REJECTION-PATH-001': ('rejection_path_taken',),
    'REQ-L1-CONTEXTUAL-REFINEMENT-001': ('contextual_refinement_applied',),
    'REQ-L1-DRAFT-PLAN-ROUTE-HINTS-001': ('draft_plan_route_hints_present',),
    'REQ-L3-CONCURRENCY-FALLBACK-001': ('concurrency_fallback_declared',),
    'REQ-L3-STEP-READINESS-LEDGER-001': ('step_readiness_ledger_recorded',),
    'REQ-C0-SHAPE-RERANK-STRATIFY-001': ('shape_rerank_stratify_applied',),
    'REQ-PA-SLOT-COMPOSITION-001': ('slot_composition_validated',),
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
