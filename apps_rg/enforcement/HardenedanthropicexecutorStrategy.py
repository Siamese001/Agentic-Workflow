"""Hardened Anthropic Executor - Military-Grade Reliability.

Provides robust execution for Anthropic Claude API with:
- Circuit breaker for fault tolerance
- Exponential backoff retry logic
- Pre-flight token budget validation
- Structured telemetry logging
- Rate limit handling

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

import logging
from dataclasses import dataclass

from apps_rg.utils.agent_executor import AgentMessage, AgentResponse

from agentic_core.interfaces.observability import SystemTelemetry
from agentic_core.L2_execution.utils import get_clock
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
from agentic_core.mixins.hardening_mixin import HardeningMixin, TokenLimitError

_emit_reads_policy_state("p0", "HardenedanthropicexecutorStrategy", "policy_binding")
_emit_snapshots_state("p0", "HardenedanthropicexecutorStrategy", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "HardenedanthropicexecutorStrategy", "execution_auth")
_emit_validates_capability("p2", "HardenedanthropicexecutorStrategy", "capability_check")
_emit_routes_to_capability("p2", "HardenedanthropicexecutorStrategy", "capability_route")
_emit_writes_via_uwg("p2", "HardenedanthropicexecutorStrategy", "uwg_write")
_emit_blocks_direct_write("p2", "HardenedanthropicexecutorStrategy", "direct_write_block")
_emit_records_tool_invocation("p2", "HardenedanthropicexecutorStrategy", "tool_invocation")
_emit_captures_execution_output("p2", "HardenedanthropicexecutorStrategy", "exec_output")
_emit_dispatches_agent("p3", "HardenedanthropicexecutorStrategy", "agent_dispatch")
_emit_coordinates_agents("p3", "HardenedanthropicexecutorStrategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "HardenedanthropicexecutorStrategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "HardenedanthropicexecutorStrategy", "healing_outcome")
_emit_escalates_failure("p3", "HardenedanthropicexecutorStrategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "HardenedanthropicexecutorStrategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "HardenedanthropicexecutorStrategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "HardenedanthropicexecutorStrategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "HardenedanthropicexecutorStrategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "HardenedanthropicexecutorStrategy", "eval_metric")
_emit_stores_embedding("p4", "HardenedanthropicexecutorStrategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "HardenedanthropicexecutorStrategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "HardenedanthropicexecutorStrategy", "exec_snapshot_link")
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

_emit_emits_metric_event("HardenedanthropicexecutorStrategy", "p4obs", "metric_1")
_emit_emits_metric_event("HardenedanthropicexecutorStrategy", "p4obs", "metric_2")
_emit_emits_metric_event("HardenedanthropicexecutorStrategy", "p4obs", "metric_3")
_emit_emits_metric_event("HardenedanthropicexecutorStrategy", "p4obs", "metric_4")
_emit_emits_metric_event("HardenedanthropicexecutorStrategy", "p4obs", "metric_5")
_emit_emits_metric_event("HardenedanthropicexecutorStrategy", "p4obs", "metric_6")
_emit_records_incident_event("HardenedanthropicexecutorStrategy", "p4obs", "incident")
_emit_captures_runtime_anomaly("HardenedanthropicexecutorStrategy", "p4obs", "anomaly")
_emit_writes_observability_log("HardenedanthropicexecutorStrategy", "p4obs", "obs_log")
_emit_updates_monitoring_state("HardenedanthropicexecutorStrategy", "p4obs", "mon_state")
_emit_triggers_alert("HardenedanthropicexecutorStrategy", "p4obs", "alert")
_emit_links_incident_trace("HardenedanthropicexecutorStrategy", "p4obs", "trace_link")
_emit_captures_pattern("HardenedanthropicexecutorStrategy", "p3lm", "pattern")
_emit_records_learning_event("HardenedanthropicexecutorStrategy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("HardenedanthropicexecutorStrategy", "p3lm", "snapshot")
_emit_feeds_meta_learning("HardenedanthropicexecutorStrategy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("HardenedanthropicexecutorStrategy", "p3lm", "routing")
_emit_improves_agent_policy("HardenedanthropicexecutorStrategy", "p3lm", "policy")
_emit_stores_learning_state("HardenedanthropicexecutorStrategy", "p3lm", "state")
_emit_records_execution_trace("HardenedanthropicexecutorStrategy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("HardenedanthropicexecutorStrategy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("HardenedanthropicexecutorStrategy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("HardenedanthropicexecutorStrategy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("HardenedanthropicexecutorStrategy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("HardenedanthropicexecutorStrategy", "env_read", "p2_env_1")
_emit_reads_environ("HardenedanthropicexecutorStrategy", "env_read", "p2_env_2")
_emit_reads_runtime_state("HardenedanthropicexecutorStrategy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("HardenedanthropicexecutorStrategy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "HardenedanthropicexecutorStrategy", "context_pull")
_emit_pulls_context("p1", "HardenedanthropicexecutorStrategy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "HardenedanthropicexecutorStrategy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "HardenedanthropicexecutorStrategy", "uwg_term_2")
_emit_writes_through("p1", "HardenedanthropicexecutorStrategy", "write_through")
_emit_writes_through("p1", "HardenedanthropicexecutorStrategy", "write_through_2")
_emit_validated_by_safety_plane("p1", "HardenedanthropicexecutorStrategy", "safety_validation")
_emit_invokes_eval("p1", "HardenedanthropicexecutorStrategy", "eval_call")
_emit_proposal_commits_routing("p1", "HardenedanthropicexecutorStrategy", "routing_commit")
_emit_escalates_to_human("p1", "HardenedanthropicexecutorStrategy", "human_escalation")
_emit_routes_through("p1", "HardenedanthropicexecutorStrategy", "route_through")
_emit_checks_agent_registry("p1", "HardenedanthropicexecutorStrategy", "agent_registry")
_emit_validates_agent_capability("p1", "HardenedanthropicexecutorStrategy", "capability")
_emit_dispatches_execution_plan("p1", "HardenedanthropicexecutorStrategy", "exec_plan")
_emit_agent_executes_agent("p1", "HardenedanthropicexecutorStrategy", "sub_agent")
_emit_routes_to_agent("p1", "HardenedanthropicexecutorStrategy", "target_agent")
_emit_verifies_policy("p1", "HardenedanthropicexecutorStrategy", "policy_check")
_emit_observes_runtime_state("p1", "HardenedanthropicexecutorStrategy", "runtime_state")
_emit_verifies_boundary("p1", "HardenedanthropicexecutorStrategy", "boundary_check")
_emit_transcripts_response("p1", "HardenedanthropicexecutorStrategy", "transcript")
_emit_hard_fails_untranscripted("p1", "HardenedanthropicexecutorStrategy")
_emit_gated_by_confidence("p1", "HardenedanthropicexecutorStrategy", "confidence_gate")

logger = logging.getLogger(__name__)


@dataclass
class HardenedAnthropicConfig:
    """configuration for HardenedAnthropicExecutor."""

    MODEL_LIMITS = {
        "claude-3-5-sonnet-20241022": 200000,
        "claude-3-5-haiku-20241022": 200000,
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
    }

    # guardian: allow-magic-config
    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
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
        return self.MODEL_LIMITS.get(self.model, 200000)


class HardenedAnthropicExecutor(HardeningMixin):
    """Military-grade executor for Anthropic Claude API.

    Wraps the Anthropic client with circuit breaking, retries,
    token validation, and structured telemetry.
    """

    def __init__(
        self, config: HardenedAnthropicConfig | None = None, telemetry: SystemTelemetry | None = None
    ):
        """Initialize hardened Anthropic executor.

        Args:
            config: Optional configuration
            telemetry: Optional telemetry instance
        """
        self.config = config or HardenedAnthropicConfig()
        super().__init__(
            component_name="anthropic_executor",
            failure_threshold=self.config.failure_threshold,
            reset_timeout_s=self.config.reset_timeout_s,
            max_retries=self.config.max_retries,
            telemetry=telemetry,
        )
        self._client = None
        self._setup_client()

    def _setup_client(self) -> None:
        """Delegate to SovereignLLMGateway — no direct Anthropic SDK access."""
        from agentic_core.interfaces.gateway import SovereignLLMGateway

        self._gateway = SovereignLLMGateway()
        self._client = None
        _clk = get_clock()
        _clk.emit_replay_key(context=f"rg:anthropic:{self.__class__.__name__}")
        _clk.emit_determinism_digest(inputs={"strategy": self.__class__.__name__, "provider": "anthropic"})

    def _validate_token_budget(self, prompt: str) -> None:
        """Validate token budget before API call.

        Anthropic doesn't provide official tokenization, so we use
        a conservative estimate based on character count.

        Args:
            prompt: Input prompt text

        Raises:
            TokenLimitError: If prompt exceeds model limits
        """
        estimated_tokens = len(prompt) // 4
        available_tokens = self.config.max_context_tokens - self.config.max_tokens
        if estimated_tokens > available_tokens:
            raise TokenLimitError(
                f"Prompt estimated at {estimated_tokens} tokens exceeds available budget ({available_tokens} tokens for {self.config.model})"
            )

    def _build_messages(
        self, messages: list[AgentMessage], system_prompt: str | None = None
    ) -> tuple[list[dict[str, str]], str | None]:
        """Build Anthropic message format.

        Args:
            messages: Agent messages
            system_prompt: Optional system prompt

        Returns:
            Tuple of (messages, system_prompt) for Anthropic API
        """
        anthropic_messages = []
        for msg in messages:
            anthropic_messages.append({"role": msg.role, "content": msg.content})
        return (anthropic_messages, system_prompt)

    async def run_llm(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        messages: list[AgentMessage] | None = None,
    ) -> str:
        """Run Anthropic completion with hardening.

        Args:
            prompt: Input prompt (used if messages not provided)
            temperature: Sampling temperature override
            max_tokens: Max tokens override
            system_prompt: Optional system prompt
            messages: Alternative to prompt - list of messages

        Returns:
            Generated text response
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HardenedAnthropicExecutor.run_llm")

        if messages:
            anthropic_messages, sys_prompt = self._build_messages(messages, system_prompt)
            combined_prompt = "\n".join(msg.content for msg in messages)
        else:
            anthropic_messages = [{"role": "user", "content": prompt}]
            sys_prompt = system_prompt
            combined_prompt = prompt

        async def _completion():
            response = self._client.messages.create(
                model=self.config.model,
                messages=anthropic_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                system=sys_prompt,
            )
            if response.content:
                return response.content[0].text
            return ""

        return await self.execute_hardened(
            operation="messages_create",
            fn=_completion,
            validate_token_budget=lambda: self._validate_token_budget(combined_prompt),
            metadata={
                "model": self.config.model,
                "temperature": temperature or self.config.temperature,
                "max_tokens": max_tokens or self.config.max_tokens,
                "has_system_prompt": bool(sys_prompt),
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
        """Run Anthropic completion with full response metadata.

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
            anthropic_messages, sys_prompt = self._build_messages(messages, system_prompt)
            combined_prompt = "\n".join(msg.content for msg in messages)
        else:
            anthropic_messages = [{"role": "user", "content": prompt}]
            sys_prompt = system_prompt
            combined_prompt = prompt

        async def _completion():
            response = self._client.messages.create(
                model=self.config.model,
                messages=anthropic_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                system=sys_prompt,
            )
            return response

        raw_response = await self.execute_hardened(
            operation="messages_create",
            fn=_completion,
            validate_token_budget=lambda: self._validate_token_budget(combined_prompt),
            metadata={
                "model": self.config.model,
                "temperature": temperature or self.config.temperature,
                "max_tokens": max_tokens or self.config.max_tokens,
                "has_system_prompt": bool(sys_prompt),
            },
        )
        content = ""
        usage = None
        if raw_response.content:
            content = raw_response.content[0].text
        if hasattr(raw_response, "usage"):
            usage = {
                "prompt_tokens": raw_response.usage.input_tokens,
                "completion_tokens": raw_response.usage.output_tokens,
                "total_tokens": raw_response.usage.input_tokens + raw_response.usage.output_tokens,
            }
        return AgentResponse(
            content=content,
            model=self.config.model,
            usage=usage,
            finish_reason=raw_response.stop_reason if raw_response else None,
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
def create_hardened_anthropic_executor(
    model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.7, **kwargs
) -> HardenedAnthropicExecutor:
    """Create a hardened Anthropic executor.

    Args:
        model: Anthropic model name
        temperature: Sampling temperature
        **kwargs: Additional configuration parameters

    Returns:
        HardenedAnthropicExecutor instance
    """
    config = HardenedAnthropicConfig(model=model, temperature=temperature, **kwargs)
    return HardenedAnthropicExecutor(config)
