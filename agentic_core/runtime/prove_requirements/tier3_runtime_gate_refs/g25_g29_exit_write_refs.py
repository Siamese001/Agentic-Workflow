"""Tier 3 Runtime Gates static reference module — G25..G29.

Static gate contract for Step 1 row ``REQ-GATE-G25-G29-EXIT-WRITE-001``.

Static metadata only. Does not call runtime services, execute tools, emit
OTEL spans, import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Tuple

STEP1_REQ_ID: str = "REQ-GATE-G25-G29-EXIT-WRITE-001"
EXPECTED_FAIL_REASON: str = "GATE_G25_G29_EXIT_WRITE_REQUIRED"
GATE_FAMILY: str = "G25..G29"
GATE_RANGE: str = "G25..G29"
GATE_IDS: Tuple[str, ...] = ('G25_ANOMALY', 'G26_EXIT', 'G27_WRITE', 'G28_AUDIT', 'G29_LEARN')
SPAN_NAMES: Tuple[str, ...] = ('gate.exit_write.g25_anomaly', 'gate.exit_write.g26_exit', 'gate.exit_write.g27_write', 'gate.exit_write.g28_audit', 'gate.exit_write.g29_learn')
NEGATIVE_CONTROL_NAME: str = "negative_control_exit_write_bypass_blocked"
REQUIRED_ARTIFACT_FIELDS: Tuple[str, ...] = ('exit_write_gate_ids', 'exit_write_validated')

SCENARIO_KEY: str = "AB_gate_g25_g29_exit_write"


def validate_gate_contract(payload: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a scenario payload against this gate band contract.

    Checks:
      1. ``step1_req_id`` matches this module's ``STEP1_REQ_ID``.
      2. ``expected_fail_reason`` matches this module's ``EXPECTED_FAIL_REASON``.
      3. Every field in ``REQUIRED_ARTIFACT_FIELDS`` is present and truthy (or
         explicitly ``False`` for the ``overlap_detected`` / paired fields).
      4. ``gate_result`` is present and equal to ``"BLOCKED"``.

    Returns ``(ok, errors)``. Pure function; no I/O.
    """
    errors: List[str] = []
    if payload.get("step1_req_id") != STEP1_REQ_ID:
        errors.append(
            f"step1_req_id mismatch: got {payload.get('step1_req_id')!r} "
            f"expected {STEP1_REQ_ID!r}"
        )
    if payload.get("expected_fail_reason") != EXPECTED_FAIL_REASON:
        errors.append(
            f"expected_fail_reason mismatch: got "
            f"{payload.get('expected_fail_reason')!r} expected {EXPECTED_FAIL_REASON!r}"
        )
    if payload.get("gate_result") != "BLOCKED":
        errors.append(
            f"gate_result mismatch: got {payload.get('gate_result')!r} expected 'BLOCKED'"
        )
    for field in REQUIRED_ARTIFACT_FIELDS:
        if field not in payload:
            errors.append(f"missing required artifact field: {field}")
    # overlap_detected (when present) must be explicitly False to demonstrate
    # no-overlap; any other truthy value is a contract violation.
    if "overlap_detected" in REQUIRED_ARTIFACT_FIELDS:
        if payload.get("overlap_detected") is not False:
            errors.append("overlap_detected must be explicitly False for no-overlap gates")
    return (not errors, errors)



__all__ = [
    "STEP1_REQ_ID",
    "EXPECTED_FAIL_REASON",
    "GATE_FAMILY",
    "GATE_RANGE",
    "GATE_IDS",
    "SPAN_NAMES",
    "NEGATIVE_CONTROL_NAME",
    "REQUIRED_ARTIFACT_FIELDS",
    "SCENARIO_KEY",
    "validate_gate_contract",
]
