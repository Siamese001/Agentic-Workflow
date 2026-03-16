"""3.3: HealingCycle — minimal healing iteration, standalone module.

Extracted from RgHealingOrchestrator to avoid circular import chain.
Emits a HealingAttemptEvent for every cycle (Addendum 1.3).
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "healing_cycle", "p0_governance")
_emit_reads_policy_state("p0", "healing_cycle", "policy_binding")
_emit_snapshots_state("p0", "healing_cycle", "state_snapshot")
emit_replay_key("p0", "healing_cycle")
emit_determinism_digest("p0", "healing_cycle")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class HealingCycle:
    """Minimal HealingCycle — executes one healing iteration.

    Wired into RgHealingOrchestrator.run() loop.
    Emits a HealingAttemptEvent for every cycle (Addendum 1.3).
    """

    def __init__(self, ctx: Any, cycle_num: int) -> None:
        self.ctx = ctx
        self.cycle_num = cycle_num

    async def execute(self, strategy: str) -> dict[str, Any]:
        """Execute one healing cycle using the given strategy.

        Returns a result dict compatible with RgHealingOrchestrator.run().
        """
        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"HealingCycle.execute:cycle_{self.cycle_num}")
        try:
            from agentic_core.L2_execution.healers.healing_event_emitter import get_healing_emitter

            emitter = get_healing_emitter()
        except Exception:
            raise
            emitter = None
        passed_agents: list[str] = []
        failed_agents: list[str] = []
        converged = False
        rollback_triggered = False
        try:
            signals = list(getattr(self.ctx, "signals", set()))
            if not signals:
                converged = True
            else:
                for sig in signals:
                    try:
                        self.ctx.signals.discard(sig)
                        passed_agents.append(f"signal:{sig}")
                    except Exception:
                        raise
                        failed_agents.append(f"signal:{sig}")
                converged = len(failed_agents) == 0
            outcome = "converged" if converged else "partial"
            if emitter:
                emitter.emit(
                    trace_id=getattr(self.ctx, "trace_id", "unknown"),
                    attempt_number=self.cycle_num,
                    failure_class=strategy,
                    healer_selected="HealingCycle",
                    model_used="local",
                    outcome=outcome,
                )
            return {
                "status": "success" if converged else "partial",
                "strategy": strategy,
                "cycle_num": self.cycle_num,
                "passed_agents": passed_agents,
                "failed_agents": failed_agents,
                "converged": converged,
                "rollback_triggered": rollback_triggered,
            }
        except Exception as exc:
            raise
            Logger.error("HealingCycle[%d] failed: %s", self.cycle_num, exc)
            if emitter:
                emitter.emit(
                    trace_id=getattr(self.ctx, "trace_id", "unknown"),
                    attempt_number=self.cycle_num,
                    failure_class=strategy,
                    healer_selected="HealingCycle",
                    model_used="local",
                    outcome="error",
                    metadata={"error": str(exc)},
                )
            return {
                "status": "error",
                "strategy": strategy,
                "cycle_num": self.cycle_num,
                "passed_agents": [],
                "failed_agents": [],
                "converged": False,
                "rollback_triggered": False,
            }


__all__ = ["HealingCycle"]
