"""Boundary guard reference — REQ-L1-NO-EXECUTE-001.

Static reference/validator metadata declaring the L1 no-execute
boundary contract: the L1 cognition/planning layer must not invoke
tools or models directly; execution is delegated to L2 only and any
execution attempt at L1 must be rejected with zero tool and model
invocations. This module does not call runtime services, does not
perform retrieval, does not execute tools, and does not mutate
runtime state.
"""

from __future__ import annotations

from typing import Final, List, Tuple

STEP1_REQ_ID: Final[str] = "REQ-L1-NO-EXECUTE-001"
EXPECTED_FAIL_REASON: Final[str] = "L1_EXECUTION_BLOCKED"
GUARD_NAME: Final[str] = "l1_no_execute_guard"
NEGATIVE_CONTROL_NAME: Final[str] = "scenario_V_l1_no_execute"

FORBIDDEN_CAPABILITIES: Final[Tuple[str, ...]] = (
    "tool_invocation",
    "model_invocation",
    "l2_bypass_execute",
    "direct_subprocess_call",
)

ALLOWED_OUTPUTS: Final[Tuple[str, ...]] = (
    "l1_plan_contract",
    "l2_execution_request",
    "plan_handoff_envelope",
)


def validate_boundary_contract(payload: dict) -> Tuple[bool, List[str]]:
    """Return (ok, violations) for an L1 no-execute payload.

    Pure function. Does not execute tools. Does not invoke models.
    """
    violations: List[str] = []
    if not isinstance(payload, dict):
        return False, ["payload_not_mapping"]
    if payload.get("execution_attempted") and not payload.get("rejected"):
        violations.append("execution_attempt_not_rejected")
    tool_count = payload.get("tool_invocation_count")
    if tool_count is None or tool_count != 0:
        violations.append("tool_invocation_count_must_be_zero")
    model_count = payload.get("model_invocation_count")
    if model_count is None or model_count != 0:
        violations.append("model_invocation_count_must_be_zero")
    return (not violations), violations
