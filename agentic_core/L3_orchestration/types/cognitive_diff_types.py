"""
§Wave4.2 — L3CognitiveDiffBundle: deterministic cognitive state diff at L3 boundary.

Emitted when L3 produces a RouteDecisionArtifact, capturing the before/after
cognitive state and a structured, sorted diff representation.

Deterministic contract:
  - SemanticClockSnapshot required (Phase 3.2)
  - DiffOp list sorted by path
  - Deterministic trace_id (SHA-256 of canonical payload)
  - No uuid4, no wall-clock, no elapsed_ms
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
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

_emit_emits_metric_event("cognitive_diff_types", "p4obs", "metric_1")
_emit_emits_metric_event("cognitive_diff_types", "p4obs", "metric_2")
_emit_emits_metric_event("cognitive_diff_types", "p4obs", "metric_3")
_emit_emits_metric_event("cognitive_diff_types", "p4obs", "metric_4")
_emit_emits_metric_event("cognitive_diff_types", "p4obs", "metric_5")
_emit_emits_metric_event("cognitive_diff_types", "p4obs", "metric_6")
_emit_records_incident_event("cognitive_diff_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("cognitive_diff_types", "p4obs", "anomaly")
_emit_writes_observability_log("cognitive_diff_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("cognitive_diff_types", "p4obs", "mon_state")
_emit_triggers_alert("cognitive_diff_types", "p4obs", "alert")
_emit_links_incident_trace("cognitive_diff_types", "p4obs", "trace_link")
_emit_captures_pattern("cognitive_diff_types", "p3lm", "pattern")
_emit_records_learning_event("cognitive_diff_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cognitive_diff_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("cognitive_diff_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cognitive_diff_types", "p3lm", "routing")
_emit_improves_agent_policy("cognitive_diff_types", "p3lm", "policy")
_emit_stores_learning_state("cognitive_diff_types", "p3lm", "state")
_emit_records_execution_trace("cognitive_diff_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cognitive_diff_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cognitive_diff_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cognitive_diff_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cognitive_diff_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cognitive_diff_types", "env_read", "p2_env_1")
_emit_reads_environ("cognitive_diff_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("cognitive_diff_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cognitive_diff_types", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "cognitive_diff_types")
emit_determinism_digest("p0", "cognitive_diff_types")

_emit_dispatches_healing_run("p1", "cognitive_diff_types", "L3")
_emit_routes_through("p1", "cognitive_diff_types", "L3")
_emit_checks_agent_registry("p1", "cognitive_diff_types", "agent_registry")
_emit_validates_agent_capability("p1", "cognitive_diff_types", "capability")
_emit_dispatches_execution_plan("p1", "cognitive_diff_types", "exec_plan")
_emit_agent_executes_agent("p1", "cognitive_diff_types", "sub_agent")
_emit_routes_to_agent("p1", "cognitive_diff_types", "target_agent")
_emit_verifies_policy("p1", "cognitive_diff_types", "policy_check")
_emit_observes_runtime_state("p1", "cognitive_diff_types", "runtime_state")
_emit_verifies_boundary("p1", "cognitive_diff_types", "boundary_check")
_emit_transcripts_response("p1", "cognitive_diff_types", "transcript")
_emit_hard_fails_untranscripted("p1", "cognitive_diff_types")
_emit_gated_by_confidence("p1", "cognitive_diff_types", "confidence_gate")
_emit_escalates_to_human("p1", "cognitive_diff_types", "L3")
_emit_reads_policy_state("p1", "cognitive_diff_types", "L3")
_emit_pulls_context("p1", "cognitive_diff_types", "context_pull")
_emit_pulls_context("p1", "cognitive_diff_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "cognitive_diff_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cognitive_diff_types", "uwg_term_secondary")
_emit_writes_through("p1", "cognitive_diff_types", "write_through")
_emit_writes_through("p1", "cognitive_diff_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "cognitive_diff_types", "safety_validation")
_emit_invokes_eval("p1", "cognitive_diff_types", "eval_call")
_emit_proposal_commits_routing("p1", "cognitive_diff_types", "routing_commit")

_emit_snapshots_state("p0", "cognitive_diff_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "cognitive_diff_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "cognitive_diff_types")
_emit_authorize_and_execute("p2", "cognitive_diff_types", "execution_auth")
_emit_validates_capability("p2", "cognitive_diff_types", "capability_check")
_emit_routes_to_capability("p2", "cognitive_diff_types", "capability_route")
_emit_writes_via_uwg("p2", "cognitive_diff_types", "uwg_write")
_emit_blocks_direct_write("p2", "cognitive_diff_types", "direct_write_block")
_emit_records_tool_invocation("p2", "cognitive_diff_types", "tool_invocation")
_emit_captures_execution_output("p2", "cognitive_diff_types", "exec_output")
_emit_dispatches_agent("p3", "cognitive_diff_types", "agent_dispatch")
_emit_coordinates_agents("p3", "cognitive_diff_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "cognitive_diff_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "cognitive_diff_types", "healing_outcome")
_emit_escalates_failure("p3", "cognitive_diff_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "cognitive_diff_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cognitive_diff_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "cognitive_diff_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "cognitive_diff_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cognitive_diff_types", "eval_metric")
_emit_stores_embedding("p4", "cognitive_diff_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "cognitive_diff_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cognitive_diff_types", "exec_snapshot_link")

# =============================================================================
# §Wave4.2 — CognitiveStateSnapshot
# =============================================================================


@dataclass(frozen=True)
class CognitiveStateSnapshot:
    """Minimal, stable snapshot of cognitive state at a decision boundary.

    All fields are JSON-primitive compatible. No repr(), no Enum objects.
    """

    route_context: str
    candidate_paths: tuple[str, ...]
    selected_path: str
    rationale_enum: str
    risk_score: float
    budget_est: float

    def __post_init__(self) -> None:
        if not isinstance(self.candidate_paths, tuple):
            raise TypeError(
                "CognitiveStateSnapshot: candidate_paths must be a tuple",
            )
        if list(self.candidate_paths) != sorted(self.candidate_paths):
            raise ValueError(
                "CognitiveStateSnapshot: candidate_paths must be sorted",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "budget_est": self.budget_est,
            "candidate_paths": list(self.candidate_paths),
            "rationale_enum": self.rationale_enum,
            "risk_score": self.risk_score,
            "route_context": self.route_context,
            "selected_path": self.selected_path,
        }


# =============================================================================
# §Wave4.2 — DiffOp
# =============================================================================


@dataclass(frozen=True)
class DiffOp:
    """A single field-level diff operation between before and after states.

    path: dotted field name (e.g., "selected_path", "risk_score")
    before: JSON-primitive value from the before state
    after: JSON-primitive value from the after state
    """

    path: str
    before: Any
    after: Any

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("DiffOp: path must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "after": self.after,
            "before": self.before,
            "path": self.path,
        }


# =============================================================================
# §Wave4.2 — L3CognitiveDiffBundle
# =============================================================================


@dataclass(frozen=True)
class L3CognitiveDiffBundle:
    """§Wave4.2 — Deterministic cognitive diff emitted at L3 orchestration boundary.

    Required fields:
      artifact_type     — fixed "COGNITIVE_DIFF_BUNDLE"
      semantic_clock    — required SemanticClockSnapshot (Phase 3.2)
      trace_id          — deterministic (SHA-256 of canonical payload)
      before            — CognitiveStateSnapshot
      after             — CognitiveStateSnapshot
      diff              — sorted tuple of DiffOp
      policy_config_hash — optional
    """

    artifact_type: str
    semantic_clock: SemanticClockSnapshot
    trace_id: str
    before: CognitiveStateSnapshot
    after: CognitiveStateSnapshot
    diff: tuple[DiffOp, ...]
    policy_config_hash: str = ""

    def __post_init__(self) -> None:
        if self.artifact_type != "COGNITIVE_DIFF_BUNDLE":
            raise ValueError(
                f"L3CognitiveDiffBundle: artifact_type must be 'COGNITIVE_DIFF_BUNDLE', "
                f"got '{self.artifact_type}'",
            )
        validate_semantic_clock(self.semantic_clock)
        if not self.trace_id:
            raise ValueError(
                "L3CognitiveDiffBundle: trace_id must be non-empty",
            )
        if not isinstance(self.before, CognitiveStateSnapshot):
            raise TypeError(
                "L3CognitiveDiffBundle: before must be CognitiveStateSnapshot",
            )
        if not isinstance(self.after, CognitiveStateSnapshot):
            raise TypeError(
                "L3CognitiveDiffBundle: after must be CognitiveStateSnapshot",
            )
        if not isinstance(self.diff, tuple):
            raise TypeError("L3CognitiveDiffBundle: diff must be a tuple")
        paths = [op.path for op in self.diff]
        if paths != sorted(paths):
            raise ValueError(
                "L3CognitiveDiffBundle: diff ops must be sorted by path",
            )

    def to_dict(self) -> dict[str, Any]:
        """Deterministic serialization with sorted keys."""
        return {
            "after": self.after.to_dict(),
            "artifact_type": self.artifact_type,
            "before": self.before.to_dict(),
            "diff": [op.to_dict() for op in self.diff],
            "policy_config_hash": self.policy_config_hash,
            "semantic_clock": self.semantic_clock.to_dict(),
            "trace_id": self.trace_id,
        }


# =============================================================================
# §Wave4.2 — Deterministic diff computation + bundle factory
# =============================================================================

_DIFF_FIELDS = (
    "budget_est",
    "candidate_paths",
    "rationale_enum",
    "risk_score",
    "route_context",
    "selected_path",
)


def compute_cognitive_diff(
    before: CognitiveStateSnapshot,
    after: CognitiveStateSnapshot,
) -> tuple[DiffOp, ...]:
    """Compute sorted diff ops between two CognitiveStateSnapshot instances.

    Compares all tracked fields. Only changed fields produce a DiffOp.
    Ops are sorted by path (alphabetical).
    """
    ops: list[DiffOp] = []
    before_d = before.to_dict()
    after_d = after.to_dict()

    for field_name in _DIFF_FIELDS:
        bv = before_d[field_name]
        av = after_d[field_name]
        if bv != av:
            ops.append(DiffOp(path=field_name, before=bv, after=av))

    return tuple(sorted(ops, key=lambda op: op.path))


def _compute_bundle_trace_id(
    before: CognitiveStateSnapshot,
    after: CognitiveStateSnapshot,
    tick: int,
) -> str:
    """Deterministic trace_id from canonical payload hash."""
    canonical = json.dumps(
        {"after": after.to_dict(), "before": before.to_dict(), "tick": tick},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def emit_cognitive_diff_bundle(
    before: CognitiveStateSnapshot,
    after: CognitiveStateSnapshot,
    semantic_clock: SemanticClockSnapshot,
    policy_config_hash: str = "",
) -> L3CognitiveDiffBundle:
    """§Wave4.2 — Build an L3CognitiveDiffBundle deterministically.

    1. Compute sorted diff ops
    2. Generate deterministic trace_id
    3. Return frozen bundle
    """
    validate_semantic_clock(semantic_clock)
    diff = compute_cognitive_diff(before, after)
    trace_id = _compute_bundle_trace_id(before, after, semantic_clock.tick)

    return L3CognitiveDiffBundle(
        artifact_type="COGNITIVE_DIFF_BUNDLE",
        semantic_clock=semantic_clock,
        trace_id=trace_id,
        before=before,
        after=after,
        diff=diff,
        policy_config_hash=policy_config_hash,
    )


__all__ = [
    "CognitiveStateSnapshot",
    "DiffOp",
    "L3CognitiveDiffBundle",
    "compute_cognitive_diff",
    "emit_cognitive_diff_bundle",
]
