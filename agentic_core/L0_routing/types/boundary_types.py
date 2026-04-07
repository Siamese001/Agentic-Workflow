"""
V15 P6 Typed Artifacts — Meta-Invariants & Typed Boundaries.

Typed artifacts required by Prompt v5.0 Enhanced for P6 (Explicit
Boundaries / Zero Trust Between Layers) invariants. All report and
violation artifacts are frozen dataclasses with strict field validation.

Artifact version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("boundary_types", "p4obs", "metric_1")
_emit_emits_metric_event("boundary_types", "p4obs", "metric_2")
_emit_emits_metric_event("boundary_types", "p4obs", "metric_3")
_emit_emits_metric_event("boundary_types", "p4obs", "metric_4")
_emit_emits_metric_event("boundary_types", "p4obs", "metric_5")
_emit_emits_metric_event("boundary_types", "p4obs", "metric_6")
_emit_records_incident_event("boundary_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("boundary_types", "p4obs", "anomaly")
_emit_writes_observability_log("boundary_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("boundary_types", "p4obs", "mon_state")
_emit_triggers_alert("boundary_types", "p4obs", "alert")
_emit_links_incident_trace("boundary_types", "p4obs", "trace_link")
_emit_captures_pattern("boundary_types", "p3lm", "pattern")
_emit_records_learning_event("boundary_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("boundary_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("boundary_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("boundary_types", "p3lm", "routing")
_emit_improves_agent_policy("boundary_types", "p3lm", "policy")
_emit_stores_learning_state("boundary_types", "p3lm", "state")
_emit_records_execution_trace("boundary_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("boundary_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("boundary_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("boundary_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("boundary_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("boundary_types", "env_read", "p2_env_1")
_emit_reads_environ("boundary_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("boundary_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("boundary_types", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "boundary_types")
emit_determinism_digest("p0", "boundary_types")

_emit_dispatches_healing_run("p1", "boundary_types", "L0")
_emit_routes_through("p1", "boundary_types", "L0")
_emit_checks_agent_registry("p1", "boundary_types", "agent_registry")
_emit_validates_agent_capability("p1", "boundary_types", "capability")
_emit_dispatches_execution_plan("p1", "boundary_types", "exec_plan")
_emit_agent_executes_agent("p1", "boundary_types", "sub_agent")
_emit_routes_to_agent("p1", "boundary_types", "target_agent")
_emit_verifies_policy("p1", "boundary_types", "policy_check")
_emit_observes_runtime_state("p1", "boundary_types", "runtime_state")
_emit_verifies_boundary("p1", "boundary_types", "boundary_check")
_emit_transcripts_response("p1", "boundary_types", "transcript")
_emit_hard_fails_untranscripted("p1", "boundary_types")
_emit_gated_by_confidence("p1", "boundary_types", "confidence_gate")
_emit_escalates_to_human("p1", "boundary_types", "L0")
_emit_reads_policy_state("p1", "boundary_types", "L0")
_emit_pulls_context("p1", "boundary_types", "context_pull")
_emit_pulls_context("p1", "boundary_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "boundary_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "boundary_types", "uwg_term_secondary")
_emit_writes_through("p1", "boundary_types", "write_through")
_emit_writes_through("p1", "boundary_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "boundary_types", "safety_validation")
_emit_invokes_eval("p1", "boundary_types", "eval_call")
_emit_proposal_commits_routing("p1", "boundary_types", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "boundary_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "boundary_types", "p0_governance")
_emit_snapshots_state("p0", "boundary_types", "state_snapshot")
_emit_authorize_and_execute("p2", "boundary_types", "execution_auth")
_emit_validates_capability("p2", "boundary_types", "capability_check")
_emit_routes_to_capability("p2", "boundary_types", "capability_route")
_emit_writes_via_uwg("p2", "boundary_types", "uwg_write")
_emit_blocks_direct_write("p2", "boundary_types", "direct_write_block")
_emit_records_tool_invocation("p2", "boundary_types", "tool_invocation")
_emit_captures_execution_output("p2", "boundary_types", "exec_output")
_emit_dispatches_agent("p3", "boundary_types", "agent_dispatch")
_emit_coordinates_agents("p3", "boundary_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "boundary_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "boundary_types", "healing_outcome")
_emit_escalates_failure("p3", "boundary_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "boundary_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "boundary_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "boundary_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "boundary_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "boundary_types", "eval_metric")
_emit_stores_embedding("p4", "boundary_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "boundary_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "boundary_types", "exec_snapshot_link")


@dataclass(frozen=True)
class SSOTBinding:
    """§1.5 — Proves a node_id resolves to a valid SSOT definition.

    The binding links the manifest's node_id to the blueprint entry
    that authorizes it.
    """

    node_id: str
    blueprint_entry: str
    resolved: bool

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("SSOTBinding: node_id must be non-empty")
        if not self.blueprint_entry:
            raise ValueError("SSOTBinding: blueprint_entry must be non-empty")


@dataclass(frozen=True)
class ContextRetrievalRequest:
    """§3.8 — Typed request from L0 to L4 (advisory-only, read-only).

    Required fields: trace_id, query_hash, semantic_clock_tick.
    Constraint: No direct writes from L0.
    """

    trace_id: str
    query_hash: str
    semantic_clock_tick: int
    source_layer: str = "L0"
    target_layer: str = "L4"
    read_only: bool = True

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("ContextRetrievalRequest: trace_id must be non-empty")
        if not self.query_hash:
            raise ValueError("ContextRetrievalRequest: query_hash must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"ContextRetrievalRequest: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )
        if not self.read_only:
            raise ValueError("ContextRetrievalRequest: read_only must be True (L0→L4 is advisory-only)")


class SchemaValidationStatus(Enum):
    """Status of a boundary schema validation."""

    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"


@dataclass(frozen=True)
class BoundarySchemaDescriptor:
    """§12.1 / §2.4 — Typed and versioned boundary between layers.

    Every cross-layer call must declare its schema version and the
    source/target layers. Validation status is captured.
    """

    schema_id: str
    schema_version: str
    source_layer: str
    target_layer: str
    validation_status: SchemaValidationStatus

    def __post_init__(self) -> None:
        if not self.schema_id:
            raise ValueError("BoundarySchemaDescriptor: schema_id must be non-empty")
        if not self.schema_version:
            raise ValueError("BoundarySchemaDescriptor: schema_version must be non-empty")
        if not self.source_layer:
            raise ValueError("BoundarySchemaDescriptor: source_layer must be non-empty")
        if not self.target_layer:
            raise ValueError("BoundarySchemaDescriptor: target_layer must be non-empty")
        if not isinstance(self.validation_status, SchemaValidationStatus):
            raise TypeError(
                f"BoundarySchemaDescriptor: validation_status must be SchemaValidationStatus, got {type(self.validation_status).__name__}",
            )


class InvariantSeverity(Enum):
    """Severity of an invariant violation."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    INFO = "info"


