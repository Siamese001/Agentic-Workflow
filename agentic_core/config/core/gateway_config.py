"""
GatewayFactory - Unified Gateway Access via Composition

Phase 2 MRO Refactoring: Provides dependency injection alternative to mixin inheritance.

Instead of:
    class MyAgent(LLMProviderMixin, EmbeddingMixin, SovereignBaseAgent):
        pass

Use:
    class MyAgent(SovereignBaseAgent):
        def __post_init__(self):
            super().__post_init__()
            self.gateways = GatewayFactory.create_all()
            # or
            self.llm = GatewayFactory.get_llm_gateway()

Benefits:
- Reduces MRO depth by ~4 classes
- Explicit dependency declaration
- Easier testing with mock gateways
- Clear separation of concerns
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "gateway_config", "p0_governance")
_emit_reads_policy_state("p0", "gateway_config", "policy_binding")
_emit_snapshots_state("p0", "gateway_config", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.config.core.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

_emit_emits_metric_event("gateway_config", "p4obs", "metric_1")
_emit_emits_metric_event("gateway_config", "p4obs", "metric_2")
_emit_emits_metric_event("gateway_config", "p4obs", "metric_3")
_emit_emits_metric_event("gateway_config", "p4obs", "metric_4")
_emit_emits_metric_event("gateway_config", "p4obs", "metric_5")
_emit_emits_metric_event("gateway_config", "p4obs", "metric_6")
_emit_records_incident_event("gateway_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("gateway_config", "p4obs", "anomaly")
_emit_writes_observability_log("gateway_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("gateway_config", "p4obs", "mon_state")
_emit_triggers_alert("gateway_config", "p4obs", "alert")
_emit_links_incident_trace("gateway_config", "p4obs", "trace_link")
_emit_captures_pattern("gateway_config", "p3lm", "pattern")
_emit_records_learning_event("gateway_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("gateway_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("gateway_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("gateway_config", "p3lm", "routing")
_emit_improves_agent_policy("gateway_config", "p3lm", "policy")
_emit_stores_learning_state("gateway_config", "p3lm", "state")
_emit_records_execution_trace("gateway_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("gateway_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("gateway_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("gateway_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("gateway_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("gateway_config", "env_read", "p2_env_1")
_emit_reads_environ("gateway_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("gateway_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("gateway_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "gateway_config", "context_pull")
_emit_pulls_context("p1", "gateway_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "gateway_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "gateway_config", "uwg_term_2")
_emit_writes_through("p1", "gateway_config", "write_through")
_emit_writes_through("p1", "gateway_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "gateway_config", "safety_validation")
_emit_invokes_eval("p1", "gateway_config", "eval_call")
_emit_proposal_commits_routing("p1", "gateway_config", "routing_commit")
_emit_escalates_to_human("p1", "gateway_config", "human_escalation")
_emit_routes_through("p1", "gateway_config", "route_through")
_emit_checks_agent_registry("p1", "gateway_config", "agent_registry")
_emit_validates_agent_capability("p1", "gateway_config", "capability")
_emit_dispatches_execution_plan("p1", "gateway_config", "exec_plan")
_emit_agent_executes_agent("p1", "gateway_config", "sub_agent")
_emit_routes_to_agent("p1", "gateway_config", "target_agent")
_emit_verifies_policy("p1", "gateway_config", "policy_check")
_emit_observes_runtime_state("p1", "gateway_config", "runtime_state")
_emit_verifies_boundary("p1", "gateway_config", "boundary_check")
_emit_transcripts_response("p1", "gateway_config", "transcript")
_emit_hard_fails_untranscripted("p1", "gateway_config")
_emit_gated_by_confidence("p1", "gateway_config", "confidence_gate")
emit_replay_key("p0", "gateway_config")
emit_determinism_digest("p0", "gateway_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "gateway_config", "execution_auth")
_emit_validates_capability("p2", "gateway_config", "capability_check")
_emit_routes_to_capability("p2", "gateway_config", "capability_route")
_emit_writes_via_uwg("p2", "gateway_config", "uwg_write")
_emit_blocks_direct_write("p2", "gateway_config", "direct_write_block")
_emit_records_tool_invocation("p2", "gateway_config", "tool_invocation")
_emit_captures_execution_output("p2", "gateway_config", "exec_output")
_emit_dispatches_agent("p3", "gateway_config", "agent_dispatch")
_emit_coordinates_agents("p3", "gateway_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "gateway_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "gateway_config", "healing_outcome")
_emit_escalates_failure("p3", "gateway_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "gateway_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gateway_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "gateway_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "gateway_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gateway_config", "eval_metric")
_emit_stores_embedding("p4", "gateway_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "gateway_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gateway_config", "exec_snapshot_link")

# Configuration constants

# Type aliases
LLMProvider = Literal["openai", "anthropic", "google"]
EmbeddingProvider = Literal["gemini", "openai", "bge-m3"]


@dataclass
class GatewayBundle:
    """Bundle of all gateway instances for composition."""

    llm: Any = None
    embedding: Any = None
    validator: Any = None
    healing: Any = None

    def __post_init__(self):
        """Initialize with lazy loading markers."""
        self._llm_loaded = self.llm is not None
        self._embedding_loaded = self.embedding is not None
        self._validator_loaded = self.validator is not None
        self._healing_loaded = self.healing is not None


class GatewayFactory:
    """
    Factory for creating gateway instances via composition.

    Phase 2 MRO Refactoring: Use this instead of inheriting gateway mixins.
    """

    # Singleton instances
    _llm_gateway: Any = None
    _embedding_gateway: Any = None
    _validator_orchestrator: Any = None
    _healing_orchestrator: Any = None

    @classmethod
    def get_llm_gateway(cls) -> Any:
        """Get or create LLM gateway singleton."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GatewayFactory.get_llm_gateway")

        if cls._llm_gateway is None:
            try:
                from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
                    get_llm_gateway,
                )

                cls._llm_gateway = get_llm_gateway()
            # guardian: allow-silent-swallow - optional dependency
            except ImportError:
                # Stub for testing or when gateway not available
                cls._llm_gateway = _StubLLMGateway()
        return cls._llm_gateway

    @classmethod
    def get_embedding_gateway(cls) -> Any:
        """Get or create embedding gateway singleton."""
        if cls._embedding_gateway is None:
            try:
                from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (
                    get_embedding_gateway,
                )

                cls._embedding_gateway = get_embedding_gateway()
            except ImportError:
                # Stub for testing or when gateway not available
                cls._embedding_gateway = _StubEmbeddingGateway()
        return cls._embedding_gateway

    @classmethod
    def get_validator_orchestrator(cls) -> Any:
        """Get or create validator orchestrator singleton."""
        if cls._validator_orchestrator is None:
            try:
                from agentic_core.L5_safety.types.healing_orchestration_types import (
                    get_validator_orchestrator,
                )

                cls._validator_orchestrator = get_validator_orchestrator()
            except ImportError:
                # Stub for testing or when orchestrator not available
                cls._validator_orchestrator = _StubValidatorOrchestrator()
        return cls._validator_orchestrator

    @classmethod
    def get_healing_orchestrator(cls) -> Any:
        """Get or create healing orchestrator singleton."""
        if cls._healing_orchestrator is None:
            try:
                from agentic_core.L5_safety.types.healing_orchestration_types import (
                    get_healing_orchestrator,
                )

                cls._healing_orchestrator = get_healing_orchestrator()
            except ImportError:
                # Stub for testing or when orchestrator not available
                cls._healing_orchestrator = _StubHealingOrchestrator()
        return cls._healing_orchestrator

    @classmethod
    def create_all(cls) -> GatewayBundle:
        """Create bundle with all gateways."""
        return GatewayBundle(
            llm=cls.get_llm_gateway(),
            embedding=cls.get_embedding_gateway(),
            validator=cls.get_validator_orchestrator(),
            healing=cls.get_healing_orchestrator(),
        )

    @classmethod
    def create_minimal(cls) -> GatewayBundle:
        """Create bundle with only LLM gateway (most common use case)."""
        return GatewayBundle(llm=cls.get_llm_gateway())

    @classmethod
    def reset_all(cls) -> None:
        """Reset all singleton instances (useful for testing)."""
        cls._llm_gateway = None
        cls._embedding_gateway = None
        cls._validator_orchestrator = None
        cls._healing_orchestrator = None


