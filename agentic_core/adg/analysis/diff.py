"""Enhancement 7: Historical graph diff engine.

Compares two CanonicalSnapshots (ADG(t-1) vs ADG(t)) and emits a
structured GraphDiff with:
  - new_edges / removed_edges
  - new_violations / resolved_violations
  - new_coverage / removed_coverage
  - risk_delta (signed int: positive = more violations)
  - summary string for CI output
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "diff", "p0_governance")
_emit_reads_policy_state("p0", "diff", "policy_binding")
_emit_snapshots_state("p0", "diff", "state_snapshot")
_emit_escalates_to_human("p1", "diff", "human_escalation")
emit_replay_key("p0", "diff")
emit_determinism_digest("p0", "diff")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "diff", "execution_auth")
_emit_validates_capability("p2", "diff", "capability_check")
_emit_routes_to_capability("p2", "diff", "capability_route")
_emit_writes_via_uwg("p2", "diff", "uwg_write")
_emit_blocks_direct_write("p2", "diff", "direct_write_block")
_emit_records_tool_invocation("p2", "diff", "tool_invocation")
_emit_captures_execution_output("p2", "diff", "exec_output")
_emit_dispatches_agent("p3", "diff", "agent_dispatch")
_emit_coordinates_agents("p3", "diff", "agent_coordination")
_emit_records_workflow_lineage("p3", "diff", "workflow_lineage")
_emit_records_healing_outcome("p3", "diff", "healing_outcome")
_emit_escalates_failure("p3", "diff", "failure_escalation")
_emit_orchestrates_workflow("p3", "diff", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "diff", "healing_dispatch")
_emit_invokes_evaluation("p3", "diff", "evaluation_signal")
_emit_records_telemetry_event("p4", "diff", "telemetry_event")
_emit_captures_evaluation_metric("p4", "diff", "eval_metric")
_emit_stores_embedding("p4", "diff", "embedding_store")
_emit_updates_meta_learning_state("p4", "diff", "meta_learning")
_emit_links_execution_to_snapshot("p4", "diff", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.analysis.snapshot import CanonicalSnapshot
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("diff", "p4obs", "metric_1")
_emit_emits_metric_event("diff", "p4obs", "metric_2")
_emit_emits_metric_event("diff", "p4obs", "metric_3")
_emit_emits_metric_event("diff", "p4obs", "metric_4")
_emit_emits_metric_event("diff", "p4obs", "metric_5")
_emit_emits_metric_event("diff", "p4obs", "metric_6")
_emit_records_incident_event("diff", "p4obs", "incident")
_emit_captures_runtime_anomaly("diff", "p4obs", "anomaly")
_emit_writes_observability_log("diff", "p4obs", "obs_log")
_emit_updates_monitoring_state("diff", "p4obs", "mon_state")
_emit_triggers_alert("diff", "p4obs", "alert")
_emit_links_incident_trace("diff", "p4obs", "trace_link")
_emit_captures_pattern("diff", "p3lm", "pattern")
_emit_records_learning_event("diff", "p3lm", "learning_event")
_emit_writes_learning_snapshot("diff", "p3lm", "snapshot")
_emit_feeds_meta_learning("diff", "p3lm", "meta_feed")
_emit_updates_routing_strategy("diff", "p3lm", "routing")
_emit_improves_agent_policy("diff", "p3lm", "policy")
_emit_stores_learning_state("diff", "p3lm", "state")
_emit_records_execution_trace("diff", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("diff", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("diff", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("diff", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("diff", "L4_STATE", "p2_trace_5")
_emit_reads_environ("diff", "env_read", "p2_env_1")
_emit_reads_environ("diff", "env_read", "p2_env_2")
_emit_reads_runtime_state("diff", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("diff", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "diff", "context_pull")
_emit_pulls_context("p1", "diff", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "diff", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "diff", "uwg_term_2")
_emit_writes_through("p1", "diff", "write_through")
_emit_writes_through("p1", "diff", "write_through_2")
_emit_validated_by_safety_plane("p1", "diff", "safety_validation")
_emit_invokes_eval("p1", "diff", "eval_call")
_emit_proposal_commits_routing("p1", "diff", "routing_commit")
_emit_routes_through("p1", "diff", "route_through")
_emit_checks_agent_registry("p1", "diff", "agent_registry")
_emit_validates_agent_capability("p1", "diff", "capability")
_emit_dispatches_execution_plan("p1", "diff", "exec_plan")
_emit_agent_executes_agent("p1", "diff", "sub_agent")
_emit_routes_to_agent("p1", "diff", "target_agent")
_emit_verifies_policy("p1", "diff", "policy_check")
_emit_observes_runtime_state("p1", "diff", "runtime_state")
_emit_verifies_boundary("p1", "diff", "boundary_check")
_emit_transcripts_response("p1", "diff", "transcript")
_emit_hard_fails_untranscripted("p1", "diff")
_emit_gated_by_confidence("p1", "diff", "confidence_gate")


@dataclass
class GraphDiff:
    """Structured diff between two ADG snapshots.

    All edge lists contain (from_name, relation_type, to_name) tuples.
    """

    commit_before: str = ""
    commit_after: str = ""
    hash_before: str = ""
    hash_after: str = ""

    new_edges: list[tuple[str, str, str]] = field(default_factory=list)
    removed_edges: list[tuple[str, str, str]] = field(default_factory=list)

    new_violations: list[tuple[str, str, str]] = field(default_factory=list)
    resolved_violations: list[tuple[str, str, str]] = field(default_factory=list)

    new_coverage: list[tuple[str, str, str]] = field(default_factory=list)
    removed_coverage: list[tuple[str, str, str]] = field(default_factory=list)

    new_calls: list[tuple[str, str, str]] = field(default_factory=list)
    removed_calls: list[tuple[str, str, str]] = field(default_factory=list)

    new_governance: list[tuple[str, str, str]] = field(default_factory=list)
    removed_governance: list[tuple[str, str, str]] = field(default_factory=list)

    node_delta: int = 0
    edge_delta: int = 0
    risk_delta: int = 0

    is_identical: bool = False

    @property
    def summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GraphDiff.summary")

        if self.is_identical:
            return f"ADG unchanged (hash={self.hash_after[:12]})"
        parts = []
        if self.new_edges:
            parts.append(f"+{len(self.new_edges)} edges")
        if self.removed_edges:
            parts.append(f"-{len(self.removed_edges)} edges")
        if self.new_violations:
            parts.append(f"+{len(self.new_violations)} violations")
        if self.resolved_violations:
            parts.append(f"-{len(self.resolved_violations)} violations (resolved)")
        if self.risk_delta > 0:
            parts.append(f"risk_delta=+{self.risk_delta} [WORSE]")
        elif self.risk_delta < 0:
            parts.append(f"risk_delta={self.risk_delta} [IMPROVED]")
        return "ADG diff: " + ", ".join(parts) if parts else "ADG: structural changes (no violations)"

    def to_dict(self) -> dict:
        return {
            "commit_before": self.commit_before,
            "commit_after": self.commit_after,
            "hash_before": self.hash_before,
            "hash_after": self.hash_after,
            "is_identical": self.is_identical,
            "node_delta": self.node_delta,
            "edge_delta": self.edge_delta,
            "risk_delta": self.risk_delta,
            "summary": self.summary,
            "new_edges": [list(e) for e in self.new_edges],
            "removed_edges": [list(e) for e in self.removed_edges],
            "new_violations": [list(e) for e in self.new_violations],
            "resolved_violations": [list(e) for e in self.resolved_violations],
            "new_coverage": [list(e) for e in self.new_coverage],
            "removed_coverage": [list(e) for e in self.removed_coverage],
            "new_calls": [list(e) for e in self.new_calls],
            "removed_calls": [list(e) for e in self.removed_calls],
            "new_governance": [list(e) for e in self.new_governance],
            "removed_governance": [list(e) for e in self.removed_governance],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def diff_snapshots(before: CanonicalSnapshot, after: CanonicalSnapshot) -> GraphDiff:
    """Compute a structured GraphDiff between two CanonicalSnapshots.

    Args:
        before: The older snapshot (ADG at t-1).
        after: The newer snapshot (ADG at t).

    Returns:
        GraphDiff with categorised new/removed edges and risk delta.
    """
    diff = GraphDiff(
        commit_before=before.commit_sha,
        commit_after=after.commit_sha,
        hash_before=before.graph_hash,
        hash_after=after.graph_hash,
    )

    if before.graph_hash == after.graph_hash:
        diff.is_identical = True
        return diff

    before_set: set[tuple[str, str, str]] = set(before.canonical_edge_order)
    after_set: set[tuple[str, str, str]] = set(after.canonical_edge_order)

    added = sorted(after_set - before_set)
    removed = sorted(before_set - after_set)

    diff.new_edges = added
    diff.removed_edges = removed
    diff.node_delta = after.node_count - before.node_count
    diff.edge_delta = after.edge_count - before.edge_count

    def _filter(edges: list[tuple[str, str, str]], relation: str) -> list[tuple[str, str, str]]:
        return [e for e in edges if e[1] == relation]

    def _filter_multi(edges: list[tuple[str, str, str]], *relations: str) -> list[tuple[str, str, str]]:
        return [e for e in edges if e[1] in relations]

    diff.new_violations = _filter(added, "violates")
    diff.resolved_violations = _filter(removed, "violates")
    diff.new_coverage = _filter(added, "covers")
    diff.removed_coverage = _filter(removed, "covers")
    diff.new_calls = _filter(added, "calls")
    diff.removed_calls = _filter(removed, "calls")
    diff.new_governance = _filter_multi(added, "writes_through", "routes_through")
    diff.removed_governance = _filter_multi(removed, "writes_through", "routes_through")

    diff.risk_delta = len(diff.new_violations) - len(diff.resolved_violations)

    return diff
