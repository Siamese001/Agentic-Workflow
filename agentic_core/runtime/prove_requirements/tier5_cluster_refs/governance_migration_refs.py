"""Cluster A -- L5 governance + L4 migration / state reference module.

Static metadata only. Does not call runtime services, execute tools,
emit OTEL spans, import an OTEL exporter, or mutate runtime state.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

CLUSTER_ID: str = 'A'

STEP1_REQ_IDS: Tuple[str, ...] = (
    'REQ-L5-CAPABILITY-TOKEN-SCHEMA-001',
    'REQ-L5-CROSS-CHILD-CERT-CONSISTENCY-001',
    'REQ-L5-CALIBRATION-ASSURANCE-001',
    'REQ-L4-BLUEPRINT-VERSION-MIGRATION-001',
    'REQ-L4-MEMORY-PROMOTION-STATE-001',
    'REQ-L4-READ-SURFACE-REFRESH-001',
)

EXPECTED_FAIL_REASONS: Dict[str, str] = {
    'REQ-L5-CAPABILITY-TOKEN-SCHEMA-001': 'L5_CAPABILITY_TOKEN_SCHEMA_VIOLATION',
    'REQ-L5-CROSS-CHILD-CERT-CONSISTENCY-001': 'L5_CROSS_CHILD_CERT_INCONSISTENCY',
    'REQ-L5-CALIBRATION-ASSURANCE-001': 'L5_CALIBRATION_ASSURANCE_MISSING',
    'REQ-L4-BLUEPRINT-VERSION-MIGRATION-001': 'L4_BLUEPRINT_VERSION_MIGRATION_REJECTED',
    'REQ-L4-MEMORY-PROMOTION-STATE-001': 'L4_MEMORY_PROMOTION_STATE_VIOLATION',
    'REQ-L4-READ-SURFACE-REFRESH-001': 'L4_READ_SURFACE_REFRESH_REJECTED',
}

SPAN_NAMES_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-L5-CAPABILITY-TOKEN-SCHEMA-001': ('tier5.l5.capability_token_schema',),
    'REQ-L5-CROSS-CHILD-CERT-CONSISTENCY-001': ('tier5.l5.cross_child_cert_consistency',),
    'REQ-L5-CALIBRATION-ASSURANCE-001': ('tier5.l5.calibration_assurance',),
    'REQ-L4-BLUEPRINT-VERSION-MIGRATION-001': ('tier5.l4.blueprint_version_migration',),
    'REQ-L4-MEMORY-PROMOTION-STATE-001': ('tier5.l4.memory_promotion_state',),
    'REQ-L4-READ-SURFACE-REFRESH-001': ('tier5.l4.read_surface_refresh',),
}

NEGATIVE_CONTROL_BY_REQ_ID: Dict[str, str] = {
    'REQ-L5-CAPABILITY-TOKEN-SCHEMA-001': 'negative_control_l5_capability_token_schema_blocked',
    'REQ-L5-CROSS-CHILD-CERT-CONSISTENCY-001': 'negative_control_l5_cross_child_cert_consistency_blocked',
    'REQ-L5-CALIBRATION-ASSURANCE-001': 'negative_control_l5_calibration_assurance_blocked',
    'REQ-L4-BLUEPRINT-VERSION-MIGRATION-001': 'negative_control_l4_blueprint_version_migration_blocked',
    'REQ-L4-MEMORY-PROMOTION-STATE-001': 'negative_control_l4_memory_promotion_state_blocked',
    'REQ-L4-READ-SURFACE-REFRESH-001': 'negative_control_l4_read_surface_refresh_blocked',
}

REQUIRED_ARTIFACT_FIELDS_BY_REQ_ID: Dict[str, Tuple[str, ...]] = {
    'REQ-L5-CAPABILITY-TOKEN-SCHEMA-001': ('capability_token_schema_validated',),
    'REQ-L5-CROSS-CHILD-CERT-CONSISTENCY-001': ('cross_child_cert_consistent',),
    'REQ-L5-CALIBRATION-ASSURANCE-001': ('calibration_assurance_checked',),
    'REQ-L4-BLUEPRINT-VERSION-MIGRATION-001': ('blueprint_version_migration_validated',),
    'REQ-L4-MEMORY-PROMOTION-STATE-001': ('memory_promotion_state_preserved',),
    'REQ-L4-READ-SURFACE-REFRESH-001': ('read_surface_refresh_applied',),
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
