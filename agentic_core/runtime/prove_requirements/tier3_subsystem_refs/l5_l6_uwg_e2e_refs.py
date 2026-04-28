"""Tier 3 subsystem reference module -- Batch 3 -- L5 / L6 / UWG / E2E.

Static contract for 5 Tier 3 non-RuntimeGates rows. Static metadata
only. Does not call runtime services, execute tools, emit OTEL spans,
import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

STEP1_REQ_IDS: Tuple[str, ...] = ('REQ-L6-OBS-ANTI-BYPASS-001', 'REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001', 'REQ-L5-REPLAY-AUDIT-CERT-001', 'REQ-L5-EGRESS-PROVIDER-GOV-001', 'REQ-E2E-FIXTURES-REPLAY-HARNESS-001')

EXPECTED_FAIL_REASONS: Dict[str, str] = {'REQ-L6-OBS-ANTI-BYPASS-001': 'L6_OBS_BYPASS_BLOCKED', 'REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001': 'UWG_AUDIT_REPLAY_MISMATCH', 'REQ-L5-REPLAY-AUDIT-CERT-001': 'L5_REPLAY_AUDIT_CERT_MISSING', 'REQ-L5-EGRESS-PROVIDER-GOV-001': 'L5_EGRESS_PROVIDER_GOV_MISSING', 'REQ-E2E-FIXTURES-REPLAY-HARNESS-001': 'E2E_REPLAY_HARNESS_BOUNDARY_BLOCKED'}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {'REQ-L6-OBS-ANTI-BYPASS-001': ('l6.obs.anti_bypass', 'l6.obs.bypass_attempt_rejected'), 'REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001': ('uwg.audit', 'uwg.replay', 'uwg.consistency_check'), 'REQ-L5-REPLAY-AUDIT-CERT-001': ('l5.replay_audit_cert.emit', 'l5.replay_audit_cert.validate'), 'REQ-L5-EGRESS-PROVIDER-GOV-001': ('l5.egress.provider_gov', 'l5.egress.policy_applied'), 'REQ-E2E-FIXTURES-REPLAY-HARNESS-001': ('e2e.fixtures.replay_harness', 'e2e.fixtures.boundary_check')}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {'REQ-L6-OBS-ANTI-BYPASS-001': 'negative_control_l6_obs_bypass_blocked', 'REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001': 'negative_control_uwg_audit_replay_mismatch', 'REQ-L5-REPLAY-AUDIT-CERT-001': 'negative_control_l5_replay_audit_cert_missing', 'REQ-L5-EGRESS-PROVIDER-GOV-001': 'negative_control_l5_egress_provider_gov_missing', 'REQ-E2E-FIXTURES-REPLAY-HARNESS-001': 'negative_control_e2e_replay_harness_boundary_blocked'}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {'REQ-L6-OBS-ANTI-BYPASS-001': ('anti_bypass_check_present', 'bypass_attempt_rejected'), 'REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001': ('audit_replay_consistent', 'replay_observed'), 'REQ-L5-REPLAY-AUDIT-CERT-001': ('replay_audit_cert_present', 'cert_validated'), 'REQ-L5-EGRESS-PROVIDER-GOV-001': ('egress_policy_applied', 'provider_gov_validated'), 'REQ-E2E-FIXTURES-REPLAY-HARNESS-001': ('e2e_fixtures_present', 'replay_harness_referenced')}

SCENARIO_KEY_BY_REQ_ID: Dict[str, str] = {'REQ-L6-OBS-ANTI-BYPASS-001': 'AQ_l6_obs_anti_bypass', 'REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001': 'AR_uwg_audit_replay_consistency', 'REQ-L5-REPLAY-AUDIT-CERT-001': 'AS_l5_replay_audit_cert', 'REQ-L5-EGRESS-PROVIDER-GOV-001': 'AT_l5_egress_provider_gov', 'REQ-E2E-FIXTURES-REPLAY-HARNESS-001': 'AU_e2e_fixtures_replay_harness'}


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
