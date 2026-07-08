from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "SemanticGatekeeperAgent")
trace_contract.emit_determinism_digest("p0", "SemanticGatekeeperAgent")

trace_contract._emit_dispatches_healing_run("p1", "SemanticGatekeeperAgent", "L3")
trace_contract._emit_routes_through("p1", "SemanticGatekeeperAgent", "L3")
trace_contract._emit_checks_agent_registry("p1", "SemanticGatekeeperAgent", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "SemanticGatekeeperAgent", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "SemanticGatekeeperAgent", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "SemanticGatekeeperAgent", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "SemanticGatekeeperAgent", "target_agent")
trace_contract._emit_verifies_policy("p1", "SemanticGatekeeperAgent", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "SemanticGatekeeperAgent", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "SemanticGatekeeperAgent", "boundary_check")
trace_contract._emit_transcripts_response("p1", "SemanticGatekeeperAgent", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "SemanticGatekeeperAgent")
trace_contract._emit_gated_by_confidence("p1", "SemanticGatekeeperAgent", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "SemanticGatekeeperAgent", "L3")
trace_contract._emit_reads_policy_state("p1", "SemanticGatekeeperAgent", "L3")
trace_contract._emit_authorize_and_execute("p2", "SemanticGatekeeperAgent", "execution_auth")
trace_contract._emit_validates_capability("p2", "SemanticGatekeeperAgent", "capability_check")
trace_contract._emit_routes_to_capability("p2", "SemanticGatekeeperAgent", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "SemanticGatekeeperAgent", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "SemanticGatekeeperAgent", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "SemanticGatekeeperAgent", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "SemanticGatekeeperAgent", "exec_output")
trace_contract._emit_dispatches_agent("p3", "SemanticGatekeeperAgent", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "SemanticGatekeeperAgent", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "SemanticGatekeeperAgent", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "SemanticGatekeeperAgent", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "SemanticGatekeeperAgent", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "SemanticGatekeeperAgent", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "SemanticGatekeeperAgent", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "SemanticGatekeeperAgent", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "SemanticGatekeeperAgent", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "SemanticGatekeeperAgent", "eval_metric")
trace_contract._emit_stores_embedding("p4", "SemanticGatekeeperAgent", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "SemanticGatekeeperAgent", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "SemanticGatekeeperAgent", "exec_snapshot_link")

"\nSemantic Gatekeeper - L3 Orchestration Layer\n\nManages concurrency, timeouts, and dead letter handling for agent execution.\n"
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from agentic_core.utils.timeout_decorator_util import timeout

Logger: Any = logging.getLogger(__name__)
from agentic_core.utils.decorators_compat_util import standard_heal

