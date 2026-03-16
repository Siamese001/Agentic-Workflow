from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "autonomy_mixin", "p0_governance")
_emit_reads_policy_state("p0", "autonomy_mixin", "policy_binding")
_emit_snapshots_state("p0", "autonomy_mixin", "state_snapshot")
emit_replay_key("p0", "autonomy_mixin")
emit_determinism_digest("p0", "autonomy_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

"\nAutonomyMixin – Sovereign Agent Role Mixin (Phase 28 – Dec 30, 2025)\nEnables proactive, unprompted execution with constitutional safeguards.\n"
import logging
import time
from typing import Any

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin  # noqa: F401
except ImportError:

    class MCPHardenedMixin:
        """Fallback stub for MCPHardenedMixin."""

        pass
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class AutonomyMixin(SovereignBaseAgent):
    _autonomy_enabled: bool = True
    _proactive_interval: float = 300.0
    _last_proactive_check: float = 0.0
    _max_proactive_actions_per_hour: int = 12
    _proactive_action_count_this_hour: int = 0
    _hour_boundary: float = time.time()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Logger = logging.getLogger(f"{self.__class__.__name__}.Autonomy")

    async def should_act_proactively(self) -> bool:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AutonomyMixin.should_act_proactively")

        if not self._autonomy_enabled:
            return False
        now = time.time()
        if now - self._hour_boundary >= 3600:
            self._proactive_action_count_this_hour = 0
            self._hour_boundary = now
        if self._proactive_action_count_this_hour >= self._max_proactive_actions_per_hour:
            return False
        if now - self._last_proactive_check < self._proactive_interval:
            return False
        self._last_proactive_check = now
        if not await self._system_healthy_for_proactivity():
            return False
        opportunity = await self._detect_action_opportunity()
        if opportunity:
            self._proactive_action_count_this_hour += 1
            return True
        return False

    async def _system_healthy_for_proactivity(self) -> bool:
        return True

    async def _detect_action_opportunity(self) -> dict[str, Any] | None:
        raise NotImplementedError(f"{self.__class__.__name__} must implement _detect_action_opportunity")

    async def proactive_execute(self) -> dict[str, Any]:
        if not await self.should_act_proactively():
            return {"proactive": False, "skipped": True}
        opportunity = await self._detect_action_opportunity()
        try:
            result = await self.execute(proactive=True, opportunity_context=opportunity)
            return {"proactive": True, "success": True, "result": result}
        except Exception as e:
            return {"proactive": True, "success": False, "error": str(e)}