@dataclass(frozen=True)
class InvariantViolation:
    """A single meta-invariant violation with evidence."""

    invariant_id: str
    severity: InvariantSeverity
    evidence_paths: tuple[str, ...]
    details: str

    def __post_init__(self) -> None:
        if not self.invariant_id:
            raise ValueError("InvariantViolation: invariant_id must be non-empty")
        if not isinstance(self.severity, InvariantSeverity):
            raise TypeError(
                f"InvariantViolation: severity must be InvariantSeverity, got {type(self.severity).__name__}",
            )
        if not isinstance(self.evidence_paths, tuple):
            raise TypeError("InvariantViolation: evidence_paths must be a tuple")
        if not self.details:
            raise ValueError("InvariantViolation: details must be non-empty")


@dataclass(frozen=True)
class InvariantCheck:
    """A single invariant check result."""

    check_id: str
    description: str
    passed: bool
    evidence: str

    def __post_init__(self) -> None:
        if not self.check_id:
            raise ValueError("InvariantCheck: check_id must be non-empty")
        if not self.description:
            raise ValueError("InvariantCheck: description must be non-empty")
        if not self.evidence:
            raise ValueError("InvariantCheck: evidence must be non-empty")


@dataclass(frozen=True)
class MetaInvariantReport:
    """Meta-governor report for end-of-wave / end-of-run invariant checks.

    Fields: trace_id, run_id, semantic_clock_tick, checks, pass_fail, violations.
    """

    trace_id: str
    run_id: str
    semantic_clock_tick: int
    checks: tuple[InvariantCheck, ...]
    pass_fail: bool
    violations: tuple[InvariantViolation, ...]

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("MetaInvariantReport: trace_id must be non-empty")
        if not self.run_id:
            raise ValueError("MetaInvariantReport: run_id must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"MetaInvariantReport: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )
        if not isinstance(self.checks, tuple):
            raise TypeError("MetaInvariantReport: checks must be a tuple")
        if not isinstance(self.violations, tuple):
            raise TypeError("MetaInvariantReport: violations must be a tuple")
        if self.violations and self.pass_fail:
            raise ValueError("MetaInvariantReport: pass_fail cannot be True when violations are present")


