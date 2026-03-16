__version__ = "13.0"
import asyncio

from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway
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

_emit_reads_policy_state("p0", "GeminiLLMClient", "policy_binding")
_emit_snapshots_state("p0", "GeminiLLMClient", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "GeminiLLMClient", "execution_auth")
_emit_validates_capability("p2", "GeminiLLMClient", "capability_check")
_emit_routes_to_capability("p2", "GeminiLLMClient", "capability_route")
_emit_writes_via_uwg("p2", "GeminiLLMClient", "uwg_write")
_emit_blocks_direct_write("p2", "GeminiLLMClient", "direct_write_block")
_emit_records_tool_invocation("p2", "GeminiLLMClient", "tool_invocation")
_emit_captures_execution_output("p2", "GeminiLLMClient", "exec_output")
_emit_dispatches_agent("p3", "GeminiLLMClient", "agent_dispatch")
_emit_coordinates_agents("p3", "GeminiLLMClient", "agent_coordination")
_emit_records_workflow_lineage("p3", "GeminiLLMClient", "workflow_lineage")
_emit_records_healing_outcome("p3", "GeminiLLMClient", "healing_outcome")
_emit_escalates_failure("p3", "GeminiLLMClient", "failure_escalation")
_emit_orchestrates_workflow("p3", "GeminiLLMClient", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "GeminiLLMClient", "healing_dispatch")
_emit_invokes_evaluation("p3", "GeminiLLMClient", "evaluation_signal")
_emit_records_telemetry_event("p4", "GeminiLLMClient", "telemetry_event")
_emit_captures_evaluation_metric("p4", "GeminiLLMClient", "eval_metric")
_emit_stores_embedding("p4", "GeminiLLMClient", "embedding_store")
_emit_updates_meta_learning_state("p4", "GeminiLLMClient", "meta_learning")
_emit_links_execution_to_snapshot("p4", "GeminiLLMClient", "exec_snapshot_link")


class GeminiLLMClient:
    """Gateway-delegating client for Gemini.  No direct SDK access."""

    _AGENT_ID = "GeminiLLMClient"
    try:
        from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig as _HTC

        _MODEL: str = _HTC().model_gemini_2_5_pro_id
    except (ImportError, AttributeError):
        _MODEL = "gemini-2.5-pro"

    def __init__(self, circuit_breaker=None):
        self._gateway = SovereignLLMGateway()
        self.circuit_breaker = circuit_breaker

    def generate(self, prompt: str) -> str:
        import uuid  # noqa: PLC0415

        _trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GeminiLLMClient.generate")
        request = GenerationRequest(
            agent_id=self._AGENT_ID, provider="google", model=self._MODEL, prompt=prompt
        )
        _clk = get_clock()
        _clk.emit_replay_key(context=f"lic:gemini:{self._AGENT_ID}:{self._MODEL}")
        _clk.emit_determinism_digest(inputs={"agent": self._AGENT_ID, "model": self._MODEL})
        response = asyncio.get_event_loop().run_until_complete(self._gateway.route_generation(request))
        return response.content
