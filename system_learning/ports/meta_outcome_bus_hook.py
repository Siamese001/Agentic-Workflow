"""Meta Outcome Bus Hook Port — enqueues healing outcomes onto MetaLearningBus.

Called by dispatch_healing() after invocation completes.
Creates MetaLearningChangePackage with proposal_only=True and enqueues
on the injected MetaLearningBus.

Contracts:
- MUST be synchronous and fast (no network I/O in hot path).
- MUST enforce proposal_only=True in all packages.
- MUST NOT modify routing thresholds or tiers.
- MUST NOT fail dispatch if bus enqueue fails (log and continue).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from agentic_core.L0_routing.meta_control.meta_learning_bus import MetaLearningBus
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
    from agentic_core.L2_execution.healers.healing_tier_types import HealingDecision, HealingInput
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class MetaOutcomeBusHook(Protocol):
    """Synchronous seam for publishing healing outcomes to MetaLearningBus."""

    def publish_outcome(
        self,
        *,
        healing_input: HealingInput,
        decision: HealingDecision,
        record: InvocationRecord | None,
        success: bool,
    ) -> None:
        """Publish a healing outcome as a MetaLearningChangePackage.

        Parameters
        ----------
        healing_input : HealingInput
            The original structured failure context.
        decision : HealingDecision
            The routing decision that was executed.
        record : InvocationRecord | None
            The invocation trace record (None if exception before record).
        success : bool
            Whether the heal attempt succeeded.
        """
        ...


class NullMetaOutcomeBusHook:
    """No-op hook (default when no bus is configured)."""

    def publish_outcome(self, **kwargs) -> None:
        pass


class DefaultMetaOutcomeBusHook:
    """Default hook: enqueues outcomes on injected MetaLearningBus.

    Always sets proposal_only=True and never fails the dispatch path.
    """

    def __init__(self, bus: MetaLearningBus | None = None) -> None:
        self._bus = bus

    def publish_outcome(self, *, healing_input, decision, record, success: bool) -> None:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DefaultMetaOutcomeBusHook.publish_outcome")

        if self._bus is None:
            return
        try:
            from agentic_core.L0_routing.meta_control.meta_learning_bus import MetaLearningChangePackage

            package = MetaLearningChangePackage.create(
                trace_id=healing_input.trace_id,
                kind="healing_outcome",
                payload={
                    "error_signature": healing_input.error_signature,
                    "tier": decision.tier.value,
                    "heal_confidence": decision.heal_confidence,
                    "success": success,
                    "trace_id": healing_input.trace_id,
                    "retry_count": healing_input.retry_count,
                    "reason_codes": list(decision.reason_codes),
                    "proposal_only": True,
                },
            )
            self._bus.enqueue(package)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.warning(
                "meta_outcome_bus_enqueue_failed",
                extra={
                    "error_signature": healing_input.error_signature,
                    "exception": str(exc),
                    "trace_id": healing_input.trace_id,
                },
            )


__all__ = ["MetaOutcomeBusHook", "NullMetaOutcomeBusHook", "DefaultMetaOutcomeBusHook"]
