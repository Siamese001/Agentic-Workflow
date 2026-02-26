"""Outcome Write-Back Hook Port — seam for real-time meta-learning feedback.

Called by dispatch_healing() immediately after an invocation completes.
Implementations write to HealingSuccessRateStore and call
update_qwen_confidence_prior() (for QWEN tier).

Contracts:
- MUST be synchronous and fast (no network I/O in hot path).
- MUST emit structured telemetry on failure (never fully silent).
- MUST NOT modify HEALING_CONFIDENCE_X or HEALING_CONFIDENCE_Y.
- MUST NOT mutate healing_input or decision.
- MUST always execute (no retry-count short-circuit).
  Forced escalation applies to routing only, not write-back.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord
    from agentic_core.L2_execution.healers.healing_tier_types import (
        HealingDecision,
        HealingInput,
    )

logger = logging.getLogger(__name__)


class OutcomeWriteBackHook(Protocol):
    """Synchronous write-back seam called after each heal invocation."""

    def on_outcome(
        self,
        *,
        healing_input: HealingInput,
        decision: HealingDecision,
        record: InvocationRecord | None,
        success: bool,
    ) -> None:
        """Handle a completed healing outcome.

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


class NullOutcomeWriteBackHook:
    """No-op hook (default when no store is configured)."""

    def on_outcome(self, **kwargs) -> None:
        pass


class DefaultOutcomeWriteBackHook:
    """Default hook: writes to HealingSuccessRateStore + Qwen prior update.

    Never silently swallows exceptions — always emits structured telemetry.
    Always executes regardless of retry_count (forced escalation is routing-only).
    """

    def __init__(self, store=None) -> None:
        if store is None:
            from system_learning.engines.healing_success_rate_store import get_default_store

            store = get_default_store()
        self._store = store

    def on_outcome(
        self,
        *,
        healing_input,
        decision,
        record,
        success: bool,
    ) -> None:
        # Always record outcome (no retry-count short-circuit)
        try:
            self._store.record_outcome(healing_input.error_signature, success)
        except Exception as exc:  # guardian: allow-silent-swallower
            logger.warning(
                "write_back_store_failed",
                extra={
                    "error_signature": healing_input.error_signature,
                    "exception": str(exc),
                    "trace_id": healing_input.trace_id,
                },
            )

        # Qwen-specific prior update (per qwen_meta_learning contract)
        from agentic_core.L2_execution.healers.healing_tier_types import HealingTier

        if decision.tier == HealingTier.QWEN_VLLM:
            try:
                from agentic_core.L2_execution.healers.qwen_meta_learning import (
                    update_qwen_confidence_prior,
                )

                update_qwen_confidence_prior(healing_input.error_signature, success)
            except Exception as exc:  # guardian: allow-silent-swallower
                logger.warning(
                    "write_back_qwen_prior_failed",
                    extra={
                        "error_signature": healing_input.error_signature,
                        "exception": str(exc),
                        "trace_id": healing_input.trace_id,
                    },
                )


__all__ = [
    "OutcomeWriteBackHook",
    "NullOutcomeWriteBackHook",
    "DefaultOutcomeWriteBackHook",
]
