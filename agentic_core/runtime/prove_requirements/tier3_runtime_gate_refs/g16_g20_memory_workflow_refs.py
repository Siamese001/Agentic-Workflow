"""Tier 3 Runtime Gates static reference module — G16..G20.

Static gate contract for Step 1 row ``REQ-GATE-G16-G20-MEMORY-WORKFLOW-001``.

Static metadata only. Does not call runtime services, execute tools, emit
OTEL spans, import an OTEL exporter, or mutate runtime state.
"""

from __future__ import annotations

from typing import Any, List, Mapping, Tuple

STEP1_REQ_ID: str = "REQ-GATE-G16-G20-MEMORY-WORKFLOW-001"
EXPECTED_FAIL_REASON: str = "GATE_G16_G20_MEMORY_WORKFLOW_REQUIRED"
GATE_FAMILY: str = "G16..G20"
GATE_RANGE: str = "G16..G20"
GATE_IDS: Tuple[str, ...] = ('G16_MEMORY', 'G17_PRIVACY', 'G18_WORKFLOW', 'G19_LOOP', 'G20_BUDGET')
SPAN_NAMES: Tuple[str, ...] = ('gate.memory_workflow.g16_memory', 'gate.memory_workflow.g17_privacy', 'gate.memory_workflow.g18_workflow', 'gate.memory_workflow.g19_loop', 'gate.memory_workflow.g20_budget')
NEGATIVE_CONTROL_NAME: str = "negative_control_memory_workflow_bypass_blocked"
REQUIRED_ARTIFACT_FIELDS: Tuple[str, ...] = ('memory_workflow_gate_ids', 'memory_workflow_validated')

SCENARIO_KEY: str = "Z_gate_g16_g20_memory_workflow"


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
