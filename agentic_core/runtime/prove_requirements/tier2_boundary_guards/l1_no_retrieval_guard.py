"""Boundary guard reference — REQ-L1-NO-RETRIEVAL-001.

Static reference/validator metadata declaring the L1 no-retrieval
boundary contract: the L1 cognition/planning layer must not attempt
retrieval; retrieval is delegated to C0/C1 surfaces only and any
retrieval attempt at L1 must be rejected and produce zero retrieval
spans. This module does not call runtime services, does not perform
retrieval, does not execute tools, and does not mutate runtime state.
"""

from __future__ import annotations

from typing import Final, List, Tuple

STEP1_REQ_ID: Final[str] = "REQ-L1-NO-RETRIEVAL-001"
EXPECTED_FAIL_REASON: Final[str] = "L1_RETRIEVAL_BLOCKED"
GUARD_NAME: Final[str] = "l1_no_retrieval_guard"
NEGATIVE_CONTROL_NAME: Final[str] = "scenario_U_l1_no_retrieval"

FORBIDDEN_CAPABILITIES: Final[Tuple[str, ...]] = (
    "retrieval_invocation",
    "vector_store_query",
    "knowledge_base_lookup",
    "c0_bypass_retrieval",
)

ALLOWED_OUTPUTS: Final[Tuple[str, ...]] = (
    "l1_plan_contract",
    "plan_handoff_envelope",
    "c0_retrieval_request",
)


def validate_boundary_contract(payload: dict) -> Tuple[bool, List[str]]:
    """Return (ok, violations) for an L1 no-retrieval payload.

    Pure function. Does not perform retrieval.
    """
    violations: List[str] = []
    if not isinstance(payload, dict):
        return False, ["payload_not_mapping"]
    if payload.get("retrieval_attempted") and not payload.get("rejected"):
        violations.append("retrieval_attempt_not_rejected")
    span_count = payload.get("retrieval_span_count")
    if span_count is None or span_count != 0:
        violations.append("retrieval_span_count_must_be_zero")
    return (not violations), violations
