"""Tier 3 subsystem reference module -- Batch 2 -- C0 / PA / Exit.

Static contract for 5 Tier 3 non-RuntimeGates rows. Static metadata
only. Does not call runtime services, execute tools, emit OTEL spans,
import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

STEP1_REQ_IDS: Tuple[str, ...] = ('REQ-C0-NO-WRITE-001', 'REQ-C0-PREFLIGHT-GROUNDING-001', 'REQ-C0-GRAPH-RAG-001', 'REQ-PA-VALIDATE-SLOT-CONTRACT-001', 'REQ-EXIT-X1A-X1F-CHECKS-001')

EXPECTED_FAIL_REASONS: Dict[str, str] = {'REQ-C0-NO-WRITE-001': 'C0_DURABLE_WRITE_BLOCKED', 'REQ-C0-PREFLIGHT-GROUNDING-001': 'C0_PREFLIGHT_GROUNDING_REQUIRED', 'REQ-C0-GRAPH-RAG-001': 'C0_GRAPH_RAG_BOUNDS_VIOLATION', 'REQ-PA-VALIDATE-SLOT-CONTRACT-001': 'PA_SLOT_CONTRACT_VIOLATION', 'REQ-EXIT-X1A-X1F-CHECKS-001': 'EXIT_X1A_X1F_CHECKS_REQUIRED'}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {'REQ-C0-NO-WRITE-001': ('c0.write_attempt', 'c0.write_rejected'), 'REQ-C0-PREFLIGHT-GROUNDING-001': ('c0.preflight.grounding', 'c0.preflight.evidence'), 'REQ-C0-GRAPH-RAG-001': ('c0.graph_rag.invocation', 'c0.graph_rag.surface_check'), 'REQ-PA-VALIDATE-SLOT-CONTRACT-001': ('pa.slot_contract.validation', 'pa.slot_contract.violation_rejected'), 'REQ-EXIT-X1A-X1F-CHECKS-001': ('exit.x1a', 'exit.x1b', 'exit.x1c', 'exit.x1d', 'exit.x1e', 'exit.x1f')}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {'REQ-C0-NO-WRITE-001': 'negative_control_c0_durable_write_blocked', 'REQ-C0-PREFLIGHT-GROUNDING-001': 'negative_control_c0_preflight_grounding_missing', 'REQ-C0-GRAPH-RAG-001': 'negative_control_c0_graph_rag_bounds_violation', 'REQ-PA-VALIDATE-SLOT-CONTRACT-001': 'negative_control_pa_slot_contract_violation', 'REQ-EXIT-X1A-X1F-CHECKS-001': 'negative_control_exit_x1a_x1f_checks_missing'}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {'REQ-C0-NO-WRITE-001': ('no_write_attempt_rejected', 'write_count'), 'REQ-C0-PREFLIGHT-GROUNDING-001': ('preflight_grounding_present', 'grounding_evidence_present'), 'REQ-C0-GRAPH-RAG-001': ('graph_rag_used', 'retrieval_surface_only'), 'REQ-PA-VALIDATE-SLOT-CONTRACT-001': ('slot_contract_validated', 'contract_violation_rejected'), 'REQ-EXIT-X1A-X1F-CHECKS-001': ('exit_checks_applied', 'x1a_x1f_check_ids', 'all_checks_required')}

SCENARIO_KEY_BY_REQ_ID: Dict[str, str] = {'REQ-C0-NO-WRITE-001': 'AL_c0_no_write', 'REQ-C0-PREFLIGHT-GROUNDING-001': 'AM_c0_preflight_grounding', 'REQ-C0-GRAPH-RAG-001': 'AN_c0_graph_rag', 'REQ-PA-VALIDATE-SLOT-CONTRACT-001': 'AO_pa_validate_slot_contract', 'REQ-EXIT-X1A-X1F-CHECKS-001': 'AP_exit_x1a_x1f_checks'}


def validate_contract(req_id: str, payload: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a scenario payload against this batch's contract for ``req_id``.

    Pure function. Checks:
      1. ``req_id`` is in this module's ``STEP1_REQ_IDS``.
      2. ``payload['step1_req_id']`` matches ``req_id``.
      3. ``payload['expected_fail_reason']`` matches the row's mapped EFR.
      4. ``payload['gate_result'] == 'BLOCKED'``.
      5. Every field in ``REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID[req_id]`` is
         present in the payload.
    """
    errors: List[str] = []
    if req_id not in STEP1_REQ_IDS:
        errors.append("req_id " + repr(req_id) + " not in STEP1_REQ_IDS for this module")
        return (False, errors)
    got_rid = payload.get("step1_req_id")
    if got_rid != req_id:
        errors.append("step1_req_id mismatch: got " + repr(got_rid) + " expected " + repr(req_id))
    expected_efr = EXPECTED_FAIL_REASONS[req_id]
    got_efr = payload.get("expected_fail_reason")
    if got_efr != expected_efr:
        errors.append("expected_fail_reason mismatch: got " + repr(got_efr) + " expected " + repr(expected_efr))
    got_gr = payload.get("gate_result")
    if got_gr != "BLOCKED":
        errors.append("gate_result mismatch: got " + repr(got_gr) + " expected 'BLOCKED'")
    for field in REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID[req_id]:
        if field not in payload:
            errors.append("missing required artifact field: " + field)
    return (not errors, errors)


__all__ = [
    "STEP1_REQ_IDS",
    "EXPECTED_FAIL_REASONS",
    "SPAN_NAMES_BY_REQ_ID",
    "NEGATIVE_CONTROL_BY_REQ_ID",
    "REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID",
    "SCENARIO_KEY_BY_REQ_ID",
    "validate_contract",
]
