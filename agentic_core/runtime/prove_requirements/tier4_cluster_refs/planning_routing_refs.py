"""Cluster B — U0 / L1 / L0 / L3 planning-routing reference module.

Static metadata only. Does not call runtime services, execute tools,
emit OTEL spans, import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

CLUSTER_ID: str = 'B'
CLUSTER_SLUG: str = 'planning_routing'

STEP1_REQ_IDS: Tuple[str, ...] = (
    'REQ-U0-IDENTITY-TENANT-SESSION-001',
    'REQ-U0-QUOTA-BASELINE-001',
    'REQ-U0-SCHEMA-NORMALIZATION-001',
    'REQ-L1-INTENT-FRAME-001',
    'REQ-L1-PLANNING-PRIORS-001',
    'REQ-L0-ROUTE-INPUT-PREFLIGHT-001',
    'REQ-L0-CACHE-FALLBACK-HITL-001',
    'REQ-L0-ROUTECONTRACT-TELEMETRY-001',
    'REQ-L3-MANAGED-WORKFLOW-001',
)

EXPECTED_FAIL_REASONS: Dict[str, str] = {
    'REQ-U0-IDENTITY-TENANT-SESSION-001': 'U0_IDENTITY_TENANT_SESSION_REQUIRED',
    'REQ-U0-QUOTA-BASELINE-001': 'U0_QUOTA_BASELINE_DRIFT_DETECTED',
    'REQ-U0-SCHEMA-NORMALIZATION-001': 'U0_SCHEMA_NORMALIZATION_REJECTED',
    'REQ-L1-INTENT-FRAME-001': 'L1_INTENT_FRAME_MISSING',
    'REQ-L1-PLANNING-PRIORS-001': 'L1_PLANNING_PRIORS_DRIFT_DETECTED',
    'REQ-L0-ROUTE-INPUT-PREFLIGHT-001': 'L0_ROUTE_INPUT_PREFLIGHT_REJECTED',
    'REQ-L0-CACHE-FALLBACK-HITL-001': 'L0_CACHE_FALLBACK_HITL_VIOLATION',
    'REQ-L0-ROUTECONTRACT-TELEMETRY-001': 'L0_ROUTECONTRACT_TELEMETRY_MISSING',
    'REQ-L3-MANAGED-WORKFLOW-001': 'L3_MANAGED_WORKFLOW_REJECTED',
}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-U0-IDENTITY-TENANT-SESSION-001': ('tier4.u0.identity_tenant_session',),
    'REQ-U0-QUOTA-BASELINE-001': ('tier4.u0.quota_baseline',),
    'REQ-U0-SCHEMA-NORMALIZATION-001': ('tier4.u0.schema_normalization',),
    'REQ-L1-INTENT-FRAME-001': ('tier4.l1.intent_frame',),
    'REQ-L1-PLANNING-PRIORS-001': ('tier4.l1.planning_priors',),
    'REQ-L0-ROUTE-INPUT-PREFLIGHT-001': ('tier4.l0.route_input_preflight',),
    'REQ-L0-CACHE-FALLBACK-HITL-001': ('tier4.l0.cache_fallback_hitl',),
    'REQ-L0-ROUTECONTRACT-TELEMETRY-001': ('tier4.l0.routecontract_telemetry',),
    'REQ-L3-MANAGED-WORKFLOW-001': ('tier4.l3.managed_workflow',),
}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {
    'REQ-U0-IDENTITY-TENANT-SESSION-001': 'negative_control_u0_identity_tenant_session_blocked',
    'REQ-U0-QUOTA-BASELINE-001': 'negative_control_u0_quota_baseline_blocked',
    'REQ-U0-SCHEMA-NORMALIZATION-001': 'negative_control_u0_schema_normalization_blocked',
    'REQ-L1-INTENT-FRAME-001': 'negative_control_l1_intent_frame_blocked',
    'REQ-L1-PLANNING-PRIORS-001': 'negative_control_l1_planning_priors_blocked',
    'REQ-L0-ROUTE-INPUT-PREFLIGHT-001': 'negative_control_l0_route_input_preflight_blocked',
    'REQ-L0-CACHE-FALLBACK-HITL-001': 'negative_control_l0_cache_fallback_hitl_blocked',
    'REQ-L0-ROUTECONTRACT-TELEMETRY-001': 'negative_control_l0_routecontract_telemetry_blocked',
    'REQ-L3-MANAGED-WORKFLOW-001': 'negative_control_l3_managed_workflow_blocked',
}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-U0-IDENTITY-TENANT-SESSION-001': ('identity_tenant_session_validated',),
    'REQ-U0-QUOTA-BASELINE-001': ('quota_baseline_applied',),
    'REQ-U0-SCHEMA-NORMALIZATION-001': ('schema_normalized',),
    'REQ-L1-INTENT-FRAME-001': ('intent_frame_present',),
    'REQ-L1-PLANNING-PRIORS-001': ('planning_priors_applied',),
    'REQ-L0-ROUTE-INPUT-PREFLIGHT-001': ('route_input_preflight_validated',),
    'REQ-L0-CACHE-FALLBACK-HITL-001': ('cache_fallback_hitl_declared',),
    'REQ-L0-ROUTECONTRACT-TELEMETRY-001': ('routecontract_telemetry_emitted',),
    'REQ-L3-MANAGED-WORKFLOW-001': ('managed_workflow_contract_declared',),
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

