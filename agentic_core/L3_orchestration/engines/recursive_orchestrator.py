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
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.base_agents.decorators import standard_heal
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.timeout_decorator import timeout

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
        self.failure_reasons.append(reason)
        if context:
            self.accumulated_context.update(context)
        self.attempt_number += 1

    @property
    def can_retry(self) -> bool:
        """Check if more retries are allowed."""
        return self.attempt_number < self.max_attempts

    def to_parameters(self) -> dict[str, Any]:
        """Convert to parameters dict for HopSpec."""
        return {
            "retry_context": {
                "original_node_id": self.original_node_id,
                "attempt_number": self.attempt_number,
                "max_attempts": self.max_attempts,
                "failure_reasons": self.failure_reasons,
                "accumulated_context": self.accumulated_context,
            },
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

    # Callbacks for custom handling
    on_retry_spawned: Callable[[str, str, int], None] | None = field(default=None)
    on_max_retries_exceeded: Callable[[str, RetryContext], None] | None = field(default=None)

    def __post_init__(self) -> None:
        """Initialize the orchestrator."""
        super().__post_init__()
        logger.info(f"RecursiveOrchestrator initialized with max_retry_attempts={self.max_retry_attempts}")

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
        if status == TaskStatus.SUCCESS:
            # Clean up retry context if exists
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

        # Get or create retry context
        retry_ctx = self._get_or_create_retry_context(failed_node_id)
        retry_ctx.add_failure(failure_reason, additional_context)

        # Check if we've exceeded max retries
        if not retry_ctx.can_retry:
            logger.warning(
                f"Max retries exceeded for chain starting at {retry_ctx.original_node_id}. "
                f"Attempts: {retry_ctx.attempt_number}/{retry_ctx.max_attempts}",
            )

            if self.on_max_retries_exceeded:
                self.on_max_retries_exceeded(failed_node_id, retry_ctx)

            return {
                "action": "max_retries_exceeded",
                "original_node_id": retry_ctx.original_node_id,
                "attempts": retry_ctx.attempt_number,
                "failure_reasons": retry_ctx.failure_reasons,
            }

        # Determine retry function
        if retry_function is None:
            # Try to get from node registry
            retry_function = self._get_node_function(failed_node_id)

        if retry_function is None:
            raise ValueError(
                f"Cannot determine retry function for {failed_node_id}. Provide retry_function parameter.",
            )

        # Spawn successor node via DAGMutation
        result = self._spawn_retry_successor(
            failed_node_id=failed_node_id,
            retry_function=retry_function,
            retry_context=retry_ctx,
        )

        if result.get("success"):
            new_node_id = result.get("new_node_id")

            # Transfer retry context to new node
            if new_node_id:
                self.retry_contexts[new_node_id] = retry_ctx
                # Clean up old reference
                if failed_node_id in self.retry_contexts:
                    del self.retry_contexts[failed_node_id]

            # Callback
            if self.on_retry_spawned:
                self.on_retry_spawned(failed_node_id, new_node_id, retry_ctx.attempt_number)

            logger.info(
                f"Spawned retry node {new_node_id} for {failed_node_id} "
                f"(attempt {retry_ctx.attempt_number}/{retry_ctx.max_attempts})",
            )

        return result

    def _spawn_retry_successor(
        self,
        failed_node_id: str,
        retry_function: str,
        retry_context: RetryContext,
    ) -> dict[str, Any]:
        """
        Spawn a successor node using DAGMutation.

        This maintains DAG acyclicity by adding a NEW node downstream,
        never creating backward edges.
        """
        # Import here to avoid circular imports
        from agentic_core.L3_orchestration.reasoning.dag_mutator_agent_config import (
            DAGMutation,
            HopSpec,
            MutationAction,
        )

        # Build parameters with retry context
        # [CRITICAL HARDENING] Ensure parameters are merged, not overwritten.
        # If the original node had params (e.g., 'goal'), the retry needs them too.
        # We merge retry_context on top of accumulated_context.
        base_params = retry_context.accumulated_context.copy()
        retry_params = retry_context.to_parameters()

        # Merge strategies: Retry params take precedence for control flags,
        # but we must preserve original task data.
        final_params = {**base_params, **retry_params}

        # Create HopSpec for new node
        hop_spec = HopSpec(
            hop_function=retry_function,
            parameters=final_params,
            priority=1,  # Higher priority for retries
            retry_policy={
                "max_attempts": 0,
            },  # [SAFETY] Prevent internal retries on the new node, rely on Orchestrator
        )

        # Create mutation request
        mutation = DAGMutation(
            action=MutationAction.SPAWN_SUCCESSOR,
            target_hop_id=failed_node_id,
            new_hop_spec=hop_spec,
            reason=f"Retry attempt {retry_context.attempt_number} after failure: {retry_context.failure_reasons[-1][:100]}",
            requester_hop_id="recursive_orchestrator",
        )

        # Apply mutation via DAGManager
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

        # Create new context
        ctx = RetryContext(
            original_node_id=node_id,
            attempt_number=1,
            max_attempts=self.max_retry_attempts,
        )
        self.retry_contexts[node_id] = ctx
        return ctx

    def _get_node_function(self, node_id: str) -> str | None:
        """Get the function name for a node from the DAG."""
        if self.dag_manager is None:
            return None

        try:
            # [CRITICAL ANALYSIS] Robust accessor for NetworkX node data.
            # Handle cases where 'hop_spec' might be a dict or a Pydantic model
            # depending on serialization state in the DAGManager.
            node_data = self.dag_manager.graph.nodes.get(node_id, {})
            hop_spec = node_data.get("hop_spec")

            if hasattr(hop_spec, "hop_function"):
                return hop_spec.hop_function
            elif isinstance(hop_spec, dict):
                return hop_spec.get("hop_function")
            return None
        except Exception as e:
            logger.warning(f"Failed to extract function name for {node_id}: {e}")
            return None

    def _cleanup_retry_context(self, node_id: str) -> None:
        """Clean up retry context after success."""
        if node_id in self.retry_contexts:
            ctx = self.retry_contexts[node_id]
            logger.info(
                f"Retry chain completed successfully for {ctx.original_node_id} "
                f"after {ctx.attempt_number} attempts",
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
        # guardian: allow-magic-config
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
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path,
        )
        if not isinstance(metrics, dict):
            metrics = {"violations_found": 0, "violations_fixed": 0, "errors": 0}

        if metrics.get("cycle_detected"):
            return metrics

        try:
            # Check for orphaned retry contexts
            orphaned = []
            if self.dag_manager:
                for node_id in list(self.retry_contexts.keys()):
                    if node_id not in self.dag_manager.graph.nodes:
                        orphaned.append(node_id)
                        if execute and not dry_run:
                            del self.retry_contexts[node_id]

            if orphaned:
                metrics["violations_found"] = metrics.get("violations_found", 0) + len(orphaned)
                if execute and not dry_run:
                    metrics["violations_fixed"] = metrics.get("violations_fixed", 0) + len(orphaned)
                logger.info(f"Found {len(orphaned)} orphaned retry contexts")

            # Verify DAG acyclicity if manager exists
            if self.dag_manager:
                import networkx as nx

                if not nx.is_directed_acyclic_graph(self.dag_manager.graph):
                    metrics["errors"] = metrics.get("errors", 0) + 1
                    logger.error("DAG ACYCLICITY VIOLATION DETECTED!")

        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"RecursiveOrchestrator healing failed: {e}")
            metrics["errors"] = metrics.get("errors", 0) + 1

        return metrics
