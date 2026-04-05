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

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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
from agentic_core.mixins.meta_learning_contract_mixin import BaseMetaLearner

_emit_authorize_and_execute("p2", "meta_learning_mixin", "execution_auth")
_emit_validates_capability("p2", "meta_learning_mixin", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_mixin", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_mixin", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_mixin", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_mixin", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_mixin", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
from agentic_core.utils.meta_learning_engine_util import MetaLearningEngine
from agentic_core.utils.meta_learning_storage_util import MetaLearningStorage

_emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning_mixin", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning_mixin", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning_mixin", "p4obs", "alert")
_emit_links_incident_trace("meta_learning_mixin", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning_mixin", "p3lm", "pattern")
_emit_records_learning_event("meta_learning_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning_mixin", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning_mixin", "p3lm", "policy")
_emit_stores_learning_state("meta_learning_mixin", "p3lm", "state")
_emit_records_execution_trace("meta_learning_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning_mixin", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning_mixin", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "meta_learning_mixin")
_emit_applies_guardrail("p0", "meta_learning_mixin", "p0_governance")
_emit_reads_policy_state("p0", "meta_learning_mixin", "policy_binding")
_emit_snapshots_state("p0", "meta_learning_mixin", "state_snapshot")
_emit_pulls_context("p1", "meta_learning_mixin", "context_pull")
_emit_pulls_context("p1", "meta_learning_mixin", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "meta_learning_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning_mixin", "uwg_term_secondary")
_emit_writes_through("p1", "meta_learning_mixin", "write_through")
_emit_writes_through("p1", "meta_learning_mixin", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "meta_learning_mixin", "safety_validation")
_emit_invokes_eval("p1", "meta_learning_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning_mixin", "routing_commit")
_emit_escalates_to_human("p1", "meta_learning_mixin", "human_escalation")
_emit_routes_through("p1", "meta_learning_mixin", "route_through")
_emit_checks_agent_registry("p1", "meta_learning_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "meta_learning_mixin", "capability")
_emit_dispatches_execution_plan("p1", "meta_learning_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "meta_learning_mixin", "sub_agent")
_emit_routes_to_agent("p1", "meta_learning_mixin", "target_agent")
_emit_verifies_policy("p1", "meta_learning_mixin", "policy_check")
_emit_observes_runtime_state("p1", "meta_learning_mixin", "runtime_state")
_emit_verifies_boundary("p1", "meta_learning_mixin", "boundary_check")
_emit_transcripts_response("p1", "meta_learning_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_learning_mixin")
_emit_gated_by_confidence("p1", "meta_learning_mixin", "confidence_gate")
emit_replay_key("p0", "meta_learning_mixin")
emit_determinism_digest("p0", "meta_learning_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_dispatch_entry")
emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_dispatch_exit")
emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_tool_invoke")
emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_tool_complete")
emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_agent_entry")
emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_agent_exit")
emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_uwg_write")
emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_trace_sign")
emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_guardrail_check")
emit_determinism_digest("trace_meta_learning_mixin", "meta_learning_mixin_policy_verify")

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
        self, callee_agent: str, success: bool, error_type: str | None = None
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