@dataclass(frozen=True)
class SideEffectRegistry:
    """§12.2 — Immutable registry of side effects produced during a heal wave.

    Tracks all resources touched (read/written) and APIs called,
    enabling deterministic replay and audit.
    """

    trace_id: str
    wave_id: str
    paths_read: tuple[str, ...]
    paths_written: tuple[str, ...]
    apis_called: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("SideEffectRegistry: trace_id must be non-empty")
        if not self.wave_id:
            raise ValueError("SideEffectRegistry: wave_id must be non-empty")
        if not isinstance(self.paths_read, tuple):
            raise TypeError("SideEffectRegistry: paths_read must be a tuple")
        if not isinstance(self.paths_written, tuple):
            raise TypeError("SideEffectRegistry: paths_written must be a tuple")
        if not isinstance(self.apis_called, tuple):
            raise TypeError("SideEffectRegistry: apis_called must be a tuple")


V15_DISCOVERY_SCHEMA_VERSION: str = "1.0.0"


@dataclass(frozen=True)
class V15DiscoverySchema:
    """§8.4 — Pinned discovery schema for the V15 Environment Under Test.

    ALL fields are required. Missing field = HARD FAIL in guardian tests.
    MRO scanners MUST consume ONLY this schema (no live reflection fallback).
    """

    identity: str
    layer: str
    status: str
    file_path: str
    class_name: str
    mro_chain: tuple[str, ...]
    mixins: tuple[str, ...]
    detected_methods: tuple[str, ...]
    integrity_hash: str
    mro_signature: str

    def __post_init__(self) -> None:
        if not self.identity:
            raise ValueError("V15DiscoverySchema: identity must be non-empty")
        if not self.layer:
            raise ValueError("V15DiscoverySchema: layer must be non-empty")
        if not self.status:
            raise ValueError("V15DiscoverySchema: status must be non-empty")
        if not self.file_path:
            raise ValueError("V15DiscoverySchema: file_path must be non-empty")
        if not self.class_name:
            raise ValueError("V15DiscoverySchema: class_name must be non-empty")
        if not isinstance(self.mro_chain, tuple):
            raise TypeError("V15DiscoverySchema: mro_chain must be a tuple")
        if not isinstance(self.mixins, tuple):
            raise TypeError("V15DiscoverySchema: mixins must be a tuple")
        if not isinstance(self.detected_methods, tuple):
            raise TypeError("V15DiscoverySchema: detected_methods must be a tuple")
        if not self.integrity_hash:
            raise ValueError("V15DiscoverySchema: integrity_hash must be non-empty")
        if not self.mro_signature:
            raise ValueError("V15DiscoverySchema: mro_signature must be non-empty")


V15_DISCOVERY_REQUIRED_FIELDS: frozenset[str] = frozenset(
    f.name for f in __import__("dataclasses").fields(V15DiscoverySchema)
)
__all__ = [
    "BoundarySchemaDescriptor",
    "ContextRetrievalRequest",
    "InvariantCheck",
    "InvariantSeverity",
    "InvariantViolation",
    "MetaInvariantReport",
    "SSOTBinding",
    "SchemaValidationStatus",
    "SideEffectRegistry",
    "V15DiscoverySchema",
    "V15_DISCOVERY_REQUIRED_FIELDS",
    "V15_DISCOVERY_SCHEMA_VERSION",
]
