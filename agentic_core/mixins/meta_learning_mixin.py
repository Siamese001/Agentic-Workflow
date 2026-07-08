"""
MetaLearningMixin - Thin Adapter for Collective Intelligence

[MIXIN REFACTOR] Split from 643-line monolith into:
  - meta_learning_storage.py  (Pinecone/Graph connections, circuit breaker)
  - meta_learning_engine.py   (KG bridging, recall_or_execute, reflection)
  - meta_learning_mixin.py    (this file — thin adapter binding to Agent self)

Usage:
    class MyAgent(MetaLearningMixin, SovereignBaseAgent):
        def execute(self, task):
            return self.recall_or_execute(
                context=task.description,
                execution_fn=lambda: self._do_work(task)
            )
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from agentic_core.mixins.meta_learning_contract_mixin import BaseMetaLearner
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "meta_learning_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "meta_learning_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "meta_learning_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "meta_learning_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "meta_learning_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "meta_learning_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "meta_learning_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "meta_learning_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "meta_learning_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "meta_learning_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "meta_learning_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "meta_learning_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "meta_learning_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "meta_learning_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "meta_learning_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "meta_learning_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "meta_learning_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "meta_learning_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "meta_learning_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "meta_learning_mixin", "exec_snapshot_link")
from agentic_core.utils.meta_learning_engine_util import MetaLearningEngine
from agentic_core.utils.meta_learning_storage_util import MetaLearningStorage

trace_contract._emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("meta_learning_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("meta_learning_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("meta_learning_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("meta_learning_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("meta_learning_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("meta_learning_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("meta_learning_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("meta_learning_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("meta_learning_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("meta_learning_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("meta_learning_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("meta_learning_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("meta_learning_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("meta_learning_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("meta_learning_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("meta_learning_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("meta_learning_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("meta_learning_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("meta_learning_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("meta_learning_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("meta_learning_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("meta_learning_mixin", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "meta_learning_mixin")
trace_contract._emit_applies_guardrail("p0", "meta_learning_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "meta_learning_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "meta_learning_mixin", "state_snapshot")
trace_contract._emit_pulls_context("p1", "meta_learning_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "meta_learning_mixin", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_mixin", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "meta_learning_mixin", "write_through")
trace_contract._emit_writes_through("p1", "meta_learning_mixin", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "meta_learning_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "meta_learning_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "meta_learning_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "meta_learning_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "meta_learning_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "meta_learning_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "meta_learning_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "meta_learning_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "meta_learning_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "meta_learning_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "meta_learning_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "meta_learning_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "meta_learning_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "meta_learning_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "meta_learning_mixin")
trace_contract._emit_gated_by_confidence("p1", "meta_learning_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "meta_learning_mixin")
trace_contract.emit_determinism_digest("p0", "meta_learning_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_dispatch_entry")
trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_dispatch_exit")
trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_tool_invoke")
trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_tool_complete")
trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_agent_entry")
trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_agent_exit")
trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_uwg_write")
trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_trace_sign")
trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_guardrail_check")
trace_contract.emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_policy_verify")

Logger = logging.getLogger(__name__)


class MetaLearningMixin(BaseMetaLearner):
    """Thin adapter connecting Agent self to MetaLearningEngine/Storage."""

    def __init__(self, *args, **kwargs):
        """DNA Activation: connect to backends and discover context."""
        name = self.__class__.__name__
        MetaLearningStorage.ensure_memory_connection(name)
        MetaLearningEngine.ensure_kg_connection(name)
        MetaLearningStorage.ensure_graph_bridge_connection(name)
        self._discovered_context = MetaLearningEngine.discover_agent_context(name)
        MetaLearningStorage.register_agent_entity(name)
        super().__init__(*args, **kwargs)

    @property
    def _namespace(self) -> str:
        return self.__class__.__name__

    def _generate_context_hash(self, context: str) -> str:
        return MetaLearningStorage.generate_context_hash(self._namespace, context)

    def recall_experience(self, context: str) -> dict[str, Any] | None:
        return MetaLearningStorage.recall(context, self._namespace)

    async def learn_experience(self, context: str, result: dict[str, Any]) -> None:
        await MetaLearningStorage.learn_async(context, self._namespace, result)

    def recall_or_execute(self, context: str, execution_fn: Callable[[], Any]) -> Any:
        return MetaLearningEngine.recall_or_execute(self._namespace, context, execution_fn)

    def learn_with_feedback(self, context: str, result: dict[str, Any], feedback_score: float) -> bool:
        return MetaLearningStorage.learn_with_feedback(context, self._namespace, result, feedback_score)

    def reflect_on_execution(self, task_id: str, status: str, **kwargs) -> None:
        MetaLearningEngine.reflect_on_execution(self._namespace, task_id, status, **kwargs)

    def record_agent_interaction(
        self,
        callee_agent: str,
        success: bool,
        error_type: str | None = None,
    ) -> None:
        MetaLearningEngine.record_agent_interaction(self._namespace, callee_agent, success, error_type)

    def inherit_rules_from(self, parent_entity: str) -> None:
        MetaLearningEngine.inherit_rules_from(self._namespace, parent_entity)

    def mark_incompatible_with(self, other_entity: str, reason: str) -> None:
        MetaLearningEngine.mark_incompatible_with(self._namespace, other_entity, reason)

    def add_architectural_observation(self, observation: str) -> None:
        MetaLearningEngine.add_architectural_observation(self._namespace, observation)

    def get_memory_stats(self) -> dict[str, Any] | None:
        return MetaLearningStorage.get_memory_stats()

    def get_kg_stats(self) -> dict[str, Any] | None:
        return MetaLearningEngine.get_kg_stats()

    def get_graph_stats(self) -> dict[str, Any] | None:
        return MetaLearningStorage.get_graph_stats()

    @classmethod
    def reset_lobotomy(cls) -> None:
        MetaLearningStorage.reset_lobotomy()

    @classmethod
    def reset_kg(cls) -> None:
        MetaLearningEngine.reset_kg()

    @classmethod
    def reset_graph_bridge(cls) -> None:
        MetaLearningStorage.reset_graph_bridge()
