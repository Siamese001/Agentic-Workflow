"""Boundary guard reference — REQ-L4-RETRIEVAL-SURFACE-001.

Static reference/validator metadata declaring the L4 retrieval surface
boundary contract: the surface is read-only and any non-UWG mutation
attempt against it must be rejected. This module does not call runtime
services, does not perform retrieval, does not execute tools, and does
not mutate runtime state.
"""

from __future__ import annotations

from typing import Final, List, Tuple

STEP1_REQ_ID: Final[str] = "REQ-L4-RETRIEVAL-SURFACE-001"
EXPECTED_FAIL_REASON: Final[str] = "L4_RETRIEVAL_SURFACE_VIOLATION"
GUARD_NAME: Final[str] = "l4_retrieval_surface_guard"
NEGATIVE_CONTROL_NAME: Final[str] = "scenario_S_l4_retrieval_surface"

FORBIDDEN_CAPABILITIES: Final[Tuple[str, ...]] = (
    "non_uwg_mutation",
    "direct_write_bypass",
    "ad_hoc_index_rewrite",
    "non_canonical_store_write",
)

ALLOWED_OUTPUTS: Final[Tuple[str, ...]] = (
    "retrieval_read_response",
    "retrieval_surface_read_only_attestation",
    "uwg_mediated_write_receipt",
)


def validate_boundary_contract(payload: dict) -> Tuple[bool, List[str]]:
    """Return (ok, violations) for an L4 retrieval surface payload.

    Pure function. Does not perform retrieval. Does not execute tools.
    Does not mutate runtime state.
    """
    violations: List[str] = []
    if not isinstance(payload, dict):
        return False, ["payload_not_mapping"]
    if payload.get("retrieval_surface_read_only") is not True:
        violations.append("retrieval_surface_not_read_only")
    if payload.get("non_uwg_mutation_attempted") and not payload.get("rejected"):
        violations.append("non_uwg_mutation_not_rejected")
    return (not violations), violations
