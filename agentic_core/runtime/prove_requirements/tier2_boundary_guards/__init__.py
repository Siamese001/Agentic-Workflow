"""Tier 2 boundary-guard reference modules.

Static reference/validator metadata declaring the boundary contract for
Tier 2 Batch D/E REQ_IDs (no-retrieval, no-execute, retrieval-surface
read-only). Each module exposes STEP1_REQ_ID, EXPECTED_FAIL_REASON,
GUARD_NAME, FORBIDDEN_CAPABILITIES, ALLOWED_OUTPUTS,
NEGATIVE_CONTROL_NAME, and a pure validate_boundary_contract function.

These modules do not call runtime services, do not perform retrieval,
do not execute tools, and do not mutate runtime state.
"""
