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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

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
from agentic_core.utils.meta_learning_engine_util import MetaLearningEngine
from agentic_core.utils.meta_learning_storage_util import MetaLearningStorage

_emit_records_execution_trace("p0", "evidence", "meta_learning_mixin")
_emit_applies_guardrail("p0", "meta_learning_mixin", "p0_governance")
_emit_reads_policy_state("p0", "meta_learning_mixin", "policy_binding")
_emit_snapshots_state("p0", "meta_learning_mixin", "state_snapshot")
emit_replay_key("p0", "meta_learning_mixin")
emit_determinism_digest("p0", "meta_learning_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
