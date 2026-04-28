"""Tier 3 subsystem reference module -- Batch 1 -- L0 / L1 / U0.

Static contract for 7 Tier 3 non-RuntimeGates rows. Static metadata
only. Does not call runtime services, execute tools, emit OTEL spans,
import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

STEP1_REQ_IDS: Tuple[str, ...] = ('REQ-L0-NO-EXECUTE-001', 'REQ-L0-GROUNDED-ACTION-HANDOFF-001', 'REQ-U0-OBS-REPLAY-001', 'REQ-U0-CHANNEL-VALIDATION-001', 'REQ-L1-OBS-OTEL-001', 'REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001', 'REQ-L1-AMBIGUITY-EVIDENCE-001')

EXPECTED_FAIL_REASONS: Dict[str, str] = {'REQ-L0-NO-EXECUTE-001': 'L0_EXECUTION_BLOCKED', 'REQ-L0-GROUNDED-ACTION-HANDOFF-001': 'L0_GROUNDED_ACTION_HANDOFF_REQUIRED', 'REQ-U0-OBS-REPLAY-001': 'U0_OBS_REPLAY_MISSING', 'REQ-U0-CHANNEL-VALIDATION-001': 'U0_CHANNEL_VALIDATION_REJECTED', 'REQ-L1-OBS-OTEL-001': 'L1_OBS_OTEL_MISSING', 'REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001': 'L1_PLAN_VALIDATION_REQUIRED', 'REQ-L1-AMBIGUITY-EVIDENCE-001': 'L1_AMBIGUITY_EVIDENCE_MISSING'}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {'REQ-L0-NO-EXECUTE-001': ('l0.route.no_execute_assertion', 'l0.boundary.execute_attempt_rejected'), 'REQ-L0-GROUNDED-ACTION-HANDOFF-001': ('l0.handoff.grounded', 'l0.handoff.action', 'l0.handoff.contract'), 'REQ-U0-OBS-REPLAY-001': ('u0.intake.obs_emitted', 'u0.intake.replay_evidence'), 'REQ-U0-CHANNEL-VALIDATION-001': ('u0.intake.channel_validation', 'u0.intake.channel_rejected'), 'REQ-L1-OBS-OTEL-001': ('l1.intent_frame', 'l1.refinement', 'l1.plan_emit'), 'REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001': ('l1.plan_validation', 'l1.self_repair'), 'REQ-L1-AMBIGUITY-EVIDENCE-001': ('l1.ambiguity_register', 'l1.ambiguity_carried_to_contract')}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {'REQ-L0-NO-EXECUTE-001': 'negative_control_l0_execute_blocked', 'REQ-L0-GROUNDED-ACTION-HANDOFF-001': 'negative_control_l0_handoff_missing', 'REQ-U0-OBS-REPLAY-001': 'negative_control_u0_obs_replay_missing', 'REQ-U0-CHANNEL-VALIDATION-001': 'negative_control_u0_unsupported_channel_blocked', 'REQ-L1-OBS-OTEL-001': 'negative_control_l1_obs_otel_missing', 'REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001': 'negative_control_l1_plan_validation_missing', 'REQ-L1-AMBIGUITY-EVIDENCE-001': 'negative_control_l1_ambiguity_evidence_missing'}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {'REQ-L0-NO-EXECUTE-001': ('rejected', 'tool_invocation_count', 'model_invocation_count'), 'REQ-L0-GROUNDED-ACTION-HANDOFF-001': ('handoff_grounded', 'evidence_present', 'dispatch_blocked_when_ungrounded'), 'REQ-U0-OBS-REPLAY-001': ('replay_observed', 'obs_span_emitted_present'), 'REQ-U0-CHANNEL-VALIDATION-001': ('channel_validated', 'invalid_channel_rejected'), 'REQ-L1-OBS-OTEL-001': ('otel_span_declared', 'replay_observed'), 'REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001': ('plan_validation_present', 'self_repair_attempted', 'repaired_or_rejected'), 'REQ-L1-AMBIGUITY-EVIDENCE-001': ('ambiguity_detected', 'evidence_present', 'action_blocked')}

SCENARIO_KEY_BY_REQ_ID: Dict[str, str] = {'REQ-L0-NO-EXECUTE-001': 'AE_l0_no_execute', 'REQ-L0-GROUNDED-ACTION-HANDOFF-001': 'AF_l0_grounded_action_handoff', 'REQ-U0-OBS-REPLAY-001': 'AG_u0_obs_replay', 'REQ-U0-CHANNEL-VALIDATION-001': 'AH_u0_channel_validation', 'REQ-L1-OBS-OTEL-001': 'AI_l1_obs_otel', 'REQ-L1-PLAN-VALIDATION-SELF-REPAIR-001': 'AJ_l1_plan_validation_self_repair', 'REQ-L1-AMBIGUITY-EVIDENCE-001': 'AK_l1_ambiguity_evidence'}


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
