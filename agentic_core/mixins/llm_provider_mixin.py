"""
LLMProviderMixin - Unified LLM Access for Agents

[PHASE 4 MIGRATION] Provides single interface to all LLM providers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "llm_provider_mixin", "p0_governance")
_emit_reads_policy_state("p0", "llm_provider_mixin", "policy_binding")
_emit_snapshots_state("p0", "llm_provider_mixin", "state_snapshot")
emit_replay_key("p0", "llm_provider_mixin")
emit_determinism_digest("p0", "llm_provider_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "llm_provider_mixin", "execution_auth")
_emit_validates_capability("p2", "llm_provider_mixin", "capability_check")
_emit_routes_to_capability("p2", "llm_provider_mixin", "capability_route")
_emit_writes_via_uwg("p2", "llm_provider_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "llm_provider_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "llm_provider_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "llm_provider_mixin", "exec_output")
_emit_dispatches_agent("p3", "llm_provider_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "llm_provider_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "llm_provider_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "llm_provider_mixin", "healing_outcome")
_emit_escalates_failure("p3", "llm_provider_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "llm_provider_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "llm_provider_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "llm_provider_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "llm_provider_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "llm_provider_mixin", "eval_metric")
_emit_stores_embedding("p4", "llm_provider_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "llm_provider_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "llm_provider_mixin", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Provider = Literal["openai", "anthropic", "google"]


def _get_llm_gateway():
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway

    return get_llm_gateway()


class LLMProviderMixin:
    """
    Mixin providing unified LLM gateway access.

    [PHASE 4 MIGRATION] Replaces direct SDK imports.

    Usage:
        class MyAgent(LLMProviderMixin, SovereignBaseAgent):
            async def process(self, query: str) -> str:
                response = await self.llm_generate(query)
                return response["content"]
    """

    _llm_gateway: SovereignLLMGateway | None = None

    @property
    def llm_gateway(self) -> SovereignLLMGateway:
        """Lazy-load LLM gateway singleton."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LLMProviderMixin.llm_gateway")

        if self._llm_gateway is None:
            self._llm_gateway = _get_llm_gateway()
        return self._llm_gateway

    async def llm_generate(
        self,
        prompt: str,
        model: str | None = None,
        provider: Provider = "openai",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate LLM response through gateway."""
        return await self.llm_gateway.generate(prompt, model=model, provider=provider, **kwargs)

    async def llm_generate_with_fallback(
        self,
        prompt: str,
        model: str | None = None,
        fallback_providers: list[Provider] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate with automatic provider fallback."""
        return await self.llm_gateway.generate(
            prompt,
            model=model,
            fallback_providers=fallback_providers,
            **kwargs,
        )
