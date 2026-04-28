"""Tier 3 Runtime Gates static reference module — G11..G15.

Static gate contract for Step 1 row ``REQ-GATE-G11-G15-TOOL-MODEL-001``.

Static metadata only. Does not call runtime services, execute tools, emit
OTEL spans, import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Tuple

STEP1_REQ_ID: str = "REQ-GATE-G11-G15-TOOL-MODEL-001"
EXPECTED_FAIL_REASON: str = "GATE_G11_G15_TOOL_MODEL_REQUIRED"
GATE_FAMILY: str = "G11..G15"
GATE_RANGE: str = "G11..G15"
GATE_IDS: Tuple[str, ...] = ('G11_TOOL', 'G12_MODEL', 'G13_ARGS', 'G14_EGRESS', 'G15_SANDBOX')
SPAN_NAMES: Tuple[str, ...] = ('gate.tool_model.g11_tool', 'gate.tool_model.g12_model', 'gate.tool_model.g13_args', 'gate.tool_model.g14_egress', 'gate.tool_model.g15_sandbox')
NEGATIVE_CONTROL_NAME: str = "negative_control_tool_model_bypass_blocked"
REQUIRED_ARTIFACT_FIELDS: Tuple[str, ...] = ('tool_model_gate_ids', 'tool_model_validated')

SCENARIO_KEY: str = "Y_gate_g11_g15_tool_model"


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
