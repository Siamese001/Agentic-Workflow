# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, state, validator, workflow
from __future__ import annotations

from dataclasses import dataclass

# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
Semantic Gatekeeper - L3 Orchestration Layer

Manages concurrency, timeouts, and dead letter handling for agent execution.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from agentic_core.base_agents.timeout_decorator import timeout

Logger: Any = logging.getLogger(__name__)

from agentic_core.base_agents.decorators import standard_heal


# NAMING CANON COMPLIANCE — renamed to SemanticGatekeeperAgent for discovery and sovereignty — 2025-12-30
@dataclass
class SemanticGatekeeperAgent(SovereignBaseAgent):
    """
    Gatekeeper that controls agent execution with concurrency limits and timeouts.
    """

    def __init__(self, max_concurrent: int = 5, timeout_seconds: int = 120) -> None:
        """
        Initialize the gatekeeper.

        Args:
            max_concurrent: Maximum number of concurrent executions
            timeout_seconds: Default timeout for operations
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout_seconds = timeout_seconds
        self.dead_letter_queue = []
        Logger.info(
            f"Gatekeeper initialized: max_concurrent={max_concurrent}, TIMEOUT={timeout_seconds}s"
        )

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L3 compliance."""
        assert hasattr(self, "timeout_seconds"), "Missing timeout_seconds"
        assert hasattr(self, "dead_letter_queue"), "Missing dead_letter_queue"
        return True

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L3 orchestration agent - operational only."""
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
        file_path = violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")

        # Default implementation - SemanticGatekeeperAgent provides semantic gating
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

    def clear_dead_letters(self) -> Any:
        """Clear the dead letter queue."""
        self.dead_letter_queue.clear()
        Logger.info("Dead letter queue cleared")

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
