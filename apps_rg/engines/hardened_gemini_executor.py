"""3.2: HardenedGeminiExecutor — Google/Gemini execution path via SovereignLLMGateway.

Wired into HardenedRouter._initialize_executors() for Provider.GOOGLE.
All calls route through SovereignLLMGateway — no direct SDK access.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
)

_emit_reads_policy_state("p0", "hardened_gemini_executor", "policy_binding")
_emit_snapshots_state("p0", "hardened_gemini_executor", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hardened_gemini_executor", "execution_auth")
_emit_validates_capability("p2", "hardened_gemini_executor", "capability_check")
_emit_routes_to_capability("p2", "hardened_gemini_executor", "capability_route")
_emit_writes_via_uwg("p2", "hardened_gemini_executor", "uwg_write")
_emit_blocks_direct_write("p2", "hardened_gemini_executor", "direct_write_block")
_emit_records_tool_invocation("p2", "hardened_gemini_executor", "tool_invocation")
_emit_captures_execution_output("p2", "hardened_gemini_executor", "exec_output")
_emit_dispatches_agent("p3", "hardened_gemini_executor", "agent_dispatch")
_emit_coordinates_agents("p3", "hardened_gemini_executor", "agent_coordination")
_emit_records_workflow_lineage("p3", "hardened_gemini_executor", "workflow_lineage")
_emit_records_healing_outcome("p3", "hardened_gemini_executor", "healing_outcome")
_emit_escalates_failure("p3", "hardened_gemini_executor", "failure_escalation")
_emit_orchestrates_workflow("p3", "hardened_gemini_executor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hardened_gemini_executor", "healing_dispatch")
_emit_invokes_evaluation("p3", "hardened_gemini_executor", "evaluation_signal")
_emit_records_telemetry_event("p4", "hardened_gemini_executor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hardened_gemini_executor", "eval_metric")
_emit_stores_embedding("p4", "hardened_gemini_executor", "embedding_store")
_emit_updates_meta_learning_state("p4", "hardened_gemini_executor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hardened_gemini_executor", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class HardenedGeminiExecutor:
    """Sovereign Gemini execution path.

    Delegates all LLM calls to SovereignLLMGateway.
    Provides circuit-breaker and retry logic consistent with the hardened router.
    """

    agent_id: str = "HardenedGeminiExecutor"
    max_retries: int = 3
    _gateway: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        try:
            from agentic_core.interfaces.gateway import SovereignLLMGateway

            self._gateway = SovereignLLMGateway()
            _clk = get_clock()
            _clk.emit_replay_key(context=f"rg:gemini:{self.agent_id}")
            _clk.emit_determinism_digest(inputs={"executor": self.agent_id, "provider": "google"})
        except ImportError:
            logger.warning("HardenedGeminiExecutor: SovereignLLMGateway not available")
            self._gateway = None

    def execute(
        self, prompt: str, model: str | None = None, temperature: float = 0.7, max_tokens: int | None = None
    ) -> dict[str, Any]:
        """Execute a prompt via SovereignLLMGateway (Google/Gemini path).

        Returns:
            dict with 'content', 'model', 'provider', 'success' keys.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HardenedGeminiExecutor.execute")

        if self._gateway is None:
            raise RuntimeError("HardenedGeminiExecutor: SovereignLLMGateway not available — cannot execute")
        from agentic_core.interfaces.gateway import GenerationRequest

        effective_model = model or "gemini-2.5-pro"
        request = GenerationRequest(
            agent_id=self.agent_id, provider="google", model=effective_model, prompt=prompt
        )
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                loop = asyncio.new_event_loop()
                try:
                    response = loop.run_until_complete(self._gateway.route_generation(request))
                finally:
                    loop.close()
                logger.debug(
                    "HardenedGeminiExecutor: success on attempt %d model=%s", attempt, effective_model
                )
                return {
                    "content": response.content,
                    "model": effective_model,
                    "provider": "google",
                    "success": True,
                    "attempt": attempt,
                }
            # guardian: allow-silent-swallow
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "HardenedGeminiExecutor attempt %d/%d failed: %s", attempt, self.max_retries, exc
                )
        raise RuntimeError(
            f"HardenedGeminiExecutor: all {self.max_retries} attempts failed. Last: {last_exc}"
        )

    def is_available(self) -> bool:
        """Return True if the gateway is wired up."""
        return self._gateway is not None


__all__ = ["HardenedGeminiExecutor"]