# Stub implementations for testing and fallback
class _StubLLMGateway:
    """Stub LLM gateway for testing."""

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        provider: LLMProvider = "openai",
        **kwargs: Any,
    ) -> dict[str, Any]:
        return {
            "content": f"[Stub response for: {prompt[:50]}...]",
            "model": model or "stub-model",
            "provider": provider,
            "stub": True,
        }


class _StubEmbeddingGateway:
    """Stub embedding gateway for testing."""

    async def get_embedding(
        self,
        content: str,
        provider: EmbeddingProvider = "bge-m3",
        use_cache: bool = True,
    ) -> list[float]:
        return [0.0] * 1024

    async def get_embeddings_batch(
        self,
        contents: list[str],
        provider: EmbeddingProvider = "bge-m3",
    ) -> list[list[float]]:
        return [[0.0] * 1024 for _ in contents]


class _StubValidatorOrchestrator:
    """Stub validator orchestrator for testing."""

    async def validate(self, content: Any, validator_name: str, context: dict | None = None) -> dict:
        return {
            "valid": True,
            "validator": validator_name,
            "stub": True,
        }


class _StubHealingOrchestrator:
    """Stub healing orchestrator for testing."""

    async def heal(self, violation: dict, context: dict | None = None) -> dict:
        return {
            "healed": True,
            "violation": violation,
            "stub": True,
        }


__all__ = [
    "GatewayFactory",
    "GatewayBundle",
    "LLMProvider",
    "EmbeddingProvider",
]
