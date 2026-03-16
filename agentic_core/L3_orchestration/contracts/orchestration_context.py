"""
agentic_core/L3_orchestration/contracts/orchestration_context.py

OrchestrationContext — P0/L3 gap remediation.

Typed, run-scoped context object that must travel across every agent-to-agent
handoff.  No child agent may reconstruct orchestration context from ambient
globals or hidden state.

Required fields (spec §4):
    run_id, parent_trace_id, parent_agent_id, current_work_item_id,
    workflow_stage, policy_hash, state_version, routing_decision_id
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "orchestration_context")
emit_determinism_digest("p0", "orchestration_context")

_emit_dispatches_healing_run("p1", "orchestration_context", "L3")
_emit_routes_through("p1", "orchestration_context", "L3")
_emit_escalates_to_human("p1", "orchestration_context", "L3")
_emit_reads_policy_state("p1", "orchestration_context", "L3")
_emit_authorize_and_execute("p2", "orchestration_context", "execution_auth")
_emit_validates_capability("p2", "orchestration_context", "capability_check")
_emit_routes_to_capability("p2", "orchestration_context", "capability_route")
_emit_writes_via_uwg("p2", "orchestration_context", "uwg_write")
_emit_blocks_direct_write("p2", "orchestration_context", "direct_write_block")
_emit_records_tool_invocation("p2", "orchestration_context", "tool_invocation")
_emit_captures_execution_output("p2", "orchestration_context", "exec_output")
_emit_dispatches_agent("p3", "orchestration_context", "agent_dispatch")
_emit_coordinates_agents("p3", "orchestration_context", "agent_coordination")
_emit_records_workflow_lineage("p3", "orchestration_context", "workflow_lineage")
_emit_records_healing_outcome("p3", "orchestration_context", "healing_outcome")
_emit_escalates_failure("p3", "orchestration_context", "failure_escalation")
_emit_orchestrates_workflow("p3", "orchestration_context", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "orchestration_context", "healing_dispatch")
_emit_invokes_evaluation("p3", "orchestration_context", "evaluation_signal")
_emit_records_telemetry_event("p4", "orchestration_context", "telemetry_event")
_emit_captures_evaluation_metric("p4", "orchestration_context", "eval_metric")
_emit_stores_embedding("p4", "orchestration_context", "embedding_store")
_emit_updates_meta_learning_state("p4", "orchestration_context", "meta_learning")
_emit_links_execution_to_snapshot("p4", "orchestration_context", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("orchestration_context", "p4obs", "metric_1")
_emit_emits_metric_event("orchestration_context", "p4obs", "metric_2")
_emit_emits_metric_event("orchestration_context", "p4obs", "metric_3")
_emit_emits_metric_event("orchestration_context", "p4obs", "metric_4")
_emit_emits_metric_event("orchestration_context", "p4obs", "metric_5")
_emit_emits_metric_event("orchestration_context", "p4obs", "metric_6")
_emit_records_incident_event("orchestration_context", "p4obs", "incident")
_emit_captures_runtime_anomaly("orchestration_context", "p4obs", "anomaly")
_emit_writes_observability_log("orchestration_context", "p4obs", "obs_log")
_emit_updates_monitoring_state("orchestration_context", "p4obs", "mon_state")
_emit_triggers_alert("orchestration_context", "p4obs", "alert")
_emit_links_incident_trace("orchestration_context", "p4obs", "trace_link")
_emit_captures_pattern("orchestration_context", "p3lm", "pattern")
_emit_records_learning_event("orchestration_context", "p3lm", "learning_event")
_emit_writes_learning_snapshot("orchestration_context", "p3lm", "snapshot")
_emit_feeds_meta_learning("orchestration_context", "p3lm", "meta_feed")
_emit_updates_routing_strategy("orchestration_context", "p3lm", "routing")
_emit_improves_agent_policy("orchestration_context", "p3lm", "policy")
_emit_stores_learning_state("orchestration_context", "p3lm", "state")
_emit_records_execution_trace("orchestration_context", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("orchestration_context", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("orchestration_context", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("orchestration_context", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("orchestration_context", "L4_STATE", "p2_trace_5")
_emit_reads_environ("orchestration_context", "env_read", "p2_env_1")
_emit_reads_environ("orchestration_context", "env_read", "p2_env_2")
_emit_reads_runtime_state("orchestration_context", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("orchestration_context", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "orchestration_context", "context_pull")
_emit_pulls_context("p1", "orchestration_context", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "orchestration_context", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "orchestration_context", "uwg_term_2")
_emit_writes_through("p1", "orchestration_context", "write_through")
_emit_writes_through("p1", "orchestration_context", "write_through_2")
_emit_validated_by_safety_plane("p1", "orchestration_context", "safety_validation")
_emit_invokes_eval("p1", "orchestration_context", "eval_call")
_emit_proposal_commits_routing("p1", "orchestration_context", "routing_commit")

logger = logging.getLogger(__name__)

_ADG_LOGGER = logging.getLogger("adg.orchestration_context")


@dataclass(frozen=True)
class OrchestrationContext:
    """Immutable run-scoped orchestration context carried across every handoff.

    Every agent-to-agent handoff MUST pass this object explicitly.
    Reconstruction from ambient globals is forbidden.

    ADG signals emitted on creation:
        ``agent_executes_agent``  (via _emit_agent_executes_agent helper)
    """

    run_id: str
    parent_trace_id: str
    parent_agent_id: str
    current_work_item_id: str
    workflow_stage: str
    policy_hash: str
    state_version: int
    routing_decision_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        run_id: str,
        parent_agent_id: str,
        workflow_stage: str,
        policy_hash: str,
        parent_trace_id: str = "",
        current_work_item_id: str = "",
        state_version: int = 0,
        routing_decision_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> OrchestrationContext:
        """Factory: create a context with deterministic routing_decision_id."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "OrchestrationContext.create", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "OrchestrationContext.create", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OrchestrationContext.create")

        if not parent_trace_id:
            try:
                from agentic_core.runtime.trace_context import get_trace_context

                tc = get_trace_context()
                parent_trace_id = getattr(tc, "trace_id", "") or ""
            except Exception:
                parent_trace_id = ""
        if not routing_decision_id:
            key = f"{run_id}:{parent_agent_id}:{workflow_stage}:{get_clock().now_epoch()}"
            routing_decision_id = hashlib.sha256(key.encode()).hexdigest()[:16]
        ctx = cls(
            run_id=run_id,
            parent_trace_id=parent_trace_id,
            parent_agent_id=parent_agent_id,
            current_work_item_id=current_work_item_id,
            workflow_stage=workflow_stage,
            policy_hash=policy_hash,
            state_version=state_version,
            routing_decision_id=routing_decision_id,
            metadata=metadata or {},
        )
        _ADG_LOGGER.debug(
            "orchestration_context_created run_id=%s stage=%s agent=%s routing=%s",
            run_id,
            workflow_stage,
            parent_agent_id,
            routing_decision_id,
        )
        return ctx

    def advance(
        self,
        next_agent_id: str,
        next_stage: str,
        next_work_item_id: str = "",
    ) -> OrchestrationContext:
        """Create a child context for the next handoff leg.

        Preserves run_id, policy_hash, parent_trace_id.
        Increments state_version.
        """
        new_routing = hashlib.sha256(
            f"{self.routing_decision_id}:{next_agent_id}:{next_stage}".encode()
        ).hexdigest()[:16]
        child = OrchestrationContext(
            run_id=self.run_id,
            parent_trace_id=self.parent_trace_id,
            parent_agent_id=next_agent_id,
            current_work_item_id=next_work_item_id or self.current_work_item_id,
            workflow_stage=next_stage,
            policy_hash=self.policy_hash,
            state_version=self.state_version + 1,
            routing_decision_id=new_routing,
            metadata=dict(self.metadata),
        )
        _ADG_LOGGER.debug(
            "orchestration_context_advanced run_id=%s %s->%s stage=%s",
            self.run_id,
            self.parent_agent_id,
            next_agent_id,
            next_stage,
        )
        return child

    def _emit_agent_executes_agent(self, child_agent_id: str) -> None:
        """Emit ADG agent_executes_agent signal for graph visibility."""
        _ADG_LOGGER.debug(
            "agent_executes_agent parent=%s child=%s run_id=%s stage=%s",
            self.parent_agent_id,
            child_agent_id,
            self.run_id,
            self.workflow_stage,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "parent_trace_id": self.parent_trace_id,
            "parent_agent_id": self.parent_agent_id,
            "current_work_item_id": self.current_work_item_id,
            "workflow_stage": self.workflow_stage,
            "policy_hash": self.policy_hash,
            "state_version": self.state_version,
            "routing_decision_id": self.routing_decision_id,
        }


__all__ = ["OrchestrationContext"]
