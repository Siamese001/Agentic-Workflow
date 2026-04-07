"""L3 Orchestration Context Freeze/Unfreeze — Path D HITL Support.

Provides deterministic context freezing at L3 (Circulation Desk) before
human-in-the-loop review. Ensures that:
- Context is snapshotted and immutable during human review
- Trace IDs and plan hashes are preserved
- Rollback to frozen state is possible
- Integration with HITL escalation and decision artifacts

Reference: docs/reference/HITL/HITL Implementations v2.md
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.types.human_decision_artifact_types import (
    HumanDecisionArtifact,
    create_human_review_draft,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
)

# Lifecycle trace emissions
_emit_reads_policy_state("p0", "l3_context_freeze", "policy_binding")
# P1 routing emissions
# P3 orchestration emissions
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FrozenContextSnapshot:
    """Immutable snapshot of context at freeze point.

    Attributes:
        trace_id: Unique trace identifier for this freeze
        plan_hash: SHA-256 hash of the plan at freeze time
        context_data: Arbitrary context data (must be serializable)
        freeze_timestamp: Sequence number (deterministic, not wall clock)
        original_plan_path: Optional path to original plan
    """

    trace_id: str
    plan_hash: str
    context_data: dict[str, Any]
    freeze_timestamp: int
    original_plan_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "plan_hash": self.plan_hash,
            "context_data": self.context_data,
            "freeze_timestamp": self.freeze_timestamp,
            "original_plan_path": self.original_plan_path,
        }

    def compute_context_hash(self) -> str:
        """Compute deterministic hash of context data."""
        canonical = json.dumps(self.context_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class FreezeUnfreezeContext:
    """Manages context freezing and unfreezing at L3.

    This is the concrete implementation of the "Freeze Context" step
    in the Path D HITL flow. It:
    - Freezes context before human review (Desk 2)
    - Maintains immutability during review
    - Unfreezes and restores context after decision
    - Creates HITL artifacts for the flow

    Attributes:
        frozen_snapshots: List of all frozen snapshots
        current_snapshot: Active snapshot (None if not frozen)
        freeze_sequence: Incrementing sequence number for determinism
    """

    frozen_snapshots: list[FrozenContextSnapshot] = field(default_factory=list)
    current_snapshot: FrozenContextSnapshot | None = None
    freeze_sequence: int = 0

    def freeze(
        self,
        trace_id: str,
        plan_content: dict[str, Any],
        context_data: dict[str, Any] | None = None,
        original_plan_path: str | None = None,
    ) -> FrozenContextSnapshot:
        """Freeze context for human-in-the-loop review.

        Args:
            trace_id: Unique trace identifier
            plan_content: Plan content to freeze (will be hashed)
            context_data: Additional context to freeze
            original_plan_path: Optional path to original plan

        Returns:
            FrozenContextSnapshot representing the frozen state
        """
        import uuid as _uuid

        _emit_trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _emit_trace_id, LayerSegment.L3_ORCHESTRATION, "FreezeUnfreezeContext.freeze",
        )

        # Compute plan hash deterministically
        canonical_plan = json.dumps(plan_content, sort_keys=True, separators=(",", ":"))
        plan_hash = hashlib.sha256(canonical_plan.encode()).hexdigest()

        # Increment sequence
        self.freeze_sequence += 1

        # Create snapshot
        snapshot = FrozenContextSnapshot(
            trace_id=trace_id,
            plan_hash=plan_hash,
            context_data=context_data or {},
            freeze_timestamp=self.freeze_sequence,
            original_plan_path=original_plan_path,
        )

        self.frozen_snapshots.append(snapshot)
        self.current_snapshot = snapshot

        logger.info(
            "L3 context frozen: trace=%s plan_hash=%s... sequence=%d",
            trace_id,
            plan_hash[:16],
            self.freeze_sequence,
        )

        return snapshot

    def unfreeze(
        self,
        restore_context: bool = True,
    ) -> FrozenContextSnapshot | None:
        """Unfreeze context after human review.

        Args:
            restore_context: If True, restores context from snapshot

        Returns:
            The snapshot that was unfrozen, or None if no active freeze
        """
        import uuid as _uuid

        _emit_trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _emit_trace_id, LayerSegment.L3_ORCHESTRATION, "FreezeUnfreezeContext.unfreeze",
        )

        if self.current_snapshot is None:
            logger.warning("Unfreeze called with no active frozen context")
            return None

        snapshot = self.current_snapshot
        self.current_snapshot = None

        if restore_context:
            logger.info(
                "L3 context unfrozen: trace=%s restored=%s",
                snapshot.trace_id,
                restore_context,
            )

        return snapshot

    def create_hitl_artifact(
        self,
        policy_hash: str,
        allowed_tools: tuple[str, ...] = (),
    ) -> HumanDecisionArtifact:
        """Create HITL artifact from frozen context.

        This creates the artifact that flows to Desk 2 (Secure Reading Room).

        Args:
            policy_hash: Policy validation hash
            allowed_tools: Allowed tools for MODIFY_DIFF actions

        Returns:
            HumanDecisionArtifact ready for human review

        Raises:
            RuntimeError: If no context is currently frozen
        """
        if self.current_snapshot is None:
            raise RuntimeError("Cannot create HITL artifact: no frozen context")

        artifact = create_human_review_draft(
            trace_id=self.current_snapshot.trace_id,
            policy_hash=policy_hash,
            plan_hash=self.current_snapshot.plan_hash,
            governed_payload=self.current_snapshot.context_data.get("governed_payload"),
            allowed_tools=allowed_tools,
            plan_content=self.current_snapshot.context_data.get("plan_content"),
        )

        logger.info(
            "HITL artifact created from frozen context: trace=%s plan_hash=%s...",
            artifact.trace_id,
            artifact.original_plan_hash[:16],
        )

        return artifact

    def is_frozen(self) -> bool:
        """Check if context is currently frozen."""
        return self.current_snapshot is not None

    def get_active_trace_id(self) -> str | None:
        """Get trace ID of active frozen context."""
        return self.current_snapshot.trace_id if self.current_snapshot else None

    def get_active_plan_hash(self) -> str | None:
        """Get plan hash of active frozen context."""
        return self.current_snapshot.plan_hash if self.current_snapshot else None

    def validate_plan_hash(self, submitted_hash: str) -> bool:
        """Validate that submitted plan hash matches frozen context.

        Args:
            submitted_hash: Hash submitted for validation

        Returns:
            True if hash matches frozen context
        """
        if self.current_snapshot is None:
            return False

        return self.current_snapshot.plan_hash == submitted_hash

    def rollback_to_snapshot(
        self,
        snapshot: FrozenContextSnapshot | None = None,
    ) -> dict[str, Any]:
        """Rollback to a specific snapshot.

        Args:
            snapshot: Snapshot to rollback to (default: most recent)

        Returns:
            Context data from the snapshot
        """
        target = snapshot or (self.frozen_snapshots[-1] if self.frozen_snapshots else None)

        if target is None:
            raise RuntimeError("No snapshots available for rollback")

        self.current_snapshot = target

        logger.info("Rolled back to snapshot: trace=%s", target.trace_id)

        return target.context_data

    def get_snapshot_history(self, limit: int | None = None) -> list[FrozenContextSnapshot]:
        """Get history of frozen snapshots.

        Args:
            limit: Maximum snapshots to return (most recent first)

        Returns:
            List of frozen snapshots
        """
        history = list(self.frozen_snapshots)
        if limit:
            history = history[-limit:]
        return list(reversed(history))


# Global context manager for singleton access
_global_freeze_context: FreezeUnfreezeContext | None = None


def get_l3_freeze_context() -> FreezeUnfreezeContext:
    """Get the global L3 freeze/unfreeze context manager."""
    global _global_freeze_context
    if _global_freeze_context is None:
        _global_freeze_context = FreezeUnfreezeContext()
    return _global_freeze_context


def reset_l3_freeze_context() -> None:
    """Reset the global L3 freeze context (for testing)."""
    global _global_freeze_context
    _global_freeze_context = None


def freeze_for_hitl(
    trace_id: str,
    plan_content: dict[str, Any],
    context_data: dict[str, Any] | None = None,
    policy_hash: str = "",
) -> tuple[FrozenContextSnapshot, HumanDecisionArtifact]:
    """Convenience function to freeze context and create HITL artifact.

    Args:
        trace_id: Unique trace identifier
        plan_content: Plan content to freeze
        context_data: Additional context
        policy_hash: Policy validation hash

    Returns:
        Tuple of (frozen snapshot, HITL artifact)
    """
    ctx = get_l3_freeze_context()

    # Freeze context
    snapshot = ctx.freeze(
        trace_id=trace_id,
        plan_content=plan_content,
        context_data=context_data,
    )

    # Create HITL artifact
    allowed_tools = context_data.get("allowed_tools", ()) if context_data else ()
    artifact = ctx.create_hitl_artifact(
        policy_hash=policy_hash,
        allowed_tools=allowed_tools,
    )

    return snapshot, artifact


def unfreeze_after_hitl(
    restore_context: bool = True,
) -> FrozenContextSnapshot | None:
    """Convenience function to unfreeze context after HITL decision.

    Args:
        restore_context: If True, restores context from snapshot

    Returns:
        The snapshot that was unfrozen, or None if no active freeze
    """
    ctx = get_l3_freeze_context()
    return ctx.unfreeze(restore_context=restore_context)


__all__ = [
    "FreezeUnfreezeContext",
    "FrozenContextSnapshot",
    "freeze_for_hitl",
    "get_l3_freeze_context",
    "reset_l3_freeze_context",
    "unfreeze_after_hitl",
]
