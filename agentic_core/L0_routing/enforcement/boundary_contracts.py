"""
V15 P6 Framework Contracts — Meta-Invariants & Typed Boundaries.

Runtime contracts enforcing P6 (Explicit Boundaries / Zero Trust Between
Layers) invariants required by the V15 Target State audit (Prompt v5.0
Enhanced).

Contract version: 1.0.0
"""

from __future__ import annotations

from agentic_core.L0_routing.types.boundary_types import (
    BoundarySchemaDescriptor,
    ContextRetrievalRequest,
    InvariantCheck,
    InvariantSeverity,
    InvariantViolation,
    MetaInvariantReport,
    SchemaValidationStatus,
    SSOTBinding,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "boundary_contracts")
# =============================================================================
# §1.5 — SSOT Binding Resolution
# =============================================================================


class SSOTBindingError(Exception):
    """Raised when SSOT binding resolution fails."""


def resolve_ssot_binding(
    node_id: str,
    blueprint_registry: dict[str, str],
) -> SSOTBinding:
    """§1.5 — Resolve node_id against the structure blueprint registry.

    blueprint_registry maps node_id -> blueprint_entry.
    Fail-closed: unresolved node_id raises SSOTBindingError.
    """
    if not node_id:
        raise SSOTBindingError("FAIL (P6): node_id must be non-empty")

    entry = blueprint_registry.get(node_id)
    if entry is None:
        raise SSOTBindingError(
            f"FAIL (P6): node_id '{node_id}' does not resolve to any definition in structure_blueprint.",
        )

    return SSOTBinding(node_id=node_id, blueprint_entry=entry, resolved=True)


# =============================================================================
# §3.8 — Context Retrieval Request Validation
# =============================================================================


class ContextRetrievalError(Exception):
    """Raised when context retrieval request validation fails."""


def build_context_retrieval_request(
    trace_id: str,
    query_hash: str,
    semantic_clock_tick: int,
) -> ContextRetrievalRequest:
    """§3.8 — Build a typed context retrieval request (L0→L4)."""
    try:
        return ContextRetrievalRequest(
            trace_id=trace_id,
            query_hash=query_hash,
            semantic_clock_tick=semantic_clock_tick,
        )
    except (ValueError, TypeError) as exc:
        raise ContextRetrievalError(
            f"FAIL (P6): ContextRetrievalRequest construction failed: {exc}",
        ) from exc


def validate_context_retrieval_read_only(
    request: ContextRetrievalRequest,
) -> bool:
    """§3.8 — Validate that the request is read-only. Fail-closed."""
    if not request.read_only:
        raise ContextRetrievalError(
            "FAIL (P6): Context retrieval request must be read-only.",
        )
    return True


# =============================================================================
# §12.1 / §2.4 — Boundary Schema Validation
# =============================================================================


class BoundarySchemaError(Exception):
    """Raised when boundary schema validation fails."""


def validate_boundary_schema(
    descriptor: BoundarySchemaDescriptor,
) -> bool:
    """§12.1 / §2.4 — Validate a boundary schema descriptor. Fail-closed.

    Rejects INVALID or MISSING schemas.
    """
    if not isinstance(descriptor, BoundarySchemaDescriptor):
        raise BoundarySchemaError(
            f"FAIL (P6): Expected BoundarySchemaDescriptor, got {type(descriptor).__name__}",
        )
    if descriptor.validation_status == SchemaValidationStatus.INVALID:
        raise BoundarySchemaError(
            f"FAIL (P6): Boundary schema '{descriptor.schema_id}' "
            f"({descriptor.source_layer}→{descriptor.target_layer}) is INVALID.",
        )
    if descriptor.validation_status == SchemaValidationStatus.MISSING:
        raise BoundarySchemaError(
            f"FAIL (P6): Boundary schema '{descriptor.schema_id}' "
            f"({descriptor.source_layer}→{descriptor.target_layer}) is MISSING.",
        )
    return True


def build_boundary_schema(
    schema_id: str,
    schema_version: str,
    source_layer: str,
    target_layer: str,
    known_schemas: dict[str, str] | None = None,
) -> BoundarySchemaDescriptor:
    """§12.1 / §2.4 — Build a boundary schema descriptor.

    If known_schemas is provided, validates schema_id exists and version matches.
    """
    if known_schemas is not None:
        expected_version = known_schemas.get(schema_id)
        if expected_version is None:
            return BoundarySchemaDescriptor(
                schema_id=schema_id,
                schema_version=schema_version,
                source_layer=source_layer,
                target_layer=target_layer,
                validation_status=SchemaValidationStatus.MISSING,
            )
        if expected_version != schema_version:
            return BoundarySchemaDescriptor(
                schema_id=schema_id,
                schema_version=schema_version,
                source_layer=source_layer,
                target_layer=target_layer,
                validation_status=SchemaValidationStatus.INVALID,
            )

    return BoundarySchemaDescriptor(
        schema_id=schema_id,
        schema_version=schema_version,
        source_layer=source_layer,
        target_layer=target_layer,
        validation_status=SchemaValidationStatus.VALID,
    )


