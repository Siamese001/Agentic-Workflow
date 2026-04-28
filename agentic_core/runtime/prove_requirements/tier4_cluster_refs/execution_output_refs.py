"""Cluster C — C0 / PA / L2 / Exit / L6 / E2E execution-output reference module.

Static metadata only. Does not call runtime services, execute tools,
emit OTEL spans, import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

CLUSTER_ID: str = 'C'
CLUSTER_SLUG: str = 'execution_output'

STEP1_REQ_IDS: Tuple[str, ...] = (
    'REQ-C0-RETRIEVAL-PLAN-001',
    'REQ-PA-LOAD-RESOLVE-BOM-001',
    'REQ-PA-TOKEN-BUDGET-DETERMINISM-001',
    'REQ-L2-E1-FROZEN-ROOM-001',
    'REQ-L2-E5-SEAL-DISPATCH-001',
    'REQ-L2-SEQUENCER-CONTRACT-001',
    'REQ-EXIT-HITL-FREEZE-001',
    'REQ-L6-RUNTIME-EXHAUST-INGEST-001',
    'REQ-E2E-EVIDENCE-GROUNDEDNESS-001',
)

EXPECTED_FAIL_REASONS: Dict[str, str] = {
    'REQ-C0-RETRIEVAL-PLAN-001': 'C0_RETRIEVAL_PLAN_VIOLATION',
    'REQ-PA-LOAD-RESOLVE-BOM-001': 'PA_BOM_RESOLUTION_REJECTED',
    'REQ-PA-TOKEN-BUDGET-DETERMINISM-001': 'PA_TOKEN_BUDGET_DRIFT_DETECTED',
    'REQ-L2-E1-FROZEN-ROOM-001': 'L2_FROZEN_ROOM_MUTATION_REJECTED',
    'REQ-L2-E5-SEAL-DISPATCH-001': 'L2_SEAL_DISPATCH_VIOLATION',
    'REQ-L2-SEQUENCER-CONTRACT-001': 'L2_SEQUENCER_CONTRACT_VIOLATION',
    'REQ-EXIT-HITL-FREEZE-001': 'EXIT_HITL_FREEZE_BYPASS_BLOCKED',
    'REQ-L6-RUNTIME-EXHAUST-INGEST-001': 'L6_RUNTIME_EXHAUST_INGEST_LOSSY',
    'REQ-E2E-EVIDENCE-GROUNDEDNESS-001': 'E2E_EVIDENCE_GROUNDEDNESS_MISSING',
}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-C0-RETRIEVAL-PLAN-001': ('tier4.c0.retrieval_plan',),
    'REQ-PA-LOAD-RESOLVE-BOM-001': ('tier4.pa.load_resolve_bom',),
    'REQ-PA-TOKEN-BUDGET-DETERMINISM-001': ('tier4.pa.token_budget_determinism',),
    'REQ-L2-E1-FROZEN-ROOM-001': ('tier4.l2.e1_frozen_room',),
    'REQ-L2-E5-SEAL-DISPATCH-001': ('tier4.l2.e5_seal_dispatch',),
    'REQ-L2-SEQUENCER-CONTRACT-001': ('tier4.l2.sequencer_contract',),
    'REQ-EXIT-HITL-FREEZE-001': ('tier4.exit.hitl_freeze',),
    'REQ-L6-RUNTIME-EXHAUST-INGEST-001': ('tier4.l6.runtime_exhaust_ingest',),
    'REQ-E2E-EVIDENCE-GROUNDEDNESS-001': ('tier4.e2e.evidence_groundedness',),
}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {
    'REQ-C0-RETRIEVAL-PLAN-001': 'negative_control_c0_retrieval_plan_blocked',
    'REQ-PA-LOAD-RESOLVE-BOM-001': 'negative_control_pa_load_resolve_bom_blocked',
    'REQ-PA-TOKEN-BUDGET-DETERMINISM-001': 'negative_control_pa_token_budget_determinism_blocked',
    'REQ-L2-E1-FROZEN-ROOM-001': 'negative_control_l2_e1_frozen_room_blocked',
    'REQ-L2-E5-SEAL-DISPATCH-001': 'negative_control_l2_e5_seal_dispatch_blocked',
    'REQ-L2-SEQUENCER-CONTRACT-001': 'negative_control_l2_sequencer_contract_blocked',
    'REQ-EXIT-HITL-FREEZE-001': 'negative_control_exit_hitl_freeze_blocked',
    'REQ-L6-RUNTIME-EXHAUST-INGEST-001': 'negative_control_l6_runtime_exhaust_ingest_blocked',
    'REQ-E2E-EVIDENCE-GROUNDEDNESS-001': 'negative_control_e2e_evidence_groundedness_blocked',
}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-C0-RETRIEVAL-PLAN-001': ('retrieval_plan_declared',),
    'REQ-PA-LOAD-RESOLVE-BOM-001': ('prompt_bom_resolved',),
    'REQ-PA-TOKEN-BUDGET-DETERMINISM-001': ('token_budget_deterministic',),
    'REQ-L2-E1-FROZEN-ROOM-001': ('frozen_room_entered',),
    'REQ-L2-E5-SEAL-DISPATCH-001': ('dispatch_sealed',),
    'REQ-L2-SEQUENCER-CONTRACT-001': ('sequencer_contract_declared',),
    'REQ-EXIT-HITL-FREEZE-001': ('hitl_freeze_applied',),
    'REQ-L6-RUNTIME-EXHAUST-INGEST-001': ('runtime_exhaust_ingested',),
    'REQ-E2E-EVIDENCE-GROUNDEDNESS-001': ('evidence_groundedness_validated',),
}

def validate_contract(req_id: str, payload: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a Tier 4 scenario payload against this cluster's contract.

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
            f"gate_result mismatch: got {payload.get('gate_result')!r} expected 'BLOCKED'"
        )
    for f in REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID.get(req_id, ()):
        if f not in payload:
            errors.append(f"missing required artifact field: {f}")
        elif payload.get(f) is not True:
            errors.append(f"required field {f!r} must be exactly True")
    if not payload.get("invariant_digest"):
        errors.append("invariant_digest missing")
    if not payload.get("evidence_refs"):
        errors.append("evidence_refs missing or empty")
    if not payload.get("blocker_target"):
        errors.append("blocker_target missing")
    return (not errors, errors)


__all__ = [
    "CLUSTER_ID",
    "CLUSTER_SLUG",
    "STEP1_REQ_IDS",
    "EXPECTED_FAIL_REASONS",
    "SPAN_NAMES_BY_REQ_ID",
    "NEGATIVE_CONTROL_BY_REQ_ID",
    "REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID",
    "validate_contract",
]

