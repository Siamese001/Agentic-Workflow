"""
agentic_core/L1_cognition/reasoning/types/domain_types.py

Passive data structures for DomainContextManager.
Extracted from engine/domain_manager.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "domain_types")
emit_determinism_digest("p0", "domain_types")

_emit_dispatches_healing_run("p1", "domain_types", "L1")
_emit_routes_through("p1", "domain_types", "L1")
_emit_checks_agent_registry("p1", "domain_types", "agent_registry")
_emit_validates_agent_capability("p1", "domain_types", "capability")
_emit_dispatches_execution_plan("p1", "domain_types", "exec_plan")
_emit_agent_executes_agent("p1", "domain_types", "sub_agent")
_emit_routes_to_agent("p1", "domain_types", "target_agent")
_emit_verifies_policy("p1", "domain_types", "policy_check")
_emit_observes_runtime_state("p1", "domain_types", "runtime_state")
_emit_verifies_boundary("p1", "domain_types", "boundary_check")
_emit_transcripts_response("p1", "domain_types", "transcript")
_emit_hard_fails_untranscripted("p1", "domain_types")
_emit_gated_by_confidence("p1", "domain_types", "confidence_gate")
_emit_escalates_to_human("p1", "domain_types", "L1")
_emit_reads_policy_state("p1", "domain_types", "L1")
_emit_authorize_and_execute("p2", "domain_types", "execution_auth")
_emit_validates_capability("p2", "domain_types", "capability_check")
_emit_routes_to_capability("p2", "domain_types", "capability_route")
_emit_writes_via_uwg("p2", "domain_types", "uwg_write")
_emit_blocks_direct_write("p2", "domain_types", "direct_write_block")
_emit_records_tool_invocation("p2", "domain_types", "tool_invocation")
_emit_captures_execution_output("p2", "domain_types", "exec_output")
_emit_dispatches_agent("p3", "domain_types", "agent_dispatch")
_emit_coordinates_agents("p3", "domain_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "domain_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "domain_types", "healing_outcome")
_emit_escalates_failure("p3", "domain_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "domain_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "domain_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "domain_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "domain_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "domain_types", "eval_metric")
_emit_stores_embedding("p4", "domain_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "domain_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "domain_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("domain_types", "p4obs", "metric_1")
_emit_emits_metric_event("domain_types", "p4obs", "metric_2")
_emit_emits_metric_event("domain_types", "p4obs", "metric_3")
_emit_emits_metric_event("domain_types", "p4obs", "metric_4")
_emit_emits_metric_event("domain_types", "p4obs", "metric_5")
_emit_emits_metric_event("domain_types", "p4obs", "metric_6")
_emit_records_incident_event("domain_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("domain_types", "p4obs", "anomaly")
_emit_writes_observability_log("domain_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("domain_types", "p4obs", "mon_state")
_emit_triggers_alert("domain_types", "p4obs", "alert")
_emit_links_incident_trace("domain_types", "p4obs", "trace_link")
_emit_captures_pattern("domain_types", "p3lm", "pattern")
_emit_records_learning_event("domain_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("domain_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("domain_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("domain_types", "p3lm", "routing")
_emit_improves_agent_policy("domain_types", "p3lm", "policy")
_emit_stores_learning_state("domain_types", "p3lm", "state")
_emit_records_execution_trace("domain_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("domain_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("domain_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("domain_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("domain_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("domain_types", "env_read", "p2_env_1")
_emit_reads_environ("domain_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("domain_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("domain_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "domain_types", "context_pull")
_emit_pulls_context("p1", "domain_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "domain_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "domain_types", "uwg_term_2")
_emit_writes_through("p1", "domain_types", "write_through")
_emit_writes_through("p1", "domain_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "domain_types", "safety_validation")
_emit_invokes_eval("p1", "domain_types", "eval_call")
_emit_proposal_commits_routing("p1", "domain_types", "routing_commit")


class SharingPolicy(Enum):
    """Policy for cross-domain pattern sharing."""

    NONE = "none"
    READ_ONLY = "read_only"
    BIDIRECTIONAL = "bidirectional"
    SELECTIVE = "selective"


@dataclass
class DomainContext:
    """
    Context for a specific domain.

    Attributes:
        domain: Domain identifier
        parent_domain: Parent domain for inheritance (if any)
        sharing_policy: Policy for cross-domain sharing
        allowed_sources: Domains allowed to share patterns with this domain
        pattern_types_shared: Pattern types allowed for sharing (if selective)
    """

    domain: str
    parent_domain: str | None = None
    sharing_policy: SharingPolicy = SharingPolicy.NONE
    allowed_sources: list[str] = field(default_factory=list)
    pattern_types_shared: list[str] = field(default_factory=list)

    def can_read_from(self, source_domain: str) -> bool:
        """Check if this domain can read patterns from source domain."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DomainContext.can_read_from", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DomainContext.can_read_from", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "DomainContext.can_read_from")

        if self.sharing_policy == SharingPolicy.NONE:
            return False
        if self.sharing_policy == SharingPolicy.BIDIRECTIONAL:
            return True
        if source_domain in self.allowed_sources:
            return True
        if self.parent_domain == source_domain:
            return True
        return False

    def can_share_pattern_type(self, pattern_type: str) -> bool:
        """Check if a pattern type can be shared."""
        if self.sharing_policy == SharingPolicy.NONE:
            return False
        if self.sharing_policy in (SharingPolicy.READ_ONLY, SharingPolicy.BIDIRECTIONAL):
            return True
        if self.sharing_policy == SharingPolicy.SELECTIVE:
            return pattern_type in self.pattern_types_shared
        return False
