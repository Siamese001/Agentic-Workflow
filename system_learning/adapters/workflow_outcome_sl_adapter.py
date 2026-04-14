"""Workflow Outcome System Learning Adapter.

Bridges WorkflowLearningBridge outcomes to SystemLearningMemoryBridge.
Captures workflow execution patterns for meta-learning analysis.
"""

import logging
from typing import Any


# Lazy import to avoid L_SL->L3 gravity violation
def _get_workflow_outcome():
    from agentic_core.L3_orchestration.reasoning.learning.workflow_learning_bridge import WorkflowOutcome

    return WorkflowOutcome


logger = logging.getLogger(__name__)


class WorkflowOutcomeSLAdapter:
    """Adapter that persists workflow outcomes to system learning memory.

    Transforms WorkflowOutcome objects into telemetry events for pattern analysis.
    """

    def __init__(self) -> None:
        self._accepted_count = 0
        self._error_count = 0

    def accept(self, outcome: "WorkflowOutcome") -> None:
        """Accept and persist a workflow outcome.

        Args:
            outcome: The workflow outcome to persist
        """
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

            bridge = get_sl_memory_bridge()

            # Persist as telemetry event
            success = bridge.persist_workflow_outcome(
                bundle_id=outcome.bundle_id,
                trace_id=outcome.trace_id,
                workflow_type=outcome.workflow_type,
                success=outcome.success,
                elapsed_ms=outcome.elapsed_ms,
                agent_sequence=list(outcome.agent_sequence),
                quality_score=outcome.quality_score,
                outcome_hash=outcome.outcome_hash,
                timestamp_utc=int(outcome.metadata.get("timestamp_utc", 0) * 1000)
                if outcome.metadata.get("timestamp_utc")
                else 0,
            )

            if success:
                self._accepted_count += 1
            else:
                logger.debug("Failed to persist workflow outcome: %s", outcome.bundle_id)
                self._error_count += 1

        except (AttributeError, ImportError, RuntimeError, TypeError, ValueError) as exc:
            logger.error("WorkflowOutcomeSLAdapter failed to accept outcome: %s", exc)
            self._error_count += 1

    def get_stats(self) -> dict[str, Any]:
        """Get adapter statistics."""
        return {
            "accepted_count": self._accepted_count,
            "error_count": self._error_count,
            "total_processed": self._accepted_count + self._error_count,
        }


# Global adapter instance
_global_adapter: WorkflowOutcomeSLAdapter | None = None


def get_workflow_outcome_sl_adapter() -> WorkflowOutcomeSLAdapter:
    """Get the global workflow outcome SL adapter instance."""
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = WorkflowOutcomeSLAdapter()
    return _global_adapter


def register_with_workflow_bridge() -> None:
    """Register the SL adapter with the WorkflowLearningBridge."""
    try:
        from agentic_core.L3_orchestration.reasoning.learning.workflow_learning_bridge import (
            get_workflow_learning_bridge,
        )

        bridge = get_workflow_learning_bridge()
        adapter = get_workflow_outcome_sl_adapter()

        bridge.register_learner("system_learning", adapter.accept)
        logger.info("WorkflowOutcomeSLAdapter registered with WorkflowLearningBridge")
    except (AttributeError, ImportError, RuntimeError, TypeError, ValueError) as exc:
        logger.error("Failed to register WorkflowOutcomeSLAdapter: %s", exc)


__all__ = [
    "WorkflowOutcomeSLAdapter",
    "get_workflow_outcome_sl_adapter",
    "register_with_workflow_bridge",
]