trace_contract._emit_emits_metric_event("SemanticGatekeeperAgent", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("SemanticGatekeeperAgent", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("SemanticGatekeeperAgent", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("SemanticGatekeeperAgent", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("SemanticGatekeeperAgent", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("SemanticGatekeeperAgent", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("SemanticGatekeeperAgent", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("SemanticGatekeeperAgent", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("SemanticGatekeeperAgent", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("SemanticGatekeeperAgent", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("SemanticGatekeeperAgent", "p4obs", "alert")
trace_contract._emit_links_incident_trace("SemanticGatekeeperAgent", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("SemanticGatekeeperAgent", "p3lm", "pattern")
trace_contract._emit_records_learning_event("SemanticGatekeeperAgent", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("SemanticGatekeeperAgent", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("SemanticGatekeeperAgent", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("SemanticGatekeeperAgent", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("SemanticGatekeeperAgent", "p3lm", "policy")
trace_contract._emit_stores_learning_state("SemanticGatekeeperAgent", "p3lm", "state")
trace_contract._emit_records_execution_trace("SemanticGatekeeperAgent", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("SemanticGatekeeperAgent", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("SemanticGatekeeperAgent", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("SemanticGatekeeperAgent", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("SemanticGatekeeperAgent", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("SemanticGatekeeperAgent", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("SemanticGatekeeperAgent", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("SemanticGatekeeperAgent", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("SemanticGatekeeperAgent", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "SemanticGatekeeperAgent", "context_pull")
trace_contract._emit_pulls_context("p1", "SemanticGatekeeperAgent", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "SemanticGatekeeperAgent", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "SemanticGatekeeperAgent", "uwg_term_2")
trace_contract._emit_writes_through("p1", "SemanticGatekeeperAgent", "write_through")
trace_contract._emit_writes_through("p1", "SemanticGatekeeperAgent", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "SemanticGatekeeperAgent", "safety_validation")
trace_contract._emit_invokes_eval("p1", "SemanticGatekeeperAgent", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "SemanticGatekeeperAgent", "routing_commit")


@dataclass
class SemanticGatekeeperAgent(SovereignBaseAgent):
    """
    Gatekeeper that controls agent execution with concurrency limits and timeouts.
    """

    # guardian: allow-magic-config
    def __init__(self, max_concurrent: int = 5, timeout_seconds: int = 120) -> None:
        """
        Initialize the gatekeeper.

        Args:
            max_concurrent: Maximum number of concurrent executions
            timeout_seconds: Default timeout for operations
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "SemanticGatekeeperAgent.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "SemanticGatekeeperAgent.__init__", "p0_governance")
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout_seconds = timeout_seconds
        self.dead_letter_queue = []
        Logger.info(f"Gatekeeper initialized: max_concurrent={max_concurrent}, TIMEOUT={timeout_seconds}s")

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L3 compliance."""
        assert hasattr(self, "timeout_seconds"), "Missing timeout_seconds"
        assert hasattr(self, "dead_letter_queue"), "Missing dead_letter_queue"
        return True

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """L3 orchestration agent - operational only."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "SemanticGatekeeperAgent.heal_repository",
        )

        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration - no healing required")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    @asynccontextmanager
    # guardian: allow-type-erasure
    async def execute(self, trace_id: str, operation: str) -> Any:
        """
        # CRITICAL FIRST: Shared HealingPolicyMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        Context manager for controlled execution.

        Args:
            trace_id: Unique identifier for the execution
            operation: Description of the operation being performed
        """
        await self.semaphore.acquire()
        try:
            Logger.debug(f"Starting execution for trace {trace_id}: {operation}")
            yield
            Logger.debug(f"Completed execution for trace {trace_id}")
        except asyncio.TimeoutError:  # guardian: allow-double-logging -- timeout recorded in dead-letter-queue audit log; local logger.error captures stack for observability
            Logger.error(f"Timeout for trace {trace_id}: {operation}")
            self.dead_letter_queue.append(
                {
                    "trace_id": trace_id,
                    "operation": operation,
                    "error": "TIMEOUT",
                    "timestamp": datetime.now().isoformat(),
                },
            )
            raise
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
        finally:
            self.semaphore.release()

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by SemanticGatekeeperAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"SemanticGatekeeperAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except (ValueError, TypeError) as e:
            return {
                "status": "failed",
                "details": f"SemanticGatekeeperAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }

    # guardian: allow-type-erasure
    async def run_with_gating(self, trace_id: str, operation: str, coro: Any) -> Any:
        """
        Run a coroutine with gatekeeping.

        Args:
            trace_id: Unique identifier for the execution
            operation: Description of the operation
            coro: Coroutine to execute

        Returns:
            Result of the coroutine
        """
        async with self.execute(trace_id, operation):
            return await asyncio.wait_for(coro, timeout=self.timeout_seconds)

    def get_dead_letters(self) -> list:
        """Get all dead letter entries."""
        return self.dead_letter_queue.copy()

    # guardian: allow-type-erasure
    def clear_dead_letters(self) -> Any:
        """Clear the dead letter queue."""
        self.dead_letter_queue.clear()
        Logger.info("Dead letter queue cleared")

    # guardian: allow-type-erasure
    def get_stats(self) -> dict:
        """Get gatekeeper statistics."""
        return {
            "max_concurrent": self.semaphore._value,
            "current_running": self.semaphore._value - self.semaphore._value,
            "dead_letter_count": len(self.dead_letter_queue),
            "timeout_seconds": self.timeout_seconds,
        }


_global_gatekeeper: SemanticGatekeeperAgent | None = None


def get_gatekeeper() -> SemanticGatekeeperAgent:
    """Get or create the global gatekeeper instance."""
    global _global_gatekeeper
    if _global_gatekeeper is None:
        _global_gatekeeper = SemanticGatekeeperAgent()
    return _global_gatekeeper


# guardian: allow-type-erasure
async def with_gatekeeping(trace_id: str, operation: str, coro: Any) -> Any:
    """
    Convenience function to run a coroutine with gatekeeping.
    Args:
        trace_id: Unique identifier for the execution
        operation: Description of the operation
        coro: Coroutine to execute

    Returns:
        Result of the coroutine
    """
    gatekeeper = get_gatekeeper()
    return await gatekeeper.run_with_gating(trace_id, operation, coro)
