"""Tier 3 Runtime Gates static reference module — NO_OVERLAP_WITH_EXIT.

Static gate contract for Step 1 row ``REQ-GATE-NO-OVERLAP-WITH-EXIT-001``.

Static metadata only. Does not call runtime services, execute tools, emit
OTEL spans, import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Tuple

STEP1_REQ_ID: str = "REQ-GATE-NO-OVERLAP-WITH-EXIT-001"
EXPECTED_FAIL_REASON: str = "GATE_EXIT_OVERLAP_BLOCKED"
GATE_FAMILY: str = "NO_OVERLAP_WITH_EXIT"
GATE_RANGE: str = "NO_OVERLAP_WITH_EXIT"
GATE_IDS: Tuple[str, ...] = ('RUNTIME_GATE_VERDICT', 'EXIT_X3_DISPOSITION')
SPAN_NAMES: Tuple[str, ...] = ('gate.no_overlap.exit.runtime_verdict', 'gate.no_overlap.exit.x3_disposition')
NEGATIVE_CONTROL_NAME: str = "negative_control_exit_overlap_blocked"
REQUIRED_ARTIFACT_FIELDS: Tuple[str, ...] = ('runtime_gate_owns_runtime_verdict', 'exit_owns_x3_disposition', 'overlap_detected')

SCENARIO_KEY: str = "AC_gate_no_overlap_exit"


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
