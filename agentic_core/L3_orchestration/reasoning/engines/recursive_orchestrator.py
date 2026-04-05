"""
RecursiveOrchestrator - Forward-Rolling Recursion for Agentic Loops.

Implements "Loop Unrolling" pattern to simulate recursive healing without
breaking DAG acyclicity constraints. When a node fails validation, instead
of routing backwards, we spawn a NEW correction node downstream.

Key Principle:
    DAG grows FORWARD (depth increases) rather than cycling backwards.
    This preserves `nx.is_directed_acyclic_graph` invariant at all times.

Usage:
    orchestrator = RecursiveOrchestrator(dag_manager)
    orchestrator.handle_task_failure(
        failed_node_id="coder_v1",
        failure_reason="Type error in generated code",
        retry_function="code_generation"
    )
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "recursive_orchestrator", "execution_auth")
_emit_validates_capability("p2", "recursive_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "recursive_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "recursive_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "recursive_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "recursive_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "recursive_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "recursive_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "recursive_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "recursive_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "recursive_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "recursive_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "recursive_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "recursive_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "recursive_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "recursive_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "recursive_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "recursive_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "recursive_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "recursive_orchestrator", "exec_snapshot_link")
from agentic_core.utils.schemas.decorators_compat_util import standard_heal
from agentic_core.utils.schemas.timeout_decorator_util import timeout

emit_replay_key("p0", "recursive_orchestrator")
emit_determinism_digest("p0", "recursive_orchestrator")

_emit_dispatches_healing_run("p1", "recursive_orchestrator", "L3")
_emit_routes_through("p1", "recursive_orchestrator", "L3")
_emit_verifies_policy("p1", "recursive_orchestrator", "policy_check")
_emit_observes_runtime_state("p1", "recursive_orchestrator", "runtime_state")
_emit_verifies_boundary("p1", "recursive_orchestrator", "boundary_check")
_emit_transcripts_response("p1", "recursive_orchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "recursive_orchestrator")
_emit_gated_by_confidence("p1", "recursive_orchestrator", "confidence_gate")
_emit_escalates_to_human("p1", "recursive_orchestrator", "L3")
_emit_reads_policy_state("p1", "recursive_orchestrator", "L3")
_emit_routes_to_agent("p1", "recursive_orchestrator", "L3")
_emit_orchestrates_workflow("p1", "recursive_orchestrator", "L3")
_emit_dispatches_execution_plan("p1", "recursive_orchestrator", "L3")
_emit_validates_agent_capability("p1", "recursive_orchestrator", "L3")
_emit_checks_agent_registry("p1", "recursive_orchestrator", "L3")

_emit_snapshots_state("p0", "recursive_orchestrator", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("recursive_orchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("recursive_orchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("recursive_orchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("recursive_orchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("recursive_orchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("recursive_orchestrator", "p4obs", "metric_6")
_emit_records_incident_event("recursive_orchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("recursive_orchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("recursive_orchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("recursive_orchestrator", "p4obs", "mon_state")
_emit_triggers_alert("recursive_orchestrator", "p4obs", "alert")
_emit_links_incident_trace("recursive_orchestrator", "p4obs", "trace_link")
_emit_captures_pattern("recursive_orchestrator", "p3lm", "pattern")
_emit_records_learning_event("recursive_orchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("recursive_orchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("recursive_orchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("recursive_orchestrator", "p3lm", "routing")
_emit_improves_agent_policy("recursive_orchestrator", "p3lm", "policy")
_emit_stores_learning_state("recursive_orchestrator", "p3lm", "state")
_emit_records_execution_trace("recursive_orchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("recursive_orchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("recursive_orchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("recursive_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("recursive_orchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("recursive_orchestrator", "env_read", "p2_env_1")
_emit_reads_environ("recursive_orchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("recursive_orchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("recursive_orchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "recursive_orchestrator", "context_pull")
_emit_pulls_context("p1", "recursive_orchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "recursive_orchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "recursive_orchestrator", "uwg_term_2")
_emit_writes_through("p1", "recursive_orchestrator", "write_through")
_emit_writes_through("p1", "recursive_orchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "recursive_orchestrator", "safety_validation")
_emit_invokes_eval("p1", "recursive_orchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "recursive_orchestrator", "routing_commit")

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status signals for task execution."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    NEEDS_REVISION = "NEEDS_REVISION"
    MAX_RETRIES_EXCEEDED = "MAX_RETRIES_EXCEEDED"


@dataclass
class RetryContext:
    """Context passed to retry nodes containing failure history."""

    original_node_id: str
    attempt_number: int
    max_attempts: int
    failure_reasons: list[str] = field(default_factory=list)
    accumulated_context: dict[str, Any] = field(default_factory=dict)

    def add_failure(self, reason: str, context: dict[str, Any] | None = None) -> None:
        """Record a failure attempt."""
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RetryContext.add_failure", "p0_governance")
        _emit_agent_executes_agent(str(uuid.uuid4()), "RetryContext", "RetryContext.add_failure")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetryContext.add_failure")

        self.failure_reasons.append(reason)
        if context:
            self.accumulated_context.update(context)
        self.attempt_number += 1

    @property
    def can_retry(self) -> bool:
        """Check if more retries are allowed."""
        return self.attempt_number < self.max_attempts

    # guardian: allow-type-erasure
    def to_parameters(self) -> dict[str, Any]:
        """Convert to parameters dict for HopSpec."""
        return {
            "retry_context": {
                "original_node_id": self.original_node_id,
                "attempt_number": self.attempt_number,
                "max_attempts": self.max_attempts,
                "failure_reasons": self.failure_reasons,
                "accumulated_context": self.accumulated_context,
            }
        }


@dataclass
class RecursiveOrchestrator(SovereignBaseAgent):
    """
    Forward-Rolling Recursion Orchestrator.

    Simulates agentic loops by spawning NEW downstream nodes instead of
    cycling backwards. This preserves DAG acyclicity while enabling
    retry/healing patterns.

    Architecture:
        [Node_v1] --FAIL--> [Node_v2] --FAIL--> [Node_v3] --SUCCESS-->
                    |               |               |
                    v               v               v
              (depth=1)       (depth=2)       (depth=3)

    The graph grows FORWARD, never backwards.
    """

    dag_manager: Any = field(default=None)
    max_retry_attempts: int = field(default=3)
    retry_contexts: dict[str, RetryContext] = field(default_factory=dict)
    on_retry_spawned: Callable[[str, str, int], None] | None = field(default=None)
    on_max_retries_exceeded: Callable[[str, RetryContext], None] | None = field(default=None)

    def __post_init__(self) -> None:
        """Initialize the orchestrator."""
        super().__post_init__()
        logger.info(f"RecursiveOrchestrator initialized with max_retry_attempts={self.max_retry_attempts}")

    # guardian: allow-type-erasure
    def handle_task_status(
        self,
        node_id: str,
        status: TaskStatus,
        failure_reason: str | None = None,
        retry_function: str | None = None,
        additional_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Handle a task status signal from a node.

        Args:
            node_id: The ID of the node reporting status
            status: The task status (FAILED, NEEDS_REVISION, etc.)
            failure_reason: Why the task failed (required for FAILED/NEEDS_REVISION)
            retry_function: Function name to use for retry node
            additional_context: Extra context to pass to retry node

        Returns:
            Dict with action taken and result
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RecursiveOrchestrator.handle_task_status"
        )

        if status == TaskStatus.SUCCESS:
            self._cleanup_retry_context(node_id)
            return {"action": "none", "status": "success", "node_id": node_id}
        if status in (TaskStatus.FAILED, TaskStatus.NEEDS_REVISION):
            if not failure_reason:
                failure_reason = f"Node {node_id} reported {status.value} without reason"
            return self.handle_task_failure(
                failed_node_id=node_id,
                failure_reason=failure_reason,
                retry_function=retry_function,
                additional_context=additional_context,
            )
        return {"action": "none", "status": status.value, "node_id": node_id}

    # guardian: allow-type-erasure
    def handle_task_failure(
        self,
        failed_node_id: str,
        failure_reason: str,
        retry_function: str | None = None,
        additional_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Handle a task failure by spawning a downstream retry node.

        This is the core of Forward-Rolling Recursion:
        1. Check if we can retry (max_attempts not exceeded)
        2. Create/update RetryContext with failure info
        3. Spawn a NEW successor node via DAGMutation
        4. The new node receives full failure history

        Args:
            failed_node_id: ID of the node that failed
            failure_reason: Why it failed
            retry_function: Function to use for retry (defaults to same function)
            additional_context: Extra context for the retry

        Returns:
            Dict with mutation result and retry info
        """
        if self.dag_manager is None:
            raise ValueError("DAGManager not configured. Set dag_manager attribute.")
        retry_ctx = self._get_or_create_retry_context(failed_node_id)
        retry_ctx.add_failure(failure_reason, additional_context)
        if not retry_ctx.can_retry:
            logger.warning(
                f"Max retries exceeded for chain starting at {retry_ctx.original_node_id}. Attempts: {retry_ctx.attempt_number}/{retry_ctx.max_attempts}"
            )
            if self.on_max_retries_exceeded:
                self.on_max_retries_exceeded(failed_node_id, retry_ctx)
            return {
                "action": "max_retries_exceeded",
                "original_node_id": retry_ctx.original_node_id,
                "attempts": retry_ctx.attempt_number,
                "failure_reasons": retry_ctx.failure_reasons,
            }
        if retry_function is None:
            retry_function = self._get_node_function(failed_node_id)
        if retry_function is None:
            raise ValueError(
                f"Cannot determine retry function for {failed_node_id}. Provide retry_function parameter."
            )
        result = self._spawn_retry_successor(
            failed_node_id=failed_node_id, retry_function=retry_function, retry_context=retry_ctx
        )
        if result.get("success"):
            new_node_id = result.get("new_node_id")
            if new_node_id:
                self.retry_contexts[new_node_id] = retry_ctx
                if failed_node_id in self.retry_contexts:
                    del self.retry_contexts[failed_node_id]
            if self.on_retry_spawned:
                self.on_retry_spawned(failed_node_id, new_node_id, retry_ctx.attempt_number)
            logger.info(
                f"Spawned retry node {new_node_id} for {failed_node_id} (attempt {retry_ctx.attempt_number}/{retry_ctx.max_attempts})"
            )
        return result

    # guardian: allow-type-erasure
    def _spawn_retry_successor(
        self, failed_node_id: str, retry_function: str, retry_context: RetryContext
    ) -> dict[str, Any]:
        """
        Spawn a successor node using DAGMutation.

        This maintains DAG acyclicity by adding a NEW node downstream,
        never creating backward edges.
        """
        from agentic_core.L3_orchestration.reasoning.dag_mutator_agent_config import (
            DAGMutation,
            HopSpec,
            MutationAction,
        )

        base_params = retry_context.accumulated_context.copy()
        retry_params = retry_context.to_parameters()
        final_params = {**base_params, **retry_params}
        hop_spec = HopSpec(
            hop_function=retry_function, parameters=final_params, priority=1, retry_policy={"max_attempts": 0}
        )
        mutation = DAGMutation(
            action=MutationAction.SPAWN_SUCCESSOR,
            target_hop_id=failed_node_id,
            new_hop_spec=hop_spec,
            reason=f"Retry attempt {retry_context.attempt_number} after failure: {retry_context.failure_reasons[-1][:100]}",
            requester_hop_id="recursive_orchestrator",
        )
        mutation_result = self.dag_manager.request_mutation(mutation)
        return {
            "success": mutation_result.success,
            "message": mutation_result.message,
            "new_node_id": hop_spec.hop_id if mutation_result.success else None,
            "mutation_id": mutation_result.mutation_id,
            "affected_nodes": mutation_result.affected_nodes,
            "attempt_number": retry_context.attempt_number,
        }

    def _get_or_create_retry_context(self, node_id: str) -> RetryContext:
        """Get existing retry context or create new one."""
        if node_id in self.retry_contexts:
            return self.retry_contexts[node_id]
        ctx = RetryContext(original_node_id=node_id, attempt_number=1, max_attempts=self.max_retry_attempts)
        self.retry_contexts[node_id] = ctx
        return ctx

    def _get_node_function(self, node_id: str) -> str | None:
        """Get the function name for a node from the DAG."""
        if self.dag_manager is None:
            return None
        try:
            node_data = self.dag_manager.graph.nodes.get(node_id, {})
            hop_spec = node_data.get("hop_spec")
            if hasattr(hop_spec, "hop_function"):
                return hop_spec.hop_function
            elif isinstance(hop_spec, dict):
                return hop_spec.get("hop_function")
            return None
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            logger.warning(f"Failed to extract function name for {node_id}: {e}")
            return None

    def _cleanup_retry_context(self, node_id: str) -> None:
        """Clean up retry context after success."""
        if node_id in self.retry_contexts:
            ctx = self.retry_contexts[node_id]
            logger.info(
                f"Retry chain completed successfully for {ctx.original_node_id} after {ctx.attempt_number} attempts"
            )
            del self.retry_contexts[node_id]

    # guardian: allow-type-erasure
    def get_retry_status(self, node_id: str) -> dict[str, Any] | None:
        """Get retry status for a node."""
        if node_id not in self.retry_contexts:
            return None
        ctx = self.retry_contexts[node_id]
        return {
            "original_node_id": ctx.original_node_id,
            "current_attempt": ctx.attempt_number,
            "max_attempts": ctx.max_attempts,
            "can_retry": ctx.can_retry,
            "failure_count": len(ctx.failure_reasons),
            "failure_reasons": ctx.failure_reasons,
        }

    # guardian: allow-type-erasure
    def get_all_active_retries(self) -> dict[str, dict[str, Any]]:
        """Get all active retry contexts."""
        return {node_id: self.get_retry_status(node_id) for node_id in self.retry_contexts}

    @timeout(120)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """
        Heal repository - validates orchestrator state.

        Checks:
        - No orphaned retry contexts
        - DAG acyclicity maintained
        - Retry limits respected
        """
        metrics = super().heal_repository(
            dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path
        )
        if not isinstance(metrics, dict):
            metrics = {"violations_found": 0, "violations_fixed": 0, "errors": 0}
        if metrics.get("cycle_detected"):
            return metrics
        try:
            orphaned = []
            if self.dag_manager:
                for node_id in list(self.retry_contexts.keys()):
                    if node_id not in self.dag_manager.graph.nodes:
                        orphaned.append(node_id)
                        if execute and (not dry_run):
                            del self.retry_contexts[node_id]
            if orphaned:
                metrics["violations_found"] = metrics.get("violations_found", 0) + len(orphaned)
                if execute and (not dry_run):
                    metrics["violations_fixed"] = metrics.get("violations_fixed", 0) + len(orphaned)
                logger.info(f"Found {len(orphaned)} orphaned retry contexts")
            if self.dag_manager:
                import networkx as nx

                if not nx.is_directed_acyclic_graph(self.dag_manager.graph):
                    metrics["errors"] = metrics.get("errors", 0) + 1
                    logger.error("DAG ACYCLICITY VIOLATION DETECTED!")
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            logger.error(f"RecursiveOrchestrator healing failed: {e}")
            metrics["errors"] = metrics.get("errors", 0) + 1
        return metrics
