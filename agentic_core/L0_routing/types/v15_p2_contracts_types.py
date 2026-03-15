"""
Backward compatibility stub for v15_p2_contracts_types module.

Canonical location: agentic_core/L0_routing/types/determinism_contracts_types.py
"""

from __future__ import annotations

from agentic_core.L0_routing.types.determinism_contracts_types import (
    EpisodicMemoryNotQueried,
    ForbiddenInputError,
    RollbackHashMismatch,
    WallClockViolation,
    ast_scan_wall_clock,
    canonical_ast_serialize,
    check_forbidden_input_type,
    check_velocity_threshold,
    create_boundary_snapshot,
    dedupe_check,
    dedupe_sha256,
    enforce_episodic_query_before_planning,
    knowledge_supervisor_check,
    require_manifest_hash_ok,
    validate_execution_input,
    validate_manifest_emission,
    verify_ast_determinism,
    verify_rollback_integrity,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "v15_p2_contracts_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "v15_p2_contracts_types", "p0_governance")
_emit_snapshots_state("p0", "v15_p2_contracts_types", "state_snapshot")

__all__ = [
    "EpisodicMemoryNotQueried",
    "ForbiddenInputError",
    "RollbackHashMismatch",
    "WallClockViolation",
    "ast_scan_wall_clock",
    "canonical_ast_serialize",
    "check_forbidden_input_type",
    "check_velocity_threshold",
    "create_boundary_snapshot",
    "dedupe_check",
    "dedupe_sha256",
    "enforce_episodic_query_before_planning",
    "knowledge_supervisor_check",
    "require_manifest_hash_ok",
    "validate_execution_input",
    "validate_manifest_emission",
    "verify_ast_determinism",
    "verify_rollback_integrity",
]
