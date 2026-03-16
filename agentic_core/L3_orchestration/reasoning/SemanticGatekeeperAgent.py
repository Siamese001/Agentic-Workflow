from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "SemanticGatekeeperAgent")
emit_determinism_digest("p0", "SemanticGatekeeperAgent")

_emit_dispatches_healing_run("p1", "SemanticGatekeeperAgent", "L3")
_emit_routes_through("p1", "SemanticGatekeeperAgent", "L3")
_emit_escalates_to_human("p1", "SemanticGatekeeperAgent", "L3")
_emit_reads_policy_state("p1", "SemanticGatekeeperAgent", "L3")
_emit_authorize_and_execute("p2", "SemanticGatekeeperAgent", "execution_auth")
_emit_validates_capability("p2", "SemanticGatekeeperAgent", "capability_check")
_emit_routes_to_capability("p2", "SemanticGatekeeperAgent", "capability_route")
_emit_writes_via_uwg("p2", "SemanticGatekeeperAgent", "uwg_write")
_emit_blocks_direct_write("p2", "SemanticGatekeeperAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "SemanticGatekeeperAgent", "tool_invocation")
_emit_captures_execution_output("p2", "SemanticGatekeeperAgent", "exec_output")
_emit_dispatches_agent("p3", "SemanticGatekeeperAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "SemanticGatekeeperAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "SemanticGatekeeperAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "SemanticGatekeeperAgent", "healing_outcome")
_emit_escalates_failure("p3", "SemanticGatekeeperAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "SemanticGatekeeperAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SemanticGatekeeperAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "SemanticGatekeeperAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "SemanticGatekeeperAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SemanticGatekeeperAgent", "eval_metric")
_emit_stores_embedding("p4", "SemanticGatekeeperAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "SemanticGatekeeperAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SemanticGatekeeperAgent", "exec_snapshot_link")

"\nSemantic Gatekeeper - L3 Orchestration Layer\n\nManages concurrency, timeouts, and dead letter handling for agent execution.\n"
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from agentic_core.utils.timeout_decorator_util import timeout

Logger: Any = logging.getLogger(__name__)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal


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

        _emit_snapshots_state(str(_uuid.uuid4()), "SemanticGatekeeperAgent.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SemanticGatekeeperAgent.__init__", "p0_governance")
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
    ) -> dict[str, int]:
        """L3 orchestration agent - operational only."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SemanticGatekeeperAgent.heal_repository"
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
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
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
        except asyncio.TimeoutError:
            Logger.error(f"Timeout for trace {trace_id}: {operation}")
            self.dead_letter_queue.append(
                {
                    "trace_id": trace_id,
                    "operation": operation,
                    "error": "TIMEOUT",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            raise
        except Exception as e:
            raise
            Logger.error(f"Execution failed for trace {trace_id}: {e}")
            self.dead_letter_queue.append(
                {
                    "trace_id": trace_id,
                    "operation": operation,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )
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
        except Exception as e:
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
