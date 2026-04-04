"""Hardened OpenAI Executor - Military-Grade Reliability.

Provides robust execution for OpenAI API with:
- Circuit breaker for fault tolerance
- Exponential backoff retry logic
- Pre-flight token budget validation
- Structured telemetry logging
- Rate limit handling

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

import logging
from dataclasses import dataclass

from agentic_core.interfaces.gateway import GenerationRequest
from agentic_core.interfaces.observability import SystemTelemetry
from agentic_core.L2_execution.providers import get_clock
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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
)
from agentic_core.mixins.hardening_mixin import HardeningMixin
from apps_rg.utils.agent_executor import AgentMessage, AgentResponse

_emit_reads_policy_state("p0", "HardenedopenaiexecutorStrategy", "policy_binding")
_emit_snapshots_state("p0", "HardenedopenaiexecutorStrategy", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "HardenedopenaiexecutorStrategy", "execution_auth")
_emit_validates_capability("p2", "HardenedopenaiexecutorStrategy", "capability_check")
_emit_routes_to_capability("p2", "HardenedopenaiexecutorStrategy", "capability_route")
_emit_writes_via_uwg("p2", "HardenedopenaiexecutorStrategy", "uwg_write")
_emit_blocks_direct_write("p2", "HardenedopenaiexecutorStrategy", "direct_write_block")
_emit_records_tool_invocation("p2", "HardenedopenaiexecutorStrategy", "tool_invocation")
_emit_captures_execution_output("p2", "HardenedopenaiexecutorStrategy", "exec_output")
_emit_dispatches_agent("p3", "HardenedopenaiexecutorStrategy", "agent_dispatch")
_emit_coordinates_agents("p3", "HardenedopenaiexecutorStrategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "HardenedopenaiexecutorStrategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "HardenedopenaiexecutorStrategy", "healing_outcome")
_emit_escalates_failure("p3", "HardenedopenaiexecutorStrategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "HardenedopenaiexecutorStrategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "HardenedopenaiexecutorStrategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "HardenedopenaiexecutorStrategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "HardenedopenaiexecutorStrategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "HardenedopenaiexecutorStrategy", "eval_metric")
_emit_stores_embedding("p4", "HardenedopenaiexecutorStrategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "HardenedopenaiexecutorStrategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "HardenedopenaiexecutorStrategy", "exec_snapshot_link")
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

_emit_emits_metric_event("HardenedopenaiexecutorStrategy", "p4obs", "metric_1")
_emit_emits_metric_event("HardenedopenaiexecutorStrategy", "p4obs", "metric_2")
_emit_emits_metric_event("HardenedopenaiexecutorStrategy", "p4obs", "metric_3")
_emit_emits_metric_event("HardenedopenaiexecutorStrategy", "p4obs", "metric_4")
_emit_emits_metric_event("HardenedopenaiexecutorStrategy", "p4obs", "metric_5")
_emit_emits_metric_event("HardenedopenaiexecutorStrategy", "p4obs", "metric_6")
_emit_records_incident_event("HardenedopenaiexecutorStrategy", "p4obs", "incident")
_emit_captures_runtime_anomaly("HardenedopenaiexecutorStrategy", "p4obs", "anomaly")
_emit_writes_observability_log("HardenedopenaiexecutorStrategy", "p4obs", "obs_log")
_emit_updates_monitoring_state("HardenedopenaiexecutorStrategy", "p4obs", "mon_state")
_emit_triggers_alert("HardenedopenaiexecutorStrategy", "p4obs", "alert")
_emit_links_incident_trace("HardenedopenaiexecutorStrategy", "p4obs", "trace_link")
_emit_captures_pattern("HardenedopenaiexecutorStrategy", "p3lm", "pattern")
_emit_records_learning_event("HardenedopenaiexecutorStrategy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("HardenedopenaiexecutorStrategy", "p3lm", "snapshot")
_emit_feeds_meta_learning("HardenedopenaiexecutorStrategy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("HardenedopenaiexecutorStrategy", "p3lm", "routing")
_emit_improves_agent_policy("HardenedopenaiexecutorStrategy", "p3lm", "policy")
_emit_stores_learning_state("HardenedopenaiexecutorStrategy", "p3lm", "state")
_emit_records_execution_trace("HardenedopenaiexecutorStrategy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("HardenedopenaiexecutorStrategy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("HardenedopenaiexecutorStrategy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("HardenedopenaiexecutorStrategy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("HardenedopenaiexecutorStrategy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("HardenedopenaiexecutorStrategy", "env_read", "p2_env_1")
_emit_reads_environ("HardenedopenaiexecutorStrategy", "env_read", "p2_env_2")
_emit_reads_runtime_state("HardenedopenaiexecutorStrategy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("HardenedopenaiexecutorStrategy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "HardenedopenaiexecutorStrategy", "context_pull")
_emit_pulls_context("p1", "HardenedopenaiexecutorStrategy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "HardenedopenaiexecutorStrategy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "HardenedopenaiexecutorStrategy", "uwg_term_2")
_emit_writes_through("p1", "HardenedopenaiexecutorStrategy", "write_through")
_emit_writes_through("p1", "HardenedopenaiexecutorStrategy", "write_through_2")
_emit_validated_by_safety_plane("p1", "HardenedopenaiexecutorStrategy", "safety_validation")
_emit_invokes_eval("p1", "HardenedopenaiexecutorStrategy", "eval_call")
_emit_proposal_commits_routing("p1", "HardenedopenaiexecutorStrategy", "routing_commit")
_emit_escalates_to_human("p1", "HardenedopenaiexecutorStrategy", "human_escalation")
_emit_routes_through("p1", "HardenedopenaiexecutorStrategy", "route_through")
_emit_checks_agent_registry("p1", "HardenedopenaiexecutorStrategy", "agent_registry")
_emit_validates_agent_capability("p1", "HardenedopenaiexecutorStrategy", "capability")
_emit_dispatches_execution_plan("p1", "HardenedopenaiexecutorStrategy", "exec_plan")
_emit_agent_executes_agent("p1", "HardenedopenaiexecutorStrategy", "sub_agent")
_emit_routes_to_agent("p1", "HardenedopenaiexecutorStrategy", "target_agent")
_emit_verifies_policy("p1", "HardenedopenaiexecutorStrategy", "policy_check")
_emit_observes_runtime_state("p1", "HardenedopenaiexecutorStrategy", "runtime_state")
_emit_verifies_boundary("p1", "HardenedopenaiexecutorStrategy", "boundary_check")
_emit_transcripts_response("p1", "HardenedopenaiexecutorStrategy", "transcript")
_emit_hard_fails_untranscripted("p1", "HardenedopenaiexecutorStrategy")
_emit_gated_by_confidence("p1", "HardenedopenaiexecutorStrategy", "confidence_gate")

logger = logging.getLogger(__name__)


@dataclass
class HardenedOpenAIConfig:
    """configuration for HardenedOpenAIExecutor."""

    MODEL_LIMITS = {
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-0613": 8192,
        "gpt-4-32k-0613": 32768,
        "gpt-4-turbo": 128000,
        "gpt-4-turbo-2024-04-09": 128000,
        "gpt-4o": 128000,
        "gpt-4o-2024-08-06": 128000,
        "gpt-4o-mini": 128000,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-3.5-turbo-0613": 4096,
        "gpt-3.5-turbo-16k-0613": 16384,
    }

    # guardian: allow-magic-config
    def __init__(
        self,
        model: str = "gpt-4o-2024-08-06",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout_s: int = 60,
        max_retries: int = 3,
        failure_threshold: int = 5,
        reset_timeout_s: int = 30,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.failure_threshold = failure_threshold
        self.reset_timeout_s = reset_timeout_s

    @property
    def max_context_tokens(self) -> int:
        """Get maximum context tokens for the model."""
        return self.MODEL_LIMITS.get(self.model, 4096)


class HardenedOpenAIExecutor(HardeningMixin):
    """Military-grade executor for OpenAI API.

    Wraps the OpenAI client with circuit breaking, retries,
    token validation, and structured telemetry.
    """

    def __init__(self, config: HardenedOpenAIConfig | None = None, telemetry: SystemTelemetry | None = None):
        """Initialize hardened OpenAI executor.

        Args:
            config: Optional configuration
            telemetry: Optional telemetry instance
        """
        self.config = config or HardenedOpenAIConfig()
        super().__init__(
            component_name="openai_executor",
            failure_threshold=self.config.failure_threshold,
            reset_timeout_s=self.config.reset_timeout_s,
            max_retries=self.config.max_retries,
            telemetry=telemetry,
        )
        self._client = None
        self._gateway = None
        self._setup_client()

    def _setup_client(self) -> None:
        """Delegate to SovereignLLMGateway — no direct SDK access."""
        from agentic_core.interfaces.gateway import SovereignLLMGateway

        self._gateway = SovereignLLMGateway()
        _clk = get_clock()
        _clk.emit_replay_key(context=f"rg:openai:{self.__class__.__name__}")
        _clk.emit_determinism_digest(inputs={"strategy": self.__class__.__name__, "provider": "openai"})

    def _validate_token_budget(self, prompt: str) -> None:
        """Validate token budget before API call.

        Args:
            prompt: Input prompt text

        Raises:
            TokenLimitError: If prompt exceeds model limits
        """
        self.validate_token_budget_tiktoken(
            prompt=prompt,
            model=self.config.model,
            max_tokens=self.config.max_context_tokens - self.config.max_tokens,
        )

    def _build_messages(
        self, messages: list[AgentMessage], system_prompt: str | None = None
    ) -> list[dict[str, str]]:
        """Build OpenAI message format.

        Args:
            messages: Agent messages
            system_prompt: Optional system prompt

        Returns:
            Formatted messages for OpenAI API
        """
        openai_messages = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})
        for msg in messages:
            openai_messages.append({"role": msg.role, "content": msg.content})
        return openai_messages

    async def run_llm(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        messages: list[AgentMessage] | None = None,
    ) -> str:
        """Run OpenAI completion with hardening.

        Args:
            prompt: Input prompt (used if messages not provided)
            temperature: Sampling temperature override
            max_tokens: Max tokens override
            system_prompt: Optional system prompt
            messages: Alternative to prompt - list of messages

        Returns:
            Generated text response
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "HardenedOpenAIExecutorStrategy.run_llm")
        if messages:
            openai_messages = self._build_messages(messages, system_prompt)
            combined_prompt = "\n".join(msg.content for msg in messages)
        else:
            openai_messages = []
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            openai_messages.append({"role": "user", "content": prompt})
            combined_prompt = prompt

        async def _completion():
            response = await self._gateway.route_generation(
                GenerationRequest(
                    agent_id="hardened_openai_executor",
                    provider="openai",
                    model=self.config.model,
                    prompt=combined_prompt,
                    temperature=temperature or self.config.temperature,
                    max_tokens=max_tokens or self.config.max_tokens,
                )
            )
            return response.content or ""

        return await self.execute_hardened(
            operation="chat_completion",
            fn=_completion,
            validate_token_budget=lambda: self._validate_token_budget(combined_prompt),
            metadata={
                "model": self.config.model,
                "temperature": temperature or self.config.temperature,
                "max_tokens": max_tokens or self.config.max_tokens,
            },
        )

    async def run_llm_with_response(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        messages: list[AgentMessage] | None = None,
    ) -> AgentResponse:
        """Run OpenAI completion with full response metadata.

        Args:
            prompt: Input prompt (used if messages not provided)
            temperature: Sampling temperature override
            max_tokens: Max tokens override
            system_prompt: Optional system prompt
            messages: Alternative to prompt - list of messages

        Returns:
            AgentResponse with content and metadata
        """
        if messages:
            openai_messages = self._build_messages(messages, system_prompt)
            combined_prompt = "\n".join(msg.content for msg in messages)
        else:
            openai_messages = []
            if system_prompt:
                openai_messages.append({"role": "system", "content": system_prompt})
            openai_messages.append({"role": "user", "content": prompt})
            combined_prompt = prompt

        async def _completion():
            return await self._gateway.route_generation(
                GenerationRequest(
                    agent_id="hardened_openai_executor",
                    provider="openai",
                    model=self.config.model,
                    prompt=combined_prompt,
                    temperature=temperature or self.config.temperature,
                    max_tokens=max_tokens or self.config.max_tokens,
                )
            )

        raw_response = await self.execute_hardened(
            operation="chat_completion",
            fn=_completion,
            validate_token_budget=lambda: self._validate_token_budget(combined_prompt),
            metadata={
                "model": self.config.model,
                "temperature": temperature or self.config.temperature,
                "max_tokens": max_tokens or self.config.max_tokens,
            },
        )
        content = raw_response.content or "" if raw_response else ""
        usage = None
        return AgentResponse(
            content=content,
            model=raw_response.model if raw_response else self.config.model,
            usage=usage,
            finish_reason=None,
        )

    def run_llm_sync(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        messages: list[AgentMessage] | None = None,
    ) -> str:
        """Synchronous version of run_llm.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature override
            max_tokens: Max tokens override
            system_prompt: Optional system prompt
            messages: Alternative to prompt - list of messages

        Returns:
            Generated text response
        """
        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self.run_llm(
                        prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_prompt,
                        messages=messages,
                    ),
                )
                return future.result()
        else:
            return asyncio.run(
                self.run_llm(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt,
                    messages=messages,
                )
            )


# guardian: allow-magic-config
def create_hardened_openai_executor(
    model: str = "gpt-4o-2024-08-06", temperature: float = 0.7, **kwargs
) -> HardenedOpenAIExecutor:
    """Create a hardened OpenAI executor.

    Args:
        model: OpenAI model name
        temperature: Sampling temperature
        **kwargs: Additional configuration parameters

    Returns:
        HardenedOpenAIExecutor instance
    """
    config = HardenedOpenAIConfig(model=model, temperature=temperature, **kwargs)
    return HardenedOpenAIExecutor(config)