# =============================================================================
# Meta-Governor: run_meta_invariants
# =============================================================================


class MetaInvariantError(Exception):
    """Raised when meta-invariant check fails (fail-closed)."""


def assert_cross_run_pins(
    discovery_hash: str,
    expected_discovery_hash: str,
    schema_version: str,
    expected_schema_version: str,
) -> tuple[InvariantCheck, InvariantViolation | None]:
    """Assert cross-run pinned values are unchanged."""
    discovery_ok = discovery_hash == expected_discovery_hash
    schema_ok = schema_version == expected_schema_version

    violations: list[str] = []
    if not discovery_ok:
        violations.append(
            f"discovery_hash mismatch: expected {expected_discovery_hash}, got {discovery_hash}",
        )
    if not schema_ok:
        violations.append(
            f"schema_version mismatch: expected {expected_schema_version}, got {schema_version}",
        )

    passed = len(violations) == 0
    check = InvariantCheck(
        check_id="cross_run_pins",
        description="Discovery hash and schema version match pinned values",
        passed=passed,
        evidence=f"discovery_hash={discovery_hash}, schema_version={schema_version}",
    )

    violation = None
    if not passed:
        violation = InvariantViolation(
            invariant_id="cross_run_pins",
            severity=InvariantSeverity.CRITICAL,
            evidence_paths=("artifacts/forensic_discovery_output.json",),
            details="; ".join(violations),
        )

    return check, violation


def assert_chain_closure(
    expected_artifacts: frozenset[str],
    actual_artifacts: frozenset[str],
) -> tuple[InvariantCheck, InvariantViolation | None]:
    """Assert P1–P5 artifact chain closure: no orphans, no missing."""
    missing = expected_artifacts - actual_artifacts
    orphans = actual_artifacts - expected_artifacts

    passed = len(missing) == 0 and len(orphans) == 0
    evidence_parts = []
    if missing:
        evidence_parts.append(f"missing={sorted(missing)}")
    if orphans:
        evidence_parts.append(f"orphans={sorted(orphans)}")
    if not evidence_parts:
        evidence_parts.append("all artifacts present, no orphans")

    check = InvariantCheck(
        check_id="chain_closure",
        description="All expected P1-P5 artifacts present, no orphan artifacts",
        passed=passed,
        evidence="; ".join(evidence_parts),
    )

    violation = None
    if not passed:
        violation = InvariantViolation(
            invariant_id="chain_closure",
            severity=InvariantSeverity.HIGH,
            evidence_paths=tuple(sorted(missing | orphans)),
            details="; ".join(evidence_parts),
        )

    return check, violation


def run_meta_invariants(
    trace_id: str,
    run_id: str,
    semantic_clock_tick: int,
    discovery_hash: str,
    expected_discovery_hash: str,
    schema_version: str,
    expected_schema_version: str,
    expected_artifacts: frozenset[str],
    actual_artifacts: frozenset[str],
) -> MetaInvariantReport:
    """Run all meta-invariant checks and produce a report.

    Fail-closed: if any check fails, pass_fail is False.
    """
    checks: list[InvariantCheck] = []
    violations: list[InvariantViolation] = []

    # Cross-run pins
    pin_check, pin_violation = assert_cross_run_pins(
        discovery_hash,
        expected_discovery_hash,
        schema_version,
        expected_schema_version,
    )
    checks.append(pin_check)
    if pin_violation is not None:
        violations.append(pin_violation)

    # Chain closure
    closure_check, closure_violation = assert_chain_closure(
        expected_artifacts,
        actual_artifacts,
    )
    checks.append(closure_check)
    if closure_violation is not None:
        violations.append(closure_violation)

    pass_fail = len(violations) == 0

    return MetaInvariantReport(
        trace_id=trace_id,
        run_id=run_id,
        semantic_clock_tick=semantic_clock_tick,
        checks=tuple(checks),
        pass_fail=pass_fail,
        violations=tuple(violations),
    )


def fail_closed_on_violation(report: MetaInvariantReport) -> bool:
    """Raise MetaInvariantError if the report contains any violations."""
    if not report.pass_fail:
        details = "; ".join(v.details for v in report.violations)
        raise MetaInvariantError(
            f"FAIL (P6): Meta-invariant violations detected in run '{report.run_id}': {details}",
        )
    return True


__all__ = [
    "BoundarySchemaError",
    "ContextRetrievalError",
    "MetaInvariantError",
    "SSOTBindingError",
    "assert_chain_closure",
    "assert_cross_run_pins",
    "build_boundary_schema",
    "build_context_retrieval_request",
    "fail_closed_on_violation",
    "resolve_ssot_binding",
    "run_meta_invariants",
    "validate_boundary_schema",
    "validate_context_retrieval_read_only",
]
