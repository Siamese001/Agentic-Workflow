"""Cluster A — L5 / L4 / UWG governance-state reference module.

Static metadata only. Does not call runtime services, execute tools,
emit OTEL spans, import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

CLUSTER_ID: str = 'A'
CLUSTER_SLUG: str = 'governance_state'

STEP1_REQ_IDS: Tuple[str, ...] = (
    'REQ-L5-AUTHORITY-REGISTRY-BIND-001',
    'REQ-L5-RUNTIME-CERT-BIND-001',
    'REQ-L5-GUARDRAIL-FAMILIES-001',
    'REQ-L5-GOV-CONTEXT-INVARIANT-001',
    'REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001',
    'REQ-L4-POLICY-BLUEPRINT-STATE-001',
    'REQ-GATE-LAYER-INVOCATION-MAP-001',
)

EXPECTED_FAIL_REASONS: Dict[str, str] = {
    'REQ-L5-AUTHORITY-REGISTRY-BIND-001': 'L5_AUTHORITY_REGISTRY_BIND_REQUIRED',
    'REQ-L5-RUNTIME-CERT-BIND-001': 'L5_RUNTIME_CERT_BIND_MISSING',
    'REQ-L5-GUARDRAIL-FAMILIES-001': 'L5_GUARDRAIL_FAMILY_MISSING',
    'REQ-L5-GOV-CONTEXT-INVARIANT-001': 'L5_GOV_CONTEXT_DRIFT_DETECTED',
    'REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001': 'UWG_DURABLE_WRITE_CTX_VIOLATION',
    'REQ-L4-POLICY-BLUEPRINT-STATE-001': 'L4_POLICY_BLUEPRINT_MUTATION_REJECTED',
    'REQ-GATE-LAYER-INVOCATION-MAP-001': 'GATE_LAYER_INVOCATION_MAP_MISSING',
}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-L5-AUTHORITY-REGISTRY-BIND-001': ('tier4.l5.authority_registry_bind',),
    'REQ-L5-RUNTIME-CERT-BIND-001': ('tier4.l5.runtime_cert_bind',),
    'REQ-L5-GUARDRAIL-FAMILIES-001': ('tier4.l5.guardrail_families',),
    'REQ-L5-GOV-CONTEXT-INVARIANT-001': ('tier4.l5.gov_context_invariant',),
    'REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001': ('tier4.l4.uwg_durable_write_ctx_invariant',),
    'REQ-L4-POLICY-BLUEPRINT-STATE-001': ('tier4.l4.policy_blueprint_state',),
    'REQ-GATE-LAYER-INVOCATION-MAP-001': ('tier4.rg.layer_invocation_map',),
}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {
    'REQ-L5-AUTHORITY-REGISTRY-BIND-001': 'negative_control_l5_authority_registry_bind_blocked',
    'REQ-L5-RUNTIME-CERT-BIND-001': 'negative_control_l5_runtime_cert_bind_blocked',
    'REQ-L5-GUARDRAIL-FAMILIES-001': 'negative_control_l5_guardrail_families_blocked',
    'REQ-L5-GOV-CONTEXT-INVARIANT-001': 'negative_control_l5_gov_context_invariant_blocked',
    'REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001': 'negative_control_uwg_durable_write_ctx_invariant_blocked',
    'REQ-L4-POLICY-BLUEPRINT-STATE-001': 'negative_control_l4_policy_blueprint_state_blocked',
    'REQ-GATE-LAYER-INVOCATION-MAP-001': 'negative_control_gate_layer_invocation_map_blocked',
}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-L5-AUTHORITY-REGISTRY-BIND-001': ('authority_registry_bound',),
    'REQ-L5-RUNTIME-CERT-BIND-001': ('runtime_cert_bound',),
    'REQ-L5-GUARDRAIL-FAMILIES-001': ('guardrail_family_declared',),
    'REQ-L5-GOV-CONTEXT-INVARIANT-001': ('governance_context_preserved',),
    'REQ-UWG-DURABLE-WRITE-CTX-INVARIANT-001': ('durable_write_context_preserved',),
    'REQ-L4-POLICY-BLUEPRINT-STATE-001': ('policy_blueprint_state_bound',),
    'REQ-GATE-LAYER-INVOCATION-MAP-001': ('layer_invocation_map_validated',),
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

