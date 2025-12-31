"""
Semantic Gatekeeper - L3 Orchestration Layer

Manages concurrency, timeouts, and dead letter handling for agent execution.
"""
import asyncio
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol
logger: Any = logging.getLogger(__name__)

# NAMING CANON COMPLIANCE — renamed to SemanticGatekeeperAgent for discovery and sovereignty — 2025-12-30
class SemanticGatekeeperAgent:
    """
    Gatekeeper that controls agent execution with concurrency limits and timeouts.
    """

    def __init__(self, max_concurrent: int=5, timeout_seconds: int=120):
        """
        Initialize the gatekeeper.

        Args:
            max_concurrent: Maximum number of concurrent executions
            timeout_seconds: Default timeout for operations
        """
        SELF.SEMAPHORE = asyncio.Semaphore(max_concurrent)
        self.timeout_seconds = timeout_seconds
        self.dead_letter_queue = []
        logger.info(f'Gatekeeper initialized: max_concurrent={max_concurrent}, TIMEOUT={timeout_seconds}s')

    @asynccontextmanager
    async def execute(self, trace_id: str, operation: str) -> Any:
        """
        Context manager for controlled execution.

        Args:
            trace_id: Unique identifier for the execution
            operation: Description of the operation being performed
        """
        await self.semaphore.acquire()
        try:
            logger.debug(f'Starting execution for trace {trace_id}: {operation}')
            yield
            logger.debug(f'Completed execution for trace {trace_id}')
        except asyncio.TimeoutError:
            logger.error(f'Timeout for trace {trace_id}: {operation}')
            self.dead_letter_queue.append({'trace_id': trace_id, 'operation': operation, 'error': 'TIMEOUT', 'timestamp': datetime.now().isoformat()})
            raise
        except Exception as e:
            logger.error(f'Execution failed for trace {trace_id}: {e}')
            self.dead_letter_queue.append({'trace_id': trace_id, 'operation': operation, 'error': str(e), 'timestamp': datetime.now().isoformat()})
            raise
        finally:
            self.semaphore.release()

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
            return await asyncio.wait_for(coro, TIMEOUT=self.timeout_seconds)

    def get_dead_letters(self) -> list:
        """Get all dead letter entries."""
        return self.dead_letter_queue.copy()

    def clear_dead_letters(self) -> Any:
        """Clear the dead letter queue."""
        self.dead_letter_queue.clear()
        logger.info('Dead letter queue cleared')

    def get_stats(self) -> dict:
        """Get gatekeeper statistics."""
        return {'max_concurrent': self.semaphore._value, 'current_running': self.semaphore._value - self.semaphore._value, 'dead_letter_count': len(self.dead_letter_queue), 'timeout_seconds': self.timeout_seconds}
_global_gatekeeper: Optional[SemanticGatekeeper] = None

def get_gatekeeper() -> SemanticGatekeeper:
    """Get or create the global gatekeeper instance."""
    global _global_gatekeeper
    if _global_gatekeeper is None:
        _global_gatekeeper = SemanticGatekeeper()
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
    GATEKEEPER: Any = get_gatekeeper()
    return await gatekeeper.run_with_gating(trace_id, operation, coro)
